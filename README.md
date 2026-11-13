# Agentic Document Extraction Benchmarks

**Reproducible results for LandingAI [Agentic Document Extraction (ADE)](https://landing.ai/agentic-document-extraction) on public document AI benchmarks published by others.**

This repository reports how ADE performs on third-party benchmarks for AI document processing (also called intelligent document processing, or IDP). These benchmarks cover document question answering and structured field extraction. Every number here was produced by LandingAI using the code, configuration, and ADE version recorded alongside it. Each run is dated and kept, so you can see how results change over time.

> **Scope:** This is a single-vendor results repository, not an independent leaderboard. Where we show other systems' scores, they come from the benchmark authors' published leaderboard or paper, with a source link and retrieval date. We did not run those systems ourselves.

## Latest results

| Benchmark | Task | Metric | ADE score | ADE version | Run date | Details |
|---|---|---|---|---|---|---|
| [DocVQA](benchmarks/docvqa/) | Document visual question answering | ANLS | _pending_ | _pending_ | _pending_ | [README](benchmarks/docvqa/README.md) |
| [ExtractBench](benchmarks/extractbench/) | Structured field extraction | Field-level F1 | _pending_ | _pending_ | _pending_ | [README](benchmarks/extractbench/README.md) |

The machine-readable version of this table is in [`results.csv`](results.csv). The full history of runs is in [`CHANGELOG.md`](CHANGELOG.md).

## How to read these results

- **LandingAI results** were run by us and can be reproduced with the code in this repo. Per-sample predictions are published next to every summary score.
- **Published results for reference**, in each benchmark's README, are copied from the cited source as reported there. Differences in setup, such as data split, prompting, or post-processing, may limit direct comparison.
- We publish every run, including runs where scores went down.

See [`METHODOLOGY.md`](METHODOLOGY.md) for how runs are configured, which metrics are used, and what counts as a reportable result.

## Repository layout

```
.
├── README.md            # this page: what the repo is and latest results
├── METHODOLOGY.md       # ADE version/config, metrics, how runs are done
├── results.csv          # machine-readable summary across benchmarks
├── CHANGELOG.md         # dated record of every run
├── CITATION.cff         # how to cite this repository
├── harness/             # shared runner and metric code
└── benchmarks/
    ├── docvqa/
    │   ├── README.md        # benchmark description, results, reproduction steps
    │   ├── config.yaml
    │   ├── download_data.py # pulls from the official source; no data is committed
    │   └── results/YYYY-MM/ # summary.json + predictions.jsonl per run
    └── extractbench/
        └── ...
```

## Reproducing a result

```bash
git clone https://github.com/landing-ai/agentic-document-extraction-benchmarks.git
cd agentic-document-extraction-benchmarks
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export VISION_AGENT_API_KEY=...   # your LandingAI API key, never commit it

python benchmarks/docvqa/download_data.py
python -m harness.run --benchmark docvqa
```

Each benchmark's README lists its exact reproduction steps and the config used for the published run.

## Citing

If you reference these results, please cite this repository (see [`CITATION.cff`](CITATION.cff)) and the original benchmark papers linked in each benchmark's README.

## License

Code and results in this repository are released under the [Apache License 2.0](LICENSE). The benchmark datasets are **not** redistributed here and remain under their original licenses; the download scripts fetch them from the official sources.
