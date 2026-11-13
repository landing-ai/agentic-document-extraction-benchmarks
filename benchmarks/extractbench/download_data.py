"""Download ExtractBench (LlamaIndex, arXiv 2607.29677) from Hugging Face. No data is committed to this repo.

Usage: python benchmarks/extractbench/download_data.py
"""

from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    out = ROOT / "data" / "extractbench"
    snapshot_download(repo_id="llamaindex/ExtractBench", repo_type="dataset", local_dir=out)
    print(f"Saved ExtractBench to {out}")


if __name__ == "__main__":
    main()
