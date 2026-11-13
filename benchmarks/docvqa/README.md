# DocVQA: LandingAI ADE results

**DocVQA** is a visual question answering benchmark over scanned document images, introduced by Mathew, Karatzas, and Jawahar ([WACV 2021](https://arxiv.org/abs/2007.00398)). Each sample is a document page and a natural-language question; answers are scored with ANLS (Average Normalized Levenshtein Similarity).

## LandingAI results (run by us, reproducible here)

| Run date | Split | Samples | ANLS | ADE version | Results |
|---|---|---|---|---|---|
| _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | [`results/2026-11/`](results/2026-11/) |

## Other published results for reference

Scores below are copied from the cited source as reported there. LandingAI did not run these systems. Differences in split or setup may limit direct comparison.

| System | ANLS | Split | Source | Retrieved |
|---|---|---|---|---|
| _to be added_ | | | [DocVQA leaderboard](https://rrc.cvc.uab.es/?ch=17&com=evaluation&task=1) | |

## Reproduce

```bash
pip install -r requirements.txt
export VISION_AGENT_API_KEY=...
python benchmarks/docvqa/download_data.py
python -m harness.run --benchmark docvqa
```

The configuration used for the published run is in [`config.yaml`](config.yaml).

## Dataset license

The DocVQA data is not redistributed in this repository. See the [official DocVQA site](https://www.docvqa.org/) for terms of use.

## Citation

```bibtex
@inproceedings{mathew2021docvqa,
  title     = {DocVQA: A Dataset for VQA on Document Images},
  author    = {Mathew, Minesh and Karatzas, Dimosthenis and Jawahar, C. V.},
  booktitle = {WACV},
  year      = {2021}
}
```
