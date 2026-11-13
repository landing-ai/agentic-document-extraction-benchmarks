# DocVQA: LandingAI ADE results

**DocVQA** is a visual question answering benchmark over scanned documents from the UCSF Industry Documents Library, introduced by Mathew, Karatzas, and Jawahar ([WACV 2021](https://arxiv.org/abs/2007.00398)). Each sample is a document page and a natural-language question. The validation split has 5,349 questions over 1,286 documents.

## Approach: parse once, answer from the parsed output

We test whether ADE's parsed output keeps enough information to answer the questions **without the image**:

1. Parse each document once with ADE (DPT-2). The output is markdown plus chunk types, page numbers, positions, and bounding boxes.
2. An LLM (Claude Sonnet) answers each question using only that parsed output. It never sees the image.

This mirrors how production systems work: parse once, store the structured output, and query it many times. The scores below reflect ADE parsing together with the LLM's answers.

## LandingAI results (run by us)

| Run | Split | Questions | Exact-match accuracy | Excl. dataset issues | ANLS (derived) | ADE model | QA model | Details |
|---|---|---:|---:|---:|---:|---|---|---|
| 2025-11 | validation | 5,349 | **98.82%** | 99.156% | 0.991 | DPT-2 | Claude Sonnet 4.5 | [`results/2025-11/`](results/2025-11/) |

- **Exact-match accuracy** is a case-insensitive exact string match against any ground-truth answer. It is stricter than ANLS.
- **Excl. dataset issues** removes 18 questions whose ground truth LandingAI judged questionable. They are listed in [`errors.jsonl`](results/2025-11/errors.jsonl) so you can check that judgment.
- **ANLS (derived)** is the official DocVQA metric. It is computed from the 5,286 exact-match answers (1.0 each) plus per-question ANLS for the 63 failures.

Of the 45 errors that remain after excluding dataset issues, 18 are LLM reasoning misses where the parse was correct. 13 are parse errors, 5 are content missed by the parser, and 9 are purely visual questions such as chart reading. See the [run README](results/2025-11/README.md) and the [interactive error gallery](https://landing-ai.github.io/ade-docvqa-benchmark/gallery.html).

## Other published results for reference

The official DocVQA leaderboard ranks systems by ANLS on the **hidden test set**, so it isn't directly comparable to the validation-set results above. Scores below are copied from the cited source as reported there, and LandingAI did not run these systems.

| System | ANLS | Split | Source | Retrieved |
|---|---|---|---|---|
| _to be added_ | | test | [DocVQA leaderboard](https://rrc.cvc.uab.es/?ch=17&com=evaluation&task=1) | |

## Reproduce

The original implementation, including the pre-parsed ADE outputs for all 1,286 documents, is in [landing-ai/ade-docvqa-benchmark](https://github.com/landing-ai/ade-docvqa-benchmark/tree/9d9bdff3b941a54f0961d428adba1bbeb261f378):

```bash
git clone https://github.com/landing-ai/ade-docvqa-benchmark.git
cd ade-docvqa-benchmark
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
python3 evaluate.py   # uses parsed/ outputs and prompt.md; ~1-2 hours
```

The question-answering prompt is also archived here as [`results/2025-11/prompt.md`](results/2025-11/prompt.md). Porting the run into this repo's shared harness (`python -m harness.run --benchmark docvqa`) is still to do.

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
