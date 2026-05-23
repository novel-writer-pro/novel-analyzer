"""Shared vector helpers for reusable retrieval pipelines."""

from __future__ import annotations


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity for two dense vectors."""

    if not left or not right or len(left) != len(right):
        return 0.0
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    if left_norm <= 1e-12 or right_norm <= 1e-12:
        return 0.0
    dot = sum(float(a) * float(b) for a, b in zip(left, right, strict=True))
    return float(dot / (left_norm * right_norm))
