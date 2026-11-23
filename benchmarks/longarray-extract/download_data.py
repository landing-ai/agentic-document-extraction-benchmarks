"""Download LongArray-Extract (Extend, CC BY 4.0) from Hugging Face at the pinned
revision and lay it out for run_ade.py and score.py. No data is committed to this repo.

Usage: python benchmarks/longarray-extract/download_data.py
Writes data/longarray-extract/:
  <vertical>/test-*.parquet, schemas/*.json, README.md   (as published)
  docs/<vertical>/<document_id>.pdf
  gold/<vertical>/<document_id>.json        (the ground_truth column, as published)
  gold/<vertical>/<document_id>.meta.json   (document_id, vertical, num_pages, target_field, target_count)
"""

import json
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[2]
REPO = "Extend-AI/LongArray-Extract"
REVISION = "f2ae30264ecd942fa0a9b9e787bb42e1e2577184"
META = ("document_id", "vertical", "num_pages", "target_field", "target_count")


def main() -> None:
    out = ROOT / "data" / "longarray-extract"
    snapshot_download(repo_id=REPO, repo_type="dataset", revision=REVISION, local_dir=out)
    for f in sorted(out.glob("*/test-*.parquet")):
        for row in pq.read_table(f).to_pylist():
            v, doc = row["vertical"], row["document_id"]
            (out / "docs" / v).mkdir(parents=True, exist_ok=True)
            (out / "gold" / v).mkdir(parents=True, exist_ok=True)
            (out / "docs" / v / f"{doc}.pdf").write_bytes(row["pdf"]["bytes"])
            (out / "gold" / v / f"{doc}.json").write_text(row["ground_truth"])
            (out / "gold" / v / f"{doc}.meta.json").write_text(json.dumps({k: row[k] for k in META}))
    print(f"Saved LongArray-Extract ({REVISION[:7]}) to {out}")


if __name__ == "__main__":
    main()
