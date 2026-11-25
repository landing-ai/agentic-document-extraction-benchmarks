# PulseBench-Tab: LandingAI ADE results

[PulseBench-Tab](https://huggingface.co/datasets/pulse-ai/PulseBench-Tab) is a table-extraction benchmark published by Pulse: 1,820 images, each containing one table, in nine languages (English 589, Chinese 213, Spanish 176, Russian 170, French 165, Japanese 164, Arabic 146, German 113, Korean 84). Each prediction is scored against a hand-made HTML answer key with T-LAG, which links every cell to its right and lower neighbours, compares cell text with a strict similarity (Levenshtein similarity raised to the 7th power) and reports an F1 over the matched links. The dataset and scorer are published under CC BY-NC-ND 4.0.

## Results (run 2026-11-24)

LandingAI Agentic Document Extraction (ADE) Parse, model `dpt-3-pro-20261111`, Parse Jobs API, standard tier, documented default options. All 1,820 samples, one run, following the benchmark's provider rules. These predictions were also submitted to the benchmark repository: [Pulse-Software-Corp/PulseBench-Tab#5](https://github.com/Pulse-Software-Corp/PulseBench-Tab/pull/5).

| | Official score |
|---|---:|
| **T-LAG, samples with a table (the benchmark's published mode)** | **78.6** |
| Coverage (samples where ADE returned a table) | 84.2% (1,532 of 1,820) |
| T-LAG with samples without a table counted as 0 | 66.2 |
| Median T-LAG per table | 90.1 |
| Tables scored 100 | 325 |

| Language | Samples | Coverage | T-LAG | T-LAG, missing as 0 |
|---|---:|---:|---:|---:|
| English | 589 | 81.2% | 73.6 | 59.7 |
| Chinese | 213 | 94.4% | 87.6 | 82.6 |
| Spanish | 176 | 84.7% | 81.6 | 69.1 |
| Russian | 170 | 87.1% | 84.3 | 73.4 |
| French | 165 | 89.7% | 86.6 | 77.7 |
| Japanese | 164 | 85.4% | 83.0 | 70.8 |
| Arabic | 146 | 80.1% | 60.6 | 48.6 |
| German | 113 | 72.6% | 76.9 | 55.8 |
| Korean | 84 | 82.1% | 75.7 | 62.2 |

- **Coverage:** for 288 samples (15.8%) ADE read the content but did not return a table block: 176 came back as text, 77 as a figure and 35 as other blocks. Under the benchmark's rules a response without a table row counts as missing. Their complete responses are in `raw_responses.jsonl.gz`.
- **Run:** 24.5 minutes, 0 API errors, no retries, 1,619.3 credits (about 0.89 per sample).

## Revised score (diagnostic): 87.1

**This is not our PulseBench-Tab score.** The official score above is.

T-LAG compares text strictly, so how the answer key writes down printed text affects every score. Looking at the answer key language by language, we found consistent writing conventions, for example:
- line breaks inside a cell are stored as `<br>`, which the scorer reads with no space, so "Total Population" printed on two lines is scored as "TotalPopulation.";
- words hyphenated at a printed line end keep the hyphen ("Luftschich-ten");
- dot leaders are kept in some tables and dropped in others;
- Arabic tables are stored in right-to-left column order in some keys and left-to-right in others with the same printed layout, and the scorer's right-neighbour links reverse with the order;
- Arabic letter variants, full-width and ordinary punctuation in Chinese and Japanese, and curly and straight apostrophes in French are mixed.

To measure how much of our score these conventions account for, [`revised_score.py`](results/2026-11/code/revised_score.py) re-scores the same predictions with the benchmark's scorer, unchanged except for its text-normalization step. Each rule is applied identically to the answer key and to our output. With no rule applied, it reproduces the official per-sample scores exactly.

| Convention ignored (answer key and prediction) | T-LAG | Change |
|---|---:|---:|
| None (official) | 78.63 | |
| Dot leaders and stray dots | 81.99 | +3.36 |
| Spaces, including words joined at line breaks | 80.77 | +2.14 |
| Arabic column order (better of the two orders kept) | 79.67 | +1.04 |
| Bold and italic Markdown markers | 79.12 | +0.49 |
| Full-width vs ordinary punctuation | 78.89 | +0.26 |
| End-of-line hyphens | 78.80 | +0.17 |
| Super- and subscript digits | 78.79 | +0.16 |
| Bullets and middle-dot leaders | 78.78 | +0.15 |
| Curly vs straight quotes | 78.73 | +0.10 |
| Arabic letter variants, vowel marks, Arabic-Indic digits | 78.71 | +0.08 |
| Raised-dot decimals (22·7) | 78.68 | +0.05 |
| Ditto marks | 78.63 | 0.00 |
| The five formatting rules together (dots, spaces, bold, hyphens, super/subscripts) | 85.00 | +6.37 |
| The six language conventions together | 80.37 | +1.74 |
| **All of the above together (revised score)** | **87.11** | **+8.48** |

Rows overlap, because one cell can carry several conventions, so they do not add up. How to read the revised score:
- **It is an upper bound.** The rules are ours, and some are deliberately generous: removing every space or hyphen also hides a few genuine reading errors.
- **It applies to any system.** The same rules would change the score of any other system scored on this benchmark, so the revised score is not comparable with published PulseBench-Tab scores.
- **It does not touch coverage.** The 288 samples without a table are still missing; with them counted as 0, the revised mean is 73.3.

The rules, exactly as applied, are in [`revised_score.py`](results/2026-11/code/revised_score.py). Per-sample revised scores are in `revised_scores.json` and `per_sample.csv`.

## Method

The full method is in [`results/2026-11/code/METHOD.md`](results/2026-11/code/METHOD.md). In short:
- **Dataset:** Hugging Face revision `e0e1fd5c4b3f7daa0c6afed88177ed9242e6593d`.
- **Scorer:** `tlag_scorer.py` from [Pulse-Software-Corp/PulseBench-Tab](https://github.com/Pulse-Software-Corp/PulseBench-Tab) at commit `b57992c`, unmodified (SHA-256 in `manifest.json`).
- **Runner:** the benchmark's own provider runner with our adapter, [`landingai.py`](results/2026-11/code/landingai.py).
- **Prediction:** every `table` block in the ADE response, in document order, copied verbatim from the response Markdown. No cleaning, no tuning, one pass.
- **Retries:** API errors only; none occurred.

## Files

Everything from the run is in [`results/2026-11/`](results/2026-11/). Internal job and organization IDs are replaced with placeholders; nothing else is changed.

| Path | Contents |
|---|---|
| `summary.json` | Official score, coverage and per-language results; revised score and change per rule |
| `scores.json` | The official scorer's output (summary and per-sample scores) |
| `per_sample.csv` | Language, whether a table was returned, official and revised T-LAG, credits and latency for each of the 1,820 samples |
| `revised_scores.json` | Mean and per-sample T-LAG for every rule in the table above |
| `manifest.json` | Run record: dataset revision, scorer commit and checksum, model, API, tier, procedure, environment, times, outcome, code checksums |
| `logs.jsonl` | One line per sample: model version reported by the API, credits, latency, output size |
| `predictions/<sample_id>.html` | The prediction for each of the 1,532 samples with a table (what the scorer reads) |
| `raw_responses.jsonl.gz` | The complete ADE response for all 1,820 samples, including the 288 without a table |
| `code/` | `landingai.py` (adapter), `revised_score.py` and `METHOD.md` |

## Reproduce

```bash
pip install -r requirements.txt
python benchmarks/pulsebench-tab/download_data.py      # pinned dataset + scorer -> data/pulsebench-tab/

# Official score of the published predictions
python data/pulsebench-tab/tlag_scorer.py --gt data/pulsebench-tab/ground_truth \
    --pred benchmarks/pulsebench-tab/results/2026-11/predictions --output scores.json

# Revised (diagnostic) score
python benchmarks/pulsebench-tab/results/2026-11/code/revised_score.py \
    --data data/pulsebench-tab --pred benchmarks/pulsebench-tab/results/2026-11/predictions
```

To produce new predictions, clone [Pulse-Software-Corp/PulseBench-Tab](https://github.com/Pulse-Software-Corp/PulseBench-Tab), add `code/landingai.py` as `providers/landingai.py` with the registry entry in `METHOD.md`, set `VISION_AGENT_API_KEY` (never commit it) and run `python -m providers.run run --provider landingai_dpt3_pro`.

## Dataset and license

The dataset and scorer are not redistributed here; `download_data.py` fetches them from the official sources at the pinned versions. Both are published by Pulse under CC BY-NC-ND 4.0. The prediction files and raw responses contain text that ADE read from the benchmark's images.
