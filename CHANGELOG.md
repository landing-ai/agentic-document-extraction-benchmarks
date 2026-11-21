# Changelog

A dated record of every benchmark run published in this repository. Newest first. Runs are never removed.

## 2026-11

- **ExtractBench (LlamaIndex, full 370 docs), run 2026-11-20, official submission ([run-llama/ExtractBench#172](https://github.com/run-llama/ExtractBench/pull/172)):** ADE Parse dpt-3-pro-20261111 + Extract extract-20261111, public production API, standard tier. Value F1 94.11 (short 94.88, medium 93.26, long 88.65), word grounding F1 66.14, page grounding F1 83.48, $0.0474 per page, 1 failed document, none over 30 minutes. All outputs and evaluator files published in `benchmarks/extractbench/results/2026-11/`. These files replace the preliminary 2026-11-12 import below; its summary numbers remain recorded here.
- Repository created with scaffolding for DocVQA and ExtractBench (LlamaIndex).
- **ExtractBench (LlamaIndex, full 370 docs), run 2026-11-12, preliminary (internal staging run; files superseded by the 2026-11-20 run):** extract-20261111 value F1 94.02 vs. 91.62 for extract-20260903. Grounding F1 not yet reported; re-run with latency improvements pending.
- Imported the November 2025 DocVQA run from [landing-ai/ade-docvqa-benchmark](https://github.com/landing-ai/ade-docvqa-benchmark) into `benchmarks/docvqa/results/2025-11/`.

## 2025-11

- **DocVQA (validation), run 2025-11-09:** ADE DPT-2 parse + Claude Sonnet QA without image access. Exact-match accuracy 98.82% on all 5,349 questions (99.156% excluding 18 questions with questionable ground truth); derived ANLS 0.991.

## 2025-10

- **DocVQA (validation), run 2025-10-30:** earlier iteration of the same pipeline reported 98.501% exact-match accuracy. Superseded by the 2025-11 prompt; no separate results folder because the full per-question outputs were not retained.
