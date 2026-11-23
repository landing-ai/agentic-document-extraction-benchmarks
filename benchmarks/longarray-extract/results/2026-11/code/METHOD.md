# LongArray-Extract: how we ran ADE

Dataset: [Extend-AI/LongArray-Extract](https://huggingface.co/datasets/Extend-AI/LongArray-Extract) (CC BY 4.0), revision `f2ae30264ecd942fa0a9b9e787bb42e1e2577184`, all 45 documents (2,152 pages). Files were checked against the Hugging Face checksums.

## System
- Parse: ADE v2 parse jobs, `dpt-3-pro-20261111`, standard tier.
- Extract: ADE v2 extract jobs, `extract-20261111`, standard tier, default options.
- Production API (api.ade.landing.ai), Python SDK `landingai-ade` 1.18.1, 4 documents in parallel.
- Retries on failure only, as a production integration would: a parse or extract job that errors, fails or times out is resubmitted, up to 3 attempts per stage. A job that completes is never re-run, whatever its output, so answers are never chosen by looking at them. Every attempt is logged, and the reported latency includes retries. A document that still fails scores 0.
- No custom chunking or post-processing; the `extraction` object returned by the API is the prediction.
- The model version reported by the API is recorded for every document.

## Schemas
We used the published schemas (`schemas/*.json`) with one change: the Extend-only keys, which only Extend's engine reads, were translated into ADE's documented equivalents (`schema_for_ade.py`). No field, type, allowed value or existing description was changed.

| Extend-only key | Where | What we did |
|---|---|---|
| `extend:type: "date"` | clinical `start_date`, `end_date`; financial `date`; legal `date` | Replaced with `"format": "YYYY-MM-DD"`, ADE's documented keyword for output formatting. The answer key stores ISO dates and is scored by exact match. |
| `extend:descriptions` (one explanation per enum value) | financial `transaction_type`; legal `relationship_type` | Appended to the field's `description` as "Allowed values: A = ...; B = ...". The `enum` list itself is unchanged. ADE has no keyword for per-value explanations (`enum` takes only the values; `oneOf`/`const` are not supported), so the description is the only place for them. |
| `extend:type: "currency"` | financial `amount` | Removed. The amount object already defines `amount` (number) and `iso_4217_currency_code`. |

Enum fields are left as published: an `enum` list that includes `null` and no `type` keyword. That is one of the forms ADE documents for enum fields that may return null. The answer key never uses null for these fields.

## Scoring
Extend's canonical scorer from the dataset README, copied verbatim (`score.py`): data-point accuracy, rows matched regardless of order (Hungarian algorithm), exact match except fuzzy matching for financial `description` (0.95) and legal `court` (0.85). We report the mean per-document accuracy (macro, Extend's headline metric) and the micro average. A document with no output scores 0.
