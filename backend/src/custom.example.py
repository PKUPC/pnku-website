from __future__ import annotations

from typing import TYPE_CHECKING

from sanic import HTTPResponse, Request, response


if TYPE_CHECKING:
    from src.state import User


def store_user_log(
    req: Request | None,
    module: str,
    event: str,
    message: str,
    extra: dict[str, int | str | bool],
    manual_user: User | None = None,
) -> None:
    return


def handle_report(req: Request) -> HTTPResponse:
    return response.text('OK')


def handle_event(req: Request) -> HTTPResponse:
    return response.text('OK')
