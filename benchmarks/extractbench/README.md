# ExtractBench: LandingAI ADE results

**ExtractBench** ([run-llama/ExtractBench](https://github.com/run-llama/ExtractBench), [arXiv 2607.29677](https://arxiv.org/abs/2607.29677)) is a benchmark from LlamaIndex for **schema-guided extraction from enterprise documents**. Given a document and a JSON Schema, a system must return schema-valid JSON with correct values, every record of each repeated structure, `null` for missing fields, and source evidence for each value. The benchmark has 370 documents (4,869 pages, 67 document types), split into short, medium, and long documents.

> Not to be confused with a different benchmark of the same name, [ExtractBench (arXiv 2602.12247)](https://arxiv.org/abs/2602.12247), by Ferguson et al. Results here use the LlamaIndex benchmark.

**Metrics** (as defined by the benchmark authors):
- **Value F1:** F1 of extracted values, averaged across documents (each document weighted equally). Reported overall and by split.
- **Grounding F1:** a value counts only if it is correct *and* its evidence box overlaps an accepted box at IoU ≥ 0.5 (word level), or cites the correct page (page level).
- **Cost per page:** mean of each document's cost divided by its page count, at public list prices.

Documents that fail or exceed the official 30-minute limit score zero.

## LandingAI results (run by us)

| Run | ADE Extract version | Value F1 (Overall) | Short | Medium | Long | Word grounding F1 | Latency p50 (s/doc) | LLM cost / doc | Status | Results |
|---|---|---:|---:|---:|---:|---|---:|---:|---|---|
| 2026-11-12 | extract-20261111 | **94.02** | 94.66 | 93.43 | 88.99 | _not reported_ | 124 | $0.039 | Preliminary | [`results/2026-11/`](results/2026-11/) |
| 2026-11-12 | extract-20260903 | 91.62 | 93.42 | 89.74 | 78.26 | _not reported_ | 38 | $0.637 | Previous version | [`results/2026-11/`](results/2026-11/) |

All 370 documents (252 short, 98 medium, 20 long), scored with the official ExtractBench harness. `extract-20261111` ran with grounding enabled. Cost is LLM cost per document, not the leaderboard's cents per page at list prices. The results are preliminary: a re-run with latency improvements is pending, followed by an official leaderboard submission. See the [run README](results/2026-11/README.md) for latency, cost, and what is still missing.

## Other published results for reference

Copied from the [official ExtractBench leaderboard](https://github.com/run-llama/ExtractBench#extractbench-leaderboard) as reported there, retrieved 2026-11-13. LandingAI did not run these systems. Top 5 of 54 ranked systems by overall value F1; see the source for the full list.

| Rank | System | Value F1 (Overall) | Short | Medium | Long | ¢ / page |
|---:|---|---:|---:|---:|---:|---:|
| 1 | LlamaExtract Agentic Plus | 96.17 | 97.02 | 94.30 | 94.65 | 7.50¢ |
| 2 | LlamaExtract Agentic Plus (Max Effort) | 96.17 | 96.82 | 95.48 | 91.36 | 19.11¢ |
| 3 | Reducto Deep Extract | 96.08 | 96.84 | 94.80 | 92.85 | 6.35¢ |
| 4 | Pulse (Effort) | 96.07 | 96.83 | 94.70 | 93.24 | 10.50¢ |
| 5 | LlamaExtract Agentic | 95.65 | 96.06 | 94.79 | 94.73 | 3.12¢ |

## Reproduce

Scoring uses the benchmark's official evaluator (`llama-extract-bench`), not a reimplementation.

```bash
pip install -r requirements.txt
export ADE_API_KEY=...
python benchmarks/extractbench/download_data.py
python -m harness.run --benchmark extractbench
```

The configuration used for the published run is in [`config.yaml`](config.yaml).

## Dataset and license

The data is not redistributed in this repository. It is published on Hugging Face at [llamaindex/ExtractBench](https://huggingface.co/datasets/llamaindex/ExtractBench); the benchmark code is licensed Apache-2.0. Check the dataset card for the data's terms of use.

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
