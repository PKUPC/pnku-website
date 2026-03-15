from __future__ import annotations

import httpx

from sanic import HTTPResponse, response
from sanic.exceptions import SanicException
from sanic.request import Request
from sanic_ext.exceptions import ValidationError

from src import secret, utils
from src.state import User
from src.store.user_store import EmailLoginPropertyModel


class UserJWTError(Exception):
    def __init__(self, message: str):
        self.message: str = message

    def __str__(self) -> str:
        return self.message


def get_cur_user(req: Request) -> User | None:
    user: User | None = None

    game = req.app.ctx.worker.game
    if game is None:
        req.app.ctx.worker.log('warning', 'app.get_cur_user', 'game is not available, skipping user detection')
    else:
        auth_token = req.cookies.get('auth_token', None)
        if auth_token is not None:
            status, info = utils.jwt_decode(auth_token)
            if not status:
                return None
                # raise UserJWTError(info)
            assert isinstance(info, dict)
            user = game.users.user_by_id.get(info.get('user_id', None), None)

            if user is not None and user.check_login() is not None:
                return None

            if user is not None and isinstance(user.model.login_properties, EmailLoginPropertyModel):
                if info.get('jwt_salt', '') != user.model.login_properties.jwt_salt:
                    return None

    return user


def get_http_client(_req: Request) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        http2=True,
        mounts=secret.OAUTH_HTTP_MOUNTS,
        timeout=secret.OAUTH_HTTP_TIMEOUT,
    )


async def handle_error(req: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, SanicException):
        if isinstance(exc, ValidationError):
            return response.json({'status': 'error', 'title': 'INVALID PARAMS', 'message': '参数格式错误'})
        raise exc

    try:
        user = get_cur_user(req)
        debug_info = f'{req.id} {req.uri_template} U#{"--" if user is None else user.model.id}'
    except Exception as e:
        debug_info = f'no debug info, {repr(e)}'

    req.app.ctx.worker.log(
        'error', 'app.handle_error', f'exception in request ({debug_info}): {utils.get_traceback(exc)}'
    )
    return response.html(
        '<!doctype html>'
        '<h1>🤡 500 — Internal Server Error</h1>'
        '<p>This accident is recorded.</p>'
        f'<p>If you believe there is a bug, tell admin about this request ID: {req.id}</p>'
        '<br>'
        '<p>😭 <i>Project Guiding Star</i></p>',
        status=500,
    )
