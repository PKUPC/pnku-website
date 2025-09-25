import time

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import secret, utils
from src.adhoc.constants.api.response import response_message
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User

from . import wish_checker, wish_response


bp: Blueprint = Blueprint('wish-user', url_prefix='/wish/user')


@dataclass
class UpdateProfileParam:
    profile: dict[str, str | int]


@bp.route('/update_profile', ['POST'])
@validate(json=UpdateProfileParam)
@wish_response
@wish_checker(['user_login'])
async def update_profile(req: Request, body: UpdateProfileParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None

    if worker.game_nocheck.is_game_end():
        return response_message('GAME_END', status='error')

    delta = time.time() - user.model.updated_at / 1000
    if not secret.DEBUG_MODE and delta < 3:
        return response_message('RATE_LIMIT', status='error', seconds=3 - delta)

    if 'nickname' not in body.profile:
        return response_message('INVALID_PARAM_MISSING_NICKNAME', status='error')

    if body.profile['nickname'] == '':
        return response_message('INVALID_PARAM_EMPTY_NICKNAME', status='error')

    rep = await worker.perform_action(
        glitter.UserUpdateProfileReq(
            client=worker.process_name,
            uid=user.model.id,
            profile={'nickname': body.profile['nickname']},  # TODO: fix type
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    store_user_log(req, 'api.user.update_profile', 'update_profile', '', {'profile': body.profile})  # type: ignore

    return {}


class ChangePasswordParam(BaseModel):
    old_password: str = Field(description='队伍名称')
    new_password: str = Field(description='队伍简介')


@bp.route('/change_password', ['POST'])
@validate(json=ChangePasswordParam)
@wish_response
@wish_checker(['user_login'])
async def change_password(req: Request, body: ChangePasswordParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None

    if user.model.login_properties.type == 'manual':
        return response_message('INVALID_OPERATION_CHANGE_PASSWORD', status='error')

    assert user.model.login_properties.type == 'email'

    salt = user.model.login_properties.salt
    jwt_salt = utils.gen_random_str(4, crypto=True)
    cur_password_md5 = user.model.login_properties.cur_password
    next_password_md5 = user.model.login_properties.next_password

    input_password_md5 = utils.calc_md5(body.old_password + salt)

    if input_password_md5 != cur_password_md5 and input_password_md5 != next_password_md5:
        return response_message('WRONG_PASSWORD', status='error')

    new_password_md5 = utils.calc_md5(body.new_password + salt)

    rep = await worker.perform_action(
        glitter.UserResetReq(
            client=worker.process_name,
            login_key=user.model.login_key,
            login_properties={
                'salt': salt,
                'jwt_salt': jwt_salt,
                'cur_password': new_password_md5,
                'next_password': '',
                'cnt': '0',
                'type': 'email',
            },
            group=user.model.group,
        )
    )

    if rep.result is not None:
        return response_message('REDUCER_ERROR', status='error', error=rep.result)

    store_user_log(req, 'api.user.change_password', 'change_password', '', {})

    return {}
