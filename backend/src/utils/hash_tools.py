import hashlib


def calc_sha1(content: str) -> str:
    return hashlib.sha1(content.encode(encoding='utf-8')).hexdigest()


def calc_md5(content: str) -> str:
    return hashlib.md5(content.encode(encoding='utf-8')).hexdigest()


def hash_int(salt: str, value: int, length: int = 16) -> int:
    return int(hashlib.md5((salt + str(value)).encode(encoding='utf-8')).hexdigest()[:length], 16)
