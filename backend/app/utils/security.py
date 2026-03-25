from collections import Counter
from math import log2


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    probs = [count / len(value) for count in Counter(value).values()]
    return -sum(p * log2(p) for p in probs)


def mask_secret(value: str) -> str:
    if len(value) <= 6:
        return "***"
    return f"{value[:3]}***{value[-3:]}"
