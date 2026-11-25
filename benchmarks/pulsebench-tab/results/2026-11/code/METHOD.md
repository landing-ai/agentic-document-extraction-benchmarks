# Method: PulseBench-Tab, run 2026-11-24

## Official run
- **Benchmark:** PulseBench-Tab (Pulse), 1,820 images, each containing one table, in nine languages. Hugging Face `pulse-ai/PulseBench-Tab`, revision `e0e1fd5c4b3f7daa0c6afed88177ed9242e6593d`.
- **Rules followed:** Pulse's provider rules (`providers/README.md` in Pulse's repository): one run of the full dataset with the vendor's documented settings, no prompt or option tuning against the answer key, the output saved verbatim, a response with no `<tr>` counted as missing, raw responses kept.
- **System:** LandingAI ADE Parse, model `dpt-3-pro-20261111`, Parse Jobs API, `standard` service tier, every other option at its documented default. One PNG per request, sent unchanged.
- **Adapter:** [`landingai.py`](landingai.py), a provider for Pulse's runner, submitted to Pulse together with these predictions. The copy here differs from the file used for the run in two ways: one docstring comment, and the API key is read from `ADE_API_KEY` (the run read the same key from `VISION_AGENT_API_KEY`). The request logic is identical. Registry entry:
  ```python
  "landingai_dpt3_pro": {"display_name": "LandingAI ADE (DPT-3 Pro)", "adapter": "providers.landingai:LandingAIProvider",
                         "config": {"model": "dpt-3-pro-20261111", "service_tier": "standard", "prediction": "tables"},
                         "concurrency": 16},
  ```
- **Prediction:** every `table` block in the response, in document order, sliced verbatim from the response Markdown by the block's `grounding.range`. Nothing is cleaned or edited. This is the same selection the benchmark's other parse-API adapters use.
- **Retries:** only API errors are resubmitted; there were none. No sample was re-run.
- **Scoring:** Pulse's `tlag_scorer.py` at commit `b57992c`, unmodified, in Pulse's published mode: the mean over samples with a prediction, with coverage reported. We also report the mean with missing samples counted as zero.

## Revised score (diagnostic)
[`revised_score.py`](revised_score.py) re-scores the same predictions with Pulse's scorer, replacing only its text-normalization step so that answer-key writing conventions are ignored on both the answer key and the prediction. With no rule applied it reproduces the official per-sample scores exactly. The rules are listed in the benchmark README. They are our choice, several are deliberately generous, and the revised score is not the PulseBench-Tab score.
