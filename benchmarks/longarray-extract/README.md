# LongArray-Extract: LandingAI ADE results

[LongArray-Extract](https://www.extend.ai/resources/long-array-extraction-benchmark) is Extend's benchmark for extracting long arrays (hundreds to thousands of rows) from long documents. It has 45 synthetic documents (2,152 pages, 29,328 rows) in three verticals: 12 clinical adverse-event reports, 25 bank statements and 8 legal pleadings. Each comes with a JSON schema and an answer key. It is scored by data-point accuracy, with rows matched regardless of order, and documents that fail score zero. The dataset is on Hugging Face as [Extend-AI/LongArray-Extract](https://huggingface.co/datasets/Extend-AI/LongArray-Extract) (CC BY 4.0).

## Results (run 2026-11-23)

LandingAI Agentic Document Extraction (ADE): Parse `dpt-3-pro-20261111` and Extract `extract-20261111`, public production API, standard tier. All 45 documents, one complete run.

| | All (45) | Clinical (12) | Financial (25) | Legal (8) |
|---|---:|---:|---:|---:|
| **Mean per-document accuracy** | **99.04%** | 99.24% | 99.14% | 98.43% |
| Micro accuracy (all data points) | 99.02% | 99.09% | 99.28% | 98.15% |
| Documents completed | 45 | 12 | 25 | 8 |
| Rows returned / expected | 29,331 / 29,328 | 5,166 / 5,162 | 21,103 / 21,104 | 3,062 / 3,062 |

- **Completion:** 45 of 45 documents completed. No job failed and none needed a retry.
- **Versions:** every document reported `dpt-3-pro-20261111` for parse and `extract-20261111` for extract.
- **Cost:** 15,083.7 credits, which is $150.84 at the $0.01 list price per credit, or $0.070 per page.
- **Latency:** median 358 s per document (parse plus extract); slowest 1,467 s. Four documents ran in parallel, and the whole run took 1 h 28 min.
- **Lowest document:** `sa_04_n700` (bank statement) scored 83.2%. Extract returned the wrong last four digits of the account number (`3933` instead of `9933`) on all 700 rows, although the parsed text shows the correct number. Every other document scored 95.4% or higher, and 37 of 45 scored above 99%.

### Published results for reference

As reported by Extend on its [benchmark page](https://www.extend.ai/resources/long-array-extraction-benchmark) (published 2026-06-02, retrieved 2026-11-23), mean per-document accuracy on the same 45 documents. We did not run these systems.

| System | Mean per-document accuracy |
|---|---:|
| Extend MAX | 99.2% |
| **LandingAI ADE (this run)** | **99.04%** |
| Unnamed peer (as reported by Extend) | 97.4% |
| Claude Opus 4.7 | 83.1% |
| Reducto Standard | 80.9% |

## Method

The full method is in [`results/2026-11/code/METHOD.md`](results/2026-11/code/METHOD.md). In short:

- **Dataset:** Hugging Face revision `f2ae30264ecd942fa0a9b9e787bb42e1e2577184`. The SHA-256 of each parquet file is in `manifest.json`.
- **Schemas:** the published schemas, with Extend-specific keys translated to ADE's documented equivalents by [`schema_for_ade.py`](results/2026-11/code/schema_for_ade.py). No field, type, allowed value or description was changed. The changes:
  - `extend:type: date` → `format: YYYY-MM-DD`;
  - `extend:descriptions` (per-value explanations) are appended to the field's description;
  - `extend:type: currency` is dropped, because the object already defines amount and currency code.
  
  The translated schemas are in [`results/2026-11/schemas_ade/`](results/2026-11/schemas_ade/).
- **Run:**
  - No post-processing: the API's `extraction` object is the prediction.
  - A job that errors, fails or times out is resubmitted, up to 3 attempts per stage.
  - A completed job is never re-run, whatever its output.
  - Every attempt is logged. This run needed no retries.
- **Scoring:** Extend's reference scorer from the dataset README, copied unchanged into [`score.py`](results/2026-11/code/score.py):
  - rows are matched with the Hungarian algorithm;
  - matching is exact, except fuzzy matching for financial `description` (0.95) and legal `court` (0.85).

## Files

Everything from the run is in [`results/2026-11/`](results/2026-11/). Internal job and organization IDs, and local file paths, are replaced with placeholders; nothing else is changed.

| Path | Contents |
|---|---|
| `summary.json` | Mean per-document and micro accuracy, completion and row counts, overall and per vertical |
| `per_document.csv` | Pages, expected and returned rows, correct and total data points, and accuracy for each of the 45 documents |
| `manifest.json` | Run record: dataset revision and checksums, models, API, tier, SDK, procedure, schema and code checksums, environment, command, start and finish times, outcome |
| `logs.jsonl` | One line per document: every job attempt, model versions reported by the API, page count, failed pages, credits, timings |
| `predictions/<vertical>/<doc>.json` | The extracted object returned by ADE for each document (what the scorer reads) |
| `schemas_ade/` | The schemas sent to ADE |
| `code/` | The exact code used (`run_ade.py`, `schema_for_ade.py`, `score.py`; checksums match `manifest.json`) and `METHOD.md` |
| `raw_files.txt` | SHA-256 of the raw parse and extract outputs, which are kept by LandingAI and not published here |

## Reproduce

```bash
pip install -r requirements.txt
python benchmarks/longarray-extract/download_data.py   # pinned revision -> data/longarray-extract/

mkdir work && cp benchmarks/longarray-extract/results/2026-11/code/*.py work/
ln -s ../data/longarray-extract work/data
cd work
python schema_for_ade.py                     # writes data/schemas_ade/ (identical to results/2026-11/schemas_ade/)
echo "VISION_AGENT_API_KEY=..." > .env.local  # your LandingAI API key; never commit it
python run_ade.py --run my-run --go
python score.py runs/my-run/predictions
```

To re-score the published predictions without calling the API: `python score.py ../benchmarks/longarray-extract/results/2026-11/predictions` from `work/`.

## Dataset and license

The dataset is not redistributed here. It is published by Extend on Hugging Face under CC BY 4.0, and the documents are synthetic. The prediction files contain values extracted from those documents.
