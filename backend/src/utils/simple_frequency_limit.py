from typing import Hashable

_cache: dict[Hashable, float] = {}


def get_last_visit(key: Hashable) -> float:
    return _cache.get(key, -1)


def set_last_visit(key: Hashable, timestamp_ms: float) -> None:
    _cache[key] = timestamp_ms
