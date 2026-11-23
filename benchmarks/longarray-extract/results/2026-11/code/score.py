"""Score LongArray-Extract predictions with Extend's canonical method.

The scoring functions (_norm, _cell_match, _score_array, score_document, FUZZY)
are copied verbatim from the "Reference implementation" in the dataset README
(https://huggingface.co/datasets/Extend-AI/LongArray-Extract, CC BY 4.0).
Only the driver around them is ours.

Predictions: <pred_dir>/<vertical>/<document_id>.json (the extracted object).
A missing or unreadable prediction scores 0 for that document, matching Extend's
results page ("failed, timed-out, or unscoreable runs count as 0%").

Usage: python -I score.py <pred_dir> [--data data] [--out <dir>]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from rapidfuzz import fuzz
from scipy.optimize import linear_sum_assignment

VERTICALS = ("clinical", "financial", "legal")

# ---------------------------------------------------------------- reference implementation (verbatim)
_PUNCT, _WS = re.compile(r"[^\w\s]", re.U), re.compile(r"\s+", re.U)
FUZZY = {"financial": {"description": 0.95}, "legal": {"court": 0.85}, "clinical": {}}

def _norm(s):
    return _WS.sub(" ", _PUNCT.sub(" ", s)).strip().lower()

def _cell_match(a, b, field, fuzzy):
    if field in fuzzy and isinstance(a, str) and isinstance(b, str):
        na, nb = _norm(a), _norm(b)
        return na == nb or (bool(na) and bool(nb)
                            and fuzz.ratio(na, nb) >= fuzzy[field] * 100.0)
    return a == b

def _score_array(pred, exp, sub_fields, fuzzy):
    total = len(exp) * len(sub_fields)
    if not exp or not sub_fields:        # nothing to score (or scalar array)
        return 0, total
    if not pred:
        return 0, total
    cost = np.empty((len(pred), len(exp)))
    for i, p in enumerate(pred):
        p = p if isinstance(p, dict) else {}
        for j, e in enumerate(exp):
            e = e if isinstance(e, dict) else {}
            cost[i, j] = sum(not _cell_match(p.get(sf), e.get(sf), sf, fuzzy)
                             for sf in sub_fields)
    correct = 0
    for i, j in zip(*linear_sum_assignment(cost)):
        p = pred[i] if isinstance(pred[i], dict) else {}
        e = exp[j] if isinstance(exp[j], dict) else {}
        correct += sum(_cell_match(p.get(sf), e.get(sf), sf, fuzzy) for sf in sub_fields)
    return correct, total

def score_document(pred, gold, schema, fuzzy):
    """Return (correct_data_points, total_data_points) for one document."""
    if isinstance(pred, dict) and set(pred) == {"value"}:
        pred = pred["value"]
    props = schema.get("properties", {})
    correct = total = 0
    for f in sorted(set(gold) | set(pred)):
        fs = props.get(f, {})
        if fs.get("type") == "array" or isinstance(gold.get(f), list):
            sub = list(fs.get("items", {}).get("properties", {}).keys())
            c, t = _score_array(pred.get(f) or [], gold.get(f) or [], sub, fuzzy)
        else:
            t, c = 1, int(_cell_match(pred.get(f), gold.get(f), f, fuzzy))
        correct += c
        total += t
    return correct, total
# ---------------------------------------------------------------- end reference implementation


def load_docs(data: Path, vertical: str) -> list[dict]:
    metas = sorted((data / "gold" / vertical).glob("*.meta.json"))
    return [json.loads(m.read_text()) for m in metas]


def score_run(pred_dir: Path, data: Path) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    for v in VERTICALS:
        schema = json.loads((data / "schemas" / f"{v}.json").read_text())
        for meta in load_docs(data, v):
            doc = meta["document_id"]
            gold = json.loads((data / "gold" / v / f"{doc}.json").read_text())
            pf = pred_dir / v / f"{doc}.json"
            status = "ok"
            try:
                pred = json.loads(pf.read_text())
                if not isinstance(pred, dict):
                    raise ValueError("prediction is not a JSON object")
            except FileNotFoundError:
                pred, status = {}, "missing"
            except Exception:  # noqa: BLE001
                pred, status = {}, "unreadable"
            c, t = score_document(pred, gold, schema, FUZZY[v])
            body = pred["value"] if isinstance(pred, dict) and set(pred) == {"value"} else pred
            arr = body.get(meta["target_field"]) if isinstance(body, dict) else None
            rows.append({
                "vertical": v, "document_id": doc, "num_pages": meta["num_pages"],
                "target_count": meta["target_count"],
                "predicted_len": len(arr) if isinstance(arr, list) else 0,
                "status": status, "correct": c, "total": t,
                "accuracy": c / t if t else 0.0,
            })
    summary = {}
    for name, group in [("all", rows)] + [(v, [r for r in rows if r["vertical"] == v]) for v in VERTICALS]:
        n = len(group)
        summary[name] = {
            "documents": n,
            "completed": sum(r["status"] == "ok" for r in group),
            "macro_accuracy": sum(r["accuracy"] for r in group) / n if n else 0.0,
            "micro_accuracy": (sum(r["correct"] for r in group) / sum(r["total"] for r in group))
            if group and sum(r["total"] for r in group) else 0.0,
            "rows_expected": sum(r["target_count"] for r in group),
            "rows_predicted": sum(r["predicted_len"] for r in group),
        }
    return rows, summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pred_dir", type=Path)
    ap.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "data")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    rows, summary = score_run(a.pred_dir, a.data)
    out = a.out or a.pred_dir.parent
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "per_document.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    for k, s in summary.items():
        print(f"{k:9} docs {s['documents']:2}  completed {s['completed']:2}  "
              f"macro {s['macro_accuracy']:.2%}  micro {s['micro_accuracy']:.2%}  "
              f"rows {s['rows_predicted']:,}/{s['rows_expected']:,}")


if __name__ == "__main__":
    sys.exit(main())
