"""Run ADE (DPT-3 Pro parse + v2 extract) on LongArray-Extract.

Dry run by default: prints the plan, document/page counts and a cost estimate,
and calls nothing. Add --go to call the API.

For each document: v2 parse job (dpt-3-pro-20261111) -> v2 extract job
(extract-20261111) with the translated schema (data/schemas_ade/, see
schema_for_ade.py). Saves per document under runs/<run>/:
  raw/<vertical>/<doc>.parse.md         parse markdown
  raw/<vertical>/<doc>.extract.json     full extract result (values, metadata, warnings)
  predictions/<vertical>/<doc>.json     the extracted object (what score.py reads)
  log/<vertical>/<doc>.json             job ids, credits, timings, error
A document that fails is left without a prediction, so it scores 0.
Re-running skips documents that already have a prediction.

Key: VISION_AGENT_API_KEY in .env.local next to this file (never in Drive).

Usage:
  python -I run_ade.py --run 2026-11-XX_dpt-3-pro-20261111           # dry run
  python -I run_ade.py --run ... --only financial --limit 1 --go      # one-document smoke test
  python -I run_ade.py --run ... --go                                 # full run
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERTICALS = ("clinical", "financial", "legal")
PARSE_MODEL = "dpt-3-pro-20261111"
EXTRACT_MODEL = "extract-20261111"
SERVICE_TIER = "standard"
POLL_S = 5.0
JOB_TIMEOUT_S = 2 * 60 * 60
DATASET_REPO = "Extend-AI/LongArray-Extract"
DATASET_REVISION = "f2ae30264ecd942fa0a9b9e787bb42e1e2577184"  # HF commit, lastModified 2026-06-04
MAX_ATTEMPTS = 3          # per stage (parse, extract)
RETRY_BACKOFF_S = (30, 120)
RETRY_POLICY = ("retry on failure only: a parse or extract job that errors, fails or times out is resubmitted, "
                "up to 3 attempts per stage (waits 30 s, then 120 s). A job that completes is never re-run, whatever "
                "its output. Every attempt is logged. A document that still fails has no prediction and scores 0")
# Planning rates from earlier runs (LongExtractBench, Nov 18): ~9.9 credits/page parse+extract.
EST_CREDITS_PER_PAGE = 9.9


def load_env() -> None:
    f = HERE / ".env.local"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def documents(data: Path, only: str | None, limit: int | None) -> list[dict]:
    out = []
    for v in VERTICALS:
        if only and v != only:
            continue
        metas = [json.loads(p.read_text()) for p in sorted((data / "gold" / v).glob("*.meta.json"))]
        metas.sort(key=lambda m: m["num_pages"])
        out += metas[:limit] if limit else metas
    return out


def wait(get, job_id: str) -> dict:
    deadline = time.monotonic() + JOB_TIMEOUT_S
    while True:
        job = get(job_id, timeout=60.0)
        status = getattr(getattr(job, "status", None), "value", getattr(job, "status", None))
        if status == "completed":
            raw = getattr(job, "raw", None) or {}
            payload = raw.get("result") if raw.get("result") is not None else raw.get("data")
            if not isinstance(payload, dict):
                raise RuntimeError(f"{job_id} completed without an inline result")
            return payload
        if status in ("failed", "cancelled"):
            err = getattr(job, "error", None)
            raise RuntimeError(f"{job_id} {status}: {getattr(err, 'code', '')} {getattr(err, 'message', '')}")
        if time.monotonic() > deadline:
            raise TimeoutError(f"{job_id} still {status} after {JOB_TIMEOUT_S}s")
        time.sleep(POLL_S)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(a, data: Path, docs: list[dict]) -> dict:
    import landingai_ade
    import importlib.metadata as md
    pkgs = {p: md.version(p) for p in ("landingai-ade", "numpy", "scipy", "rapidfuzz")}
    return {
        "benchmark": "LongArray-Extract",
        "dataset": {"repo": DATASET_REPO, "revision": DATASET_REVISION,
                    "parquet_sha256": {str(f.relative_to(data)): sha256(f) for f in sorted(data.glob("*/test-*.parquet"))}},
        "documents": len(docs), "pages": sum(d["num_pages"] for d in docs),
        "system": {"parse_api": "ADE v2 parse jobs", "parse_model": PARSE_MODEL,
                   "extract_api": "ADE v2 extract jobs", "extract_model": EXTRACT_MODEL,
                   "service_tier": SERVICE_TIER, "extract_options": "defaults (strict=false, grounding=true)",
                   "endpoint": "https://api.ade.landing.ai (production)", "sdk": f"landingai-ade {landingai_ade.__version__}"},
        "procedure": {"workers": a.workers, "job_timeout_s": JOB_TIMEOUT_S, "poll_interval_s": POLL_S,
                      "retries": RETRY_POLICY, "post_processing": "none; the extract result's `extraction` object is the prediction",
                      "schemas": "published schemas with Extend-only keys translated (schema_for_ade.py, METHOD.md)"},
        "schemas_sha256": {str(f.relative_to(data)): sha256(f) for f in sorted(list((data / "schemas").glob("*.json")) + list((data / "schemas_ade").glob("*.json")))},
        "code_sha256": {f.name: sha256(f) for f in sorted(HERE.glob("*.py")) if f.name in ("run_ade.py", "schema_for_ade.py", "score.py")},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "packages": pkgs},
        "command": " ".join(["python", "-I"] + sys.argv),
        "started_at": now(),
    }


def credits(meta: dict | None) -> float | None:
    b = (meta or {}).get("billing") or {}
    c = b.get("total_credits")
    return float(c) if isinstance(c, (int, float)) else None


def attempt_stage(stage: str, submit, get, log: dict) -> dict:
    """Submit a job and wait for it; resubmit only if the job errors, fails or times out."""
    attempts = log.setdefault(f"{stage}_attempts", [])
    for n in range(1, MAX_ATTEMPTS + 1):
        rec: dict = {"attempt": n, "started_at": now()}
        attempts.append(rec)
        try:
            job = submit()
            rec["job_id"] = job.job_id
            payload = wait(get, job.job_id)
            rec["status"] = "completed"
            rec["finished_at"] = now()
            return payload
        except Exception as e:  # noqa: BLE001
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {e}"[:500]
            rec["finished_at"] = now()
            if n == MAX_ATTEMPTS:
                raise
            time.sleep(RETRY_BACKOFF_S[min(n - 1, len(RETRY_BACKOFF_S) - 1)])
    raise AssertionError("unreachable")


def run_one(client, data: Path, run_dir: Path, m: dict) -> dict:
    v, doc = m["vertical"], m["document_id"]
    pred_f = run_dir / "predictions" / v / f"{doc}.json"
    if pred_f.exists():
        return {"document_id": doc, "skipped": True}
    for sub in ("raw", "predictions", "log"):
        (run_dir / sub / v).mkdir(parents=True, exist_ok=True)
    log: dict = {"document_id": doc, "vertical": v, "num_pages": m["num_pages"],
                 "requested_parse_model": PARSE_MODEL, "requested_extract_model": EXTRACT_MODEL,
                 "service_tier": SERVICE_TIER, "started_at": now()}
    t0 = time.perf_counter()
    try:
        parse = attempt_stage(
            "parse",
            lambda: client.v2.parse_jobs.create(document=data / "docs" / v / f"{doc}.pdf", model=PARSE_MODEL,
                                                service_tier=SERVICE_TIER, timeout=300.0),
            client.v2.parse_jobs.get, log)
        md = parse.get("markdown") or ""
        (run_dir / "raw" / v / f"{doc}.parse.md").write_text(md)
        with gzip.open(run_dir / "raw" / v / f"{doc}.parse.json.gz", "wt") as f:
            json.dump(parse, f, default=str)
        pmeta = parse.get("metadata") or {}
        log["parse_model_version"] = pmeta.get("model_version")
        log["parse_page_count"] = pmeta.get("page_count")
        log["parse_failed_pages"] = pmeta.get("failed_pages")
        log["parse_credits"] = credits(pmeta)
        log["parse_s"] = time.perf_counter() - t0

        schema = json.loads((data / "schemas_ade" / f"{v}.json").read_text())
        t1 = time.perf_counter()
        ext = attempt_stage(
            "extract",
            lambda: client.v2.extract_jobs.create(schema=schema, markdown=md, model=EXTRACT_MODEL,
                                                  service_tier=SERVICE_TIER, timeout=300.0),
            client.v2.extract_jobs.get, log)
        (run_dir / "raw" / v / f"{doc}.extract.json").write_text(json.dumps(ext, default=str))
        log["extract_model_version"] = (ext.get("metadata") or {}).get("model_version")
        log["extract_credits"] = credits(ext.get("metadata"))
        log["extract_s"] = time.perf_counter() - t1
        log["schema_violation_error"] = ext.get("schema_violation_error")
        log["warnings"] = ext.get("warnings")
        pred_f.write_text(json.dumps(ext.get("extraction") or {}, default=str))
        log["status"] = "ok"
    except Exception as e:  # noqa: BLE001
        log["status"] = "failed"
        log["error"] = f"{type(e).__name__}: {e}"[:500]
    log["total_s"] = time.perf_counter() - t0
    log["finished_at"] = now()
    (run_dir / "log" / v / f"{doc}.json").write_text(json.dumps(log, indent=2))
    return log


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run folder name, e.g. 2026-11-24_dpt-3-pro-20261111")
    ap.add_argument("--data", type=Path, default=HERE / "data")
    ap.add_argument("--only", choices=VERTICALS)
    ap.add_argument("--limit", type=int, help="smallest N documents per vertical")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--go", action="store_true", help="actually call the API")
    ap.add_argument("--resume", action="store_true", help="finish an interrupted run in the same folder")
    a = ap.parse_args()

    docs = documents(a.data, a.only, a.limit)
    pages = sum(d["num_pages"] for d in docs)
    print(f"{len(docs)} documents, {pages:,} pages; parse {PARSE_MODEL}, extract {EXTRACT_MODEL}, tier {SERVICE_TIER}")
    print(f"planning estimate: ~{pages * EST_CREDITS_PER_PAGE:,.0f} credits (~${pages * EST_CREDITS_PER_PAGE * 0.01:,.0f} at list price)")
    if not a.go:
        print("dry run: nothing called. Add --go to run.")
        return
    if not (a.data / "schemas_ade").exists():
        raise SystemExit("run schema_for_ade.py first")
    load_env()
    key = os.environ.get("VISION_AGENT_API_KEY")
    if not key:
        raise SystemExit("VISION_AGENT_API_KEY not set (put it in .env.local)")
    from landingai_ade import LandingAIADE

    client = LandingAIADE(apikey=key)
    run_dir = HERE / "runs" / a.run
    if (run_dir / "manifest.json").exists() and not a.resume:
        raise SystemExit(f"{run_dir} already has a run; use a new --run name (or --resume to finish it)")
    run_dir.mkdir(parents=True, exist_ok=True)
    man = json.loads((run_dir / "manifest.json").read_text()) if a.resume else manifest(a, a.data, docs)
    if a.resume:
        man.setdefault("resumed_at", []).append(now())
    (run_dir / "manifest.json").write_text(json.dumps(man, indent=2))
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futs = {pool.submit(run_one, client, a.data, run_dir, d): d for d in docs}
        for f in as_completed(futs):
            r = f.result()
            print(r.get("document_id"), r.get("status", "skipped"), r.get("error", ""), flush=True)
    logs = [json.loads(p.read_text()) for p in sorted((run_dir / "log").glob("*/*.json"))]
    man["finished_at"] = now()
    man["outcome"] = {
        "completed": sum(x.get("status") == "ok" for x in logs),
        "failed": [x["document_id"] for x in logs if x.get("status") != "ok"],
        "parse_model_versions": sorted({str(x.get("parse_model_version")) for x in logs}),
        "extract_model_versions": sorted({str(x.get("extract_model_version")) for x in logs}),
        "documents_with_retries": [x["document_id"] for x in logs
                                   if len(x.get("parse_attempts", [])) > 1 or len(x.get("extract_attempts", [])) > 1],
        "credits": round(sum((x.get("parse_credits") or 0) + (x.get("extract_credits") or 0) for x in logs), 1),
    }
    (run_dir / "manifest.json").write_text(json.dumps(man, indent=2))
    print(json.dumps(man["outcome"], indent=2))


if __name__ == "__main__":
    main()
