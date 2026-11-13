# ExtractBench run: November 2026 (preliminary)

Full ExtractBench (370 documents) run on 2026-11-12 with the official ExtractBench harness. Two ADE Extract versions are compared: the new `extract-20261111` and the previous `extract-20260903`. These results were imported from an internal results summary and were not re-run in this repository.

> **Preliminary.** `extract-20261111` was still being tuned for latency when these numbers were produced. A re-run is pending before submission to the [official leaderboard](https://github.com/run-llama/ExtractBench#submitting-results).

## Value F1 (%)

| Split | Docs | extract-20261111 | extract-20260903 |
|---|---:|---:|---:|
| Short | 252 | 94.66 | 93.42 |
| Medium | 98 | 93.43 | 89.74 |
| Long | 20 | 88.99 | 78.26 |
| **Overall** | **370** | **94.02** | **91.62** |

## Latency per document, p50 / p90 (seconds)

| Split | extract-20261111 | extract-20260903 |
|---|---:|---:|
| Short | 107 / 205 | 33 / 120 |
| Medium | 201 / 562 | 74 / 392 |
| Long | 424 / 1,248 | 530 / 953 |
| Overall | 124 / 362 | 38 / 382 |

## LLM cost per document (USD)

| Split | extract-20261111 | extract-20260903 |
|---|---:|---:|
| Short | $0.019 | $0.12 |
| Medium | $0.062 | $1.08 |
| Long | $0.183 | $4.98 |
| Overall | $0.039 | $0.637 |

This is LLM cost per document. It is not the leaderboard's cost per page at public list prices, so the two can't be compared directly.

## Configuration

- `extract-20261111` ran with grounding enabled. The grounding setting for `extract-20260903` was not stated.
- Parse model underneath Extract: **not recorded**.
- Harness version: **not recorded**.

## Missing before this run can be final

- Grounding F1 (word level and page level), which the leaderboard requires
- Precision and recall per split, and % of documents with perfect scores
- Per-document outputs and evaluation reports
- Parse model, harness version, and maximum latency (to confirm no document exceeded the official 30-minute limit)
