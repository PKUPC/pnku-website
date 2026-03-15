from sanic import HTTPResponse

from src import secret


def add_cookie(res: HTTPResponse, name: str, value: str, path: str, max_age: int) -> None:
    res.add_cookie(
        name, value, samesite='Lax', httponly=True, path=path, max_age=max_age, secure=secret.USE_SECURE_COOKIE
    )
