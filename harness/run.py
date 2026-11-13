"""Benchmark runner entry point.

Usage:
    python -m harness.run --benchmark docvqa [--limit 50]

Reads benchmarks/<name>/config.yaml, runs ADE on each sample, scores it, and writes
summary.json + predictions.jsonl to benchmarks/<name>/results/<YYYY-MM>/.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--limit", type=int, default=None, help="Score only the first N samples (for smoke tests; do not publish)")
    args = parser.parse_args()

    bench_dir = ROOT / "benchmarks" / args.benchmark
    config = yaml.safe_load((bench_dir / "config.yaml").read_text())

    # TODO: implement per-benchmark loading, ADE calls, and scoring.
    # Each benchmark should expose load_samples(config) and score(sample, prediction).
    raise NotImplementedError(
        f"Runner for '{args.benchmark}' is not implemented yet. Config loaded: {config.get('name')}"
    )

    run_dir = bench_dir / "results" / dt.date.today().strftime("%Y-%m")  # noqa: unreachable
    run_dir.mkdir(parents=True, exist_ok=True)
    summary = {"benchmark": args.benchmark, "harness_commit": git_commit(), "run_date": dt.date.today().isoformat()}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
