"""Shared keyword normalization helpers for reusable retrieval pipelines."""

from __future__ import annotations

import json
from typing import Any


def coerce_keywords(raw: Any) -> list[str]:
    """Normalize a keyword payload into a stable list of strings."""

    if isinstance(raw, list):
        return [str(item) for item in raw]
    if isinstance(raw, str):
        try:
            decoded = json.loads(raw)
        except Exception:  # noqa: BLE001
            return [raw]
        if isinstance(decoded, list):
            return [str(item) for item in decoded]
        return [str(decoded)]
    return [str(item) for item in (raw or [])]
