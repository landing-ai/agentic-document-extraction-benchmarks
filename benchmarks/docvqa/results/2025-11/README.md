# DocVQA run: November 2025

Imported from [landing-ai/ade-docvqa-benchmark](https://github.com/landing-ai/ade-docvqa-benchmark) at commit [`9d9bdff`](https://github.com/landing-ai/ade-docvqa-benchmark/tree/9d9bdff3b941a54f0961d428adba1bbeb261f378). The final result was committed on 2025-11-09. It was not re-run in this repository.

## Setup

- **Parse:** each of the 1,286 validation images was parsed once with ADE DPT-2 (`dpt-2-latest`).
- **Answer:** Claude Sonnet answered each of the 5,349 questions using **only** the parsed output (markdown with chunk types, page, position, and bounding boxes). It never saw the image. Prompt: [`prompt.md`](prompt.md). Temperature 0.0, max tokens 4096.
- **Score:** case-insensitive exact match against any ground-truth answer.

## Results

| Measure | Value |
|---|---|
| Exact-match accuracy, all 5,349 questions | **98.82%** (5,286 correct) |
| Exact-match accuracy, excluding 18 dataset issues | 99.156% (5,286 / 5,331) |
| ANLS (derived), all questions | 0.991 |

**Error breakdown (63 incorrect answers):**

| Category | Count | Meaning |
|---|---:|---|
| Prompt/LLM miss | 18 | Parsed content was correct; the LLM answered wrongly |
| Incorrect parse | 13 | OCR/parse errors such as character confusion or table misreads |
| Not ADE focus | 9 | Questions about purely visual layout, beyond text extraction |
| Missed parse | 5 | Information present in the document was not extracted |
| Dataset issue | 18 | Ground truth judged questionable by LandingAI; excluded from the 99.156% figure |

Each one is listed in [`errors.jsonl`](errors.jsonl) with its question, ground truth, prediction, category, and per-question ANLS. An [interactive gallery](https://landing-ai.github.io/ade-docvqa-benchmark/gallery.html) shows each error with bounding-box overlays.

## Caveats

- **Not the official DocVQA metric.** The official metric is ANLS, computed on the hidden test set via the [DocVQA leaderboard](https://rrc.cvc.uab.es/?ch=17). These are validation-set results. The ANLS here is derived: each exact-match answer scores 1.0, and the 63 failures are scored individually.
- **Exclusions.** The 99.156% figure removes 18 questions after seeing the results. Under this repo's [methodology](../../../../METHODOLOGY.md), the headline figure counts all questions.
- **No complete predictions file.** The source repo has predictions for only a subset of questions from an earlier run, so per-question outputs for the 5,286 correct answers are not available.
- **QA model is ambiguous.** The source README says Claude Sonnet 4.5. `evaluate.py` hard-codes `claude-sonnet-4-20250514` (Sonnet 4), while the client defaults to `claude-sonnet-4-5-20250929`.
- **Two systems.** The scores reflect ADE parsing *and* an LLM answering questions. They are not a standalone ADE score.

## Files

- `summary.json`: machine-readable summary
- `errors.jsonl`: all 63 incorrect answers (45 errors + 18 dataset issues)
- `prompt.md`: the question-answering system prompt used
