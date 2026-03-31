from __future__ import annotations

import math
import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]{2,}")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def embed_text(text: str) -> dict[str, float]:
    tokens = tokenize(text)
    if not tokens:
        return {}

    counts = Counter(tokens)
    norm = math.sqrt(sum(value * value for value in counts.values()))
    if norm == 0:
        return {}

    return {token: value / norm for token, value in counts.items()}


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0

    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a

    return sum(value * vec_b.get(token, 0.0) for token, value in vec_a.items())
