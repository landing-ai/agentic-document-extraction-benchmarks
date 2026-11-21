# ExtractBench: LandingAI ADE results

[ExtractBench](https://github.com/run-llama/ExtractBench) is LlamaIndex's benchmark for schema-guided extraction: 370 public documents (4,869 pages, 67 document types), each with a fixed JSON schema and an answer key, scored by a deterministic evaluator. Documents that fail or exceed 30 minutes score zero.

> Not to be confused with a different benchmark of the same name, [arXiv 2602.12247](https://arxiv.org/abs/2602.12247).

## Results (run 2026-11-20)

LandingAI Agentic Document Extraction (ADE): Parse `dpt-3-pro-20261111` and Extract `extract-20261111`, public production API, standard tier, grounding on. Submitted to the official leaderboard in [run-llama/ExtractBench#172](https://github.com/run-llama/ExtractBench/pull/172).

| | All (370) | Short (252) | Medium (98) | Long (20) |
|---|---:|---:|---:|---:|
| **Value F1** | **94.11** | 94.88 | 93.26 | 88.65 |
| Precision / recall | 94.23 / 94.07 | 94.92 / 94.89 | 93.65 / 93.03 | 88.43 / 88.87 |
| Word-level grounding F1 | 66.14 | 63.23 | 72.36 | 72.32 |
| Page-level grounding F1 | 83.48 | 81.98 | 87.86 | 80.95 |
| Cost per page (list price) | $0.0474 | $0.0472 | $0.0373 | $0.0996 |
| Mean latency per document | | 294 s | 444 s | 541 s |

- **Failures and timeouts:** one document failed (`long/real_ishares_iboxx_bond_etfs`: the extraction job hit the service's own time limit). No document exceeded 30 minutes; the median was 279 s and the slowest 1,423 s.
- **Cost:** billed credits × $0.01 list price per credit; $309.21 in total.
- **Scoring:** ExtractBench's own evaluator at [`ab573f7`](https://github.com/run-llama/ExtractBench/commit/ab573f7). Scores are identical under the earlier evaluator (`36e9d20`).
- **Leaderboard context:** on the leaderboard as of 2026-11-20 this ranks 17th of 59 on value F1 and has the highest word-level grounding of the 12 specialized document APIs. The leader is LlamaExtract Agentic Plus at 96.17. See the [official leaderboard](https://github.com/run-llama/ExtractBench#extractbench-leaderboard) for current standings.

## Files

Everything from the run is in [`results/2026-11/`](results/2026-11/). Large files are gzipped. Internal job and organization IDs, and local file paths, are replaced with placeholders; nothing else is changed.

| Path | Contents |
|---|---|
| `summary.json` | Headline metrics, models, code versions |
| `leaderboard_row.csv` | The row submitted to ExtractBench's `leaderboard.csv` |
| `per_document.csv` | Value, precision, recall, grounding, latency, pages and cost for each of the 370 documents |
| `outputs/<split>/<doc>.result.json.gz` | Normalized output: extracted data and field citations (what the evaluator scores) |
| `outputs/<split>/<doc>.raw.json.gz` | Raw API output: parse Markdown and structure, extraction, extraction metadata, billing |
| `outputs/<split>/<doc>.cost.json.gz` | Cost accounting per document |
| `evaluation/<split>/` | Evaluator output per split: `evaluation_results.csv`, `evaluation_report.md`, the full `evaluation_report.json.gz`, and HTML reports |
| `evaluation/` | Error list, run metadata, dashboard and leaderboard HTML |
| `logs/` | Run record and console logs |

## Reproduce

The connector is in [run-llama/ExtractBench#172](https://github.com/run-llama/ExtractBench/pull/172). With that branch checked out and `LANDING_AI_API_KEY` set in `.env`:

```bash
uv sync --extra runners
uv run extract-bench run landingai_ade_v2_extract --output_dir output --group long   --max_concurrent 4
uv run extract-bench run landingai_ade_v2_extract --output_dir output --group medium --max_concurrent 8
uv run extract-bench run landingai_ade_v2_extract --output_dir output --group short  --max_concurrent 12
uv run extract-bench run landingai_ade_v2_extract --output_dir output --skip_inference
```

The dataset downloads from Hugging Face ([llamaindex/ExtractBench](https://huggingface.co/datasets/llamaindex/ExtractBench), revision `f9b910906cd7`) on first run. One document (`short/sched_i__after_violence_project_ty2024`) failed in the first pass on a rounding bug in the connector's cost total; it was re-run after the fix, which does not affect extraction, and all 370 documents were re-scored.

## Dataset and license

The dataset is not redistributed here; it is published on Hugging Face under the benchmark's terms, and the benchmark code is Apache-2.0. The output files contain values extracted from those public documents.

## Citation

```bibtex
@misc{zhang2026extractbench,
  title         = {ExtractBench: A Benchmark for Schema-Guided Enterprise Document Extraction},
  author        = {Zhang, Boyang and Lyjak, Adrian and Stewart, Eli and Li, Zhaoqi and Suo, Simon},
  year          = {2026},
  eprint        = {2607.29677},
  archivePrefix = {arXiv}
}
```
