"""Download DocVQA from a public mirror of the official release. No data is committed to this repo.

Usage: python benchmarks/docvqa/download_data.py [--split validation]
"""

import argparse
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="validation")
    args = parser.parse_args()
    out = ROOT / "data" / "docvqa"
    out.mkdir(parents=True, exist_ok=True)
    # TODO: confirm this mirror matches the official release before publishing results.
    ds = load_dataset("lmms-lab/DocVQA", "DocVQA", split=args.split)
    ds.save_to_disk(str(out / args.split))
    print(f"Saved {len(ds)} samples to {out / args.split}")


if __name__ == "__main__":
    main()
