"""Shared metric implementations.

Where a benchmark ships an official scorer, verify these match it before publishing.
"""

from __future__ import annotations

import Levenshtein


def _normalize(text: str) -> str:
    return " ".join(str(text).lower().strip().split())


def anls(prediction: str, answers: list[str], threshold: float = 0.5) -> float:
    """Average Normalized Levenshtein Similarity for one question (DocVQA definition).

    Returns the max similarity over ground-truth answers; values below `threshold` score 0.
    """
    pred = _normalize(prediction)
    best = 0.0
    for answer in answers:
        gt = _normalize(answer)
        if not gt and not pred:
            return 1.0
        dist = Levenshtein.distance(pred, gt) / max(len(pred), len(gt))
        best = max(best, 1.0 - dist)
    return best if best >= threshold else 0.0


def field_f1(predicted: dict, expected: dict) -> dict[str, float]:
    """Field-level precision/recall/F1 using exact match after normalization.

    Replace with the benchmark's official definition if it differs.
    """
    pred = {k: _normalize(v) for k, v in predicted.items() if v not in (None, "")}
    gold = {k: _normalize(v) for k, v in expected.items() if v not in (None, "")}
    tp = sum(1 for k, v in pred.items() if gold.get(k) == v)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}
