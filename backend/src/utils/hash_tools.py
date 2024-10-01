import hashlib


def calc_sha1(content: str) -> str:
    return hashlib.sha1(content.encode(encoding="utf-8")).hexdigest()
