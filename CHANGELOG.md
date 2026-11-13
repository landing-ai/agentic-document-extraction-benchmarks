# Changelog

A dated record of every benchmark run published in this repository. Newest first. Runs are never removed.

## 2026-11

- Repository created with scaffolding for DocVQA and ExtractBench (LlamaIndex).
- Imported the November 2025 DocVQA run from [landing-ai/ade-docvqa-benchmark](https://github.com/landing-ai/ade-docvqa-benchmark) into `benchmarks/docvqa/results/2025-11/`.

## 2025-11

- **DocVQA (validation), run 2025-11-09:** ADE DPT-2 parse + Claude Sonnet QA without image access. Exact-match accuracy 98.82% on all 5,349 questions (99.156% excluding 18 questions with questionable ground truth); derived ANLS 0.991.

## 2025-10

- **DocVQA (validation), run 2025-10-30:** earlier iteration of the same pipeline reported 98.501% exact-match accuracy. Superseded by the 2025-11 prompt; no separate results folder because the full per-question outputs were not retained.
