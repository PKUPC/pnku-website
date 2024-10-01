from typing import Hashable

cache: dict[Hashable, float] = {}


def get_last_visit(key: Hashable) -> float:
    return cache.get(key, -1)


def set_last_visit(key: Hashable, timestamp_ms: float) -> None:
    cache[key] = timestamp_ms
