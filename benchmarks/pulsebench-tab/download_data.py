"""Download PulseBench-Tab (Pulse, CC BY-NC-ND 4.0) at the pinned revision, plus Pulse's T-LAG
scorer at the pinned commit. Nothing from the benchmark is committed to this repo.

Usage: python benchmarks/pulsebench-tab/download_data.py
Writes data/pulsebench-tab/:
  images/<sample_id>.png, ground_truth/<sample_id>.html   (as published)
  manifest.json   ({sample_id: language})
  tlag_scorer.py  (Pulse's scorer, unmodified, from the pinned commit)
  REVISION
"""
import json
import urllib.request
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[2]
DATASET = "pulse-ai/PulseBench-Tab"
REVISION = "e0e1fd5c4b3f7daa0c6afed88177ed9242e6593d"
SCORER_COMMIT = "b57992cba5b7a36fba6c1351aafc011353f6d329"
SCORER_URL = f"https://raw.githubusercontent.com/Pulse-Software-Corp/PulseBench-Tab/{SCORER_COMMIT}/tlag_scorer.py"


def main() -> None:
    out = ROOT / "data" / "pulsebench-tab"
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "ground_truth").mkdir(parents=True, exist_ok=True)
    ds = load_dataset(DATASET, split="train", revision=REVISION)
    langs = {}
    for s in ds:
        sid = s["sample_id"]
        s["image"].save(out / "images" / f"{sid}.png", format="PNG")
        (out / "ground_truth" / f"{sid}.html").write_text(s["ground_truth_html"], encoding="utf-8")
        langs[sid] = s["language"]
    (out / "manifest.json").write_text(json.dumps(langs, indent=0))
    with urllib.request.urlopen(SCORER_URL) as r:
        (out / "tlag_scorer.py").write_bytes(r.read())
    (out / "REVISION").write_text(f"dataset {REVISION}\nscorer {SCORER_COMMIT}\n")
    print(f"{len(langs)} samples -> {out}")


if __name__ == "__main__":
    main()
