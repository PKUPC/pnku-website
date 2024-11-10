import time

from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import secret, utils
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User

from . import wish_checker, wish_response


bp = Blueprint('wish-user', url_prefix='/wish/user')


@dataclass
class UpdateProfileParam:
    profile: dict[str, str | int]


@bp.route('/update_profile', ['POST'])
@validate(json=UpdateProfileParam)
@wish_response
@wish_checker(['user_login'])
async def update_profile(
    req: Request, body: UpdateProfileParam, worker: Worker, user: Optional[User]
) -> dict[str, Any]:
    assert user is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    delta = time.time() - user.model.updated_at / 1000
    if not secret.DEBUG_MODE and delta < 3:
        return {'status': 'error', 'title': 'RATE_LIMIT', 'message': f'提交太频繁，请等待 {3 - delta:.1f} 秒'}

    if 'nickname' not in body.profile:
        return {'status': 'error', 'title': 'INVALID_PARAM', 'message': '缺少昵称信息'}
    if body.profile['nickname'] == '':
        return {'status': 'error', 'title': 'INVALID_PARAM', 'message': '昵称不能为空'}

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
async def change_password(
    req: Request, body: ChangePasswordParam, worker: Worker, user: Optional[User]
) -> dict[str, Any]:
    assert user is not None

    if user.model.login_properties.type == 'manual':
        return {'status': 'error', 'title': 'INVALID_OPERATION', 'message': '测试用户不能更改密码'}

    assert user.model.login_properties.type == 'email'

    salt = user.model.login_properties.salt
    jwt_salt = utils.gen_random_str(4, crypto=True)
    cur_password_md5 = user.model.login_properties.cur_password
    next_password_md5 = user.model.login_properties.next_password

    input_password_md5 = utils.calc_md5(body.old_password + salt)

    if input_password_md5 != cur_password_md5 and input_password_md5 != next_password_md5:
        return {'status': 'error', 'title': 'WRONG_PASSWORD', 'message': '原始密码错误'}

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
        return {'status': 'error', 'title': 'REDUCER_ERROR', 'message': rep.result}

    store_user_log(req, 'api.user.change_password', 'change_password', '', {})

    return {}
