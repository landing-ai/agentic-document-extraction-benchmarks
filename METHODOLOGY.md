# Methodology

This document describes how LandingAI runs Agentic Document Extraction (ADE) on third-party benchmarks and what we commit to when we publish a result.

## Principles

1. **Third-party benchmarks only.** We report on datasets and metrics defined by others. We do not modify the evaluation data or the official metric definitions.
2. **Every run is published.** Each run gets a dated folder under `benchmarks/<name>/results/YYYY-MM/` and an entry in `CHANGELOG.md`. Earlier runs are never overwritten or deleted, including runs where scores dropped.
3. **Reproducible by default.** Each run records the ADE model/version, API endpoint, config file, harness commit, and dataset split, so anyone with an API key can re-run it.
4. **Per-sample predictions are public.** `predictions.jsonl` contains the model output for every evaluated sample, so scores can be independently re-computed.
5. **Clear separation from others' numbers.** Scores for other systems appear only in "Published results for reference" tables, copied from the cited source with a link and retrieval date. We do not run competitor systems.

## What each run records

`summary.json` in every results folder contains:

| Field | Description |
|---|---|
| `benchmark` | Benchmark name, matching the directory name |
| `split` | Dataset split evaluated (e.g. `validation`) |
| `num_samples` | Number of samples scored |
| `metric` | Primary metric name (e.g. `anls`, `field_f1`) |
| `score` | Primary metric value |
| `secondary_metrics` | Any additional metrics |
| `ade_model` | ADE model / version string returned by the API |
| `ade_endpoint` | API endpoint used |
| `config` | Path to the config file used |
| `harness_commit` | Git commit of this repo at run time |
| `run_date` | ISO 8601 date of the run |
| `notes` | Any deviations, failures, or caveats |

## Metrics

| Metric | Used by | Definition |
|---|---|---|
| ANLS | DocVQA | Average Normalized Levenshtein Similarity, threshold τ = 0.5, max over ground-truth answers, as defined by the DocVQA authors |
| Value F1, Grounding F1 | ExtractBench (LlamaIndex) | Per-document value F1 and IoU-based evidence F1, computed with the benchmark's official evaluator (`llama-extract-bench`) |

Metric implementations live in `harness/metrics.py`. Where a benchmark provides an official scorer, we use it or verify that our implementation matches it.

## Failures and exclusions

- API errors or timeouts are retried up to the limit in the config. Samples that still fail are **scored as incorrect**, not dropped, and the count is recorded in `notes`.
- No samples are excluded after seeing results.

## Versioning

Results folders are named by year and month (`YYYY-MM`). If more than one run is published in a month, use a suffix (`2026-11b`). The top-level `README.md` and `results.csv` always show the latest run per benchmark.
