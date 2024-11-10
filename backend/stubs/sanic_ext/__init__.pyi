from typing import Any, Callable, Optional, Type, TypeVar, Union

from sanic import Request
from sanic_ext.extensions.openapi import openapi

__all__ = ['openapi']

F = TypeVar('F', bound=Callable[..., Any])

# noinspection PyUnusedLocal
def validate(
    json: Optional[Union[Callable[[Request], bool], Type[object]]] = None,
    form: Optional[Union[Callable[[Request], bool], Type[object]]] = None,
    query: Optional[Union[Callable[[Request], bool], Type[object]]] = None,
    body_argument: str = 'body',
    query_argument: str = 'query',
) -> Callable[[F], F]: ...
