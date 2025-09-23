from collections.abc import Callable
from typing import Any, TypeVar

from sanic import Request
from sanic_ext.extensions.openapi import openapi

__all__ = ['openapi']

F = TypeVar('F', bound=Callable[..., Any])

# noinspection PyUnusedLocal
def validate(
    json: Callable[[Request], bool] | type[object] | None = None,
    form: Callable[[Request], bool] | type[object] | None = None,
    query: Callable[[Request], bool] | type[object] | None = None,
    body_argument: str = 'body',
    query_argument: str = 'query',
) -> Callable[[F], F]: ...
