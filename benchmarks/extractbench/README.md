# ExtractBench: LandingAI ADE results

**ExtractBench** is a benchmark for structured field extraction from documents. _TODO: add a one-sentence description, authors, and link to the paper/repo._

## LandingAI results (run by us, reproducible here)

| Run date | Split | Samples | Field F1 | ADE version | Results |
|---|---|---|---|---|---|
| _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | [`results/2026-11/`](results/2026-11/) |

## Other published results for reference

Scores below are copied from the cited source as reported there. LandingAI did not run these systems. Differences in split or setup may limit direct comparison.

| System | Field F1 | Split | Source | Retrieved |
|---|---|---|---|---|
| _to be added_ | | | _TODO: official leaderboard or paper_ | |

## Reproduce

```bash
pip install -r requirements.txt
export VISION_AGENT_API_KEY=...
python benchmarks/extractbench/download_data.py
python -m harness.run --benchmark extractbench
```

## Dataset license

The ExtractBench data is not redistributed in this repository. _TODO: link the dataset's license._

## Citation

_TODO: add the benchmark authors' BibTeX._
