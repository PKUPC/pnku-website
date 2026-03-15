from sanic import Blueprint


bp = Blueprint('sync', url_prefix='/sync')

from .endpoint import puzzle  # noqa: F401


__all__ = [
    'bp',
]
