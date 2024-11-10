from __future__ import annotations

from typing import TYPE_CHECKING

from sanic.request import Request

from src import utils
from src.state import User


if TYPE_CHECKING:
    pass


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

            if user is not None and user.model.login_properties.type == 'email':
                if info.get('jwt_salt', '') != user.model.login_properties.jwt_salt:
                    return None

    return user
