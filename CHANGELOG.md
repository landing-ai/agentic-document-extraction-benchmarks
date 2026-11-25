# Changelog

A dated record of every benchmark run published in this repository. Newest first. Runs are never removed.

## 2026-11

- **API key variable, 2026-11-25:** reproduction code and instructions now read the LandingAI API key from `ADE_API_KEY`, replacing `VISION_AGENT_API_KEY` (`longarray-extract/results/2026-11/code/run_ade.py`, `pulsebench-tab/results/2026-11/code/landingai.py`). No change to any result; code checksums in the two manifests updated.
- **PulseBench-Tab (Pulse, all 1,820 samples), run 2026-11-24, submitted to the benchmark repository ([Pulse-Software-Corp/PulseBench-Tab#5](https://github.com/Pulse-Software-Corp/PulseBench-Tab/pull/5)):** ADE Parse dpt-3-pro-20261111, Parse Jobs, standard tier, default options. T-LAG 78.6 on the 1,532 samples with a table (the benchmark's published mode), coverage 84.2%, 66.2 with missing samples counted as 0. Also published: a revised diagnostic score of 87.1 with answer-key writing conventions ignored on both sides (`revised_score.py`; not the benchmark score). All outputs in `benchmarks/pulsebench-tab/results/2026-11/`.
- **LongArray-Extract (Extend, 45 docs), run 2026-11-23:** ADE Parse dpt-3-pro-20261111 + Extract extract-20261111, public production API, standard tier. Mean per-document accuracy 99.04% (micro 99.02%; clinical 99.24%, financial 99.14%, legal 98.43%), 45/45 completed, no retries, 15,083.7 credits ($0.070 per page). Scored with Extend's reference scorer, unchanged. Predictions, run record, logs and code published in `benchmarks/longarray-extract/results/2026-11/`.
- **ExtractBench (LlamaIndex, full 370 docs), run 2026-11-20, official submission ([run-llama/ExtractBench#172](https://github.com/run-llama/ExtractBench/pull/172)):** ADE Parse dpt-3-pro-20261111 + Extract extract-20261111, public production API, standard tier. Value F1 94.11 (short 94.88, medium 93.26, long 88.65), word grounding F1 66.14, page grounding F1 83.48, $0.0474 per page, 1 failed document, none over 30 minutes. All outputs and evaluator files published in `benchmarks/extractbench/results/2026-11/`. These files replace the preliminary 2026-11-12 import below; its summary numbers remain recorded here.
- Repository created with scaffolding for DocVQA and ExtractBench (LlamaIndex).
- **ExtractBench (LlamaIndex, full 370 docs), run 2026-11-12, preliminary (internal staging run; files superseded by the 2026-11-20 run):** extract-20261111 value F1 94.02 vs. 91.62 for extract-20260903. Grounding F1 not yet reported; re-run with latency improvements pending.
- Imported the November 2025 DocVQA run from [landing-ai/ade-docvqa-benchmark](https://github.com/landing-ai/ade-docvqa-benchmark) into `benchmarks/docvqa/results/2025-11/`.

## 2025-11

- **DocVQA (validation), run 2025-11-09:** ADE DPT-2 parse + Claude Sonnet QA without image access. Exact-match accuracy 98.82% on all 5,349 questions (99.156% excluding 18 questions with questionable ground truth); derived ANLS 0.991.

## 2025-10

- **DocVQA (validation), run 2025-10-30:** earlier iteration of the same pipeline reported 98.501% exact-match accuracy. Superseded by the 2025-11 prompt; no separate results folder because the full per-question outputs were not retained.
