import re

from dataclasses import dataclass
from typing import Any

import email_validator

from pydantic import BaseModel, Field
from sanic import Blueprint, HTTPResponse, Request, response
from sanic_ext import validate

from src import secret, utils
from src.custom import store_user_log
from src.logic import Worker
from src.state import User

from ..auth import AuthError, AuthResponse, auth_response


bp = Blueprint('auth', url_prefix='/auth')


@bp.route('/logout')
async def auth_logout(req: Request) -> HTTPResponse:
    store_user_log(req, 'auth.logout', 'logout', '', {})
    res = response.redirect(secret.FRONTEND_PORTAL_URL)
    res.delete_cookie('user_token')
    res.delete_cookie('auth_token')
    res.delete_cookie('admin_2fa', path=secret.ADMIN_URL)

    return res


class AuthManualParam(BaseModel):
    identity: str = Field(description='用户名', examples=['winfrid'])


@bp.route('/manual', ['POST'])
@validate(json=AuthManualParam)
@auth_response
async def auth_manual(_req: Request, body: AuthManualParam, _worker: Worker) -> AuthResponse:
    if not secret.MANUAL_AUTH_ENABLED:
        raise AuthError('手动登录已禁用')
    if body.identity == '':
        raise AuthError('不允许空的identity')

    return f'manual:{body.identity.lower()}', {'type': 'manual'}, 'manual'


async def check_captcha(req: Request, _worker: Worker, data: dict[str, Any]) -> bool:
    if secret.USE_CAPTCHA == 'recaptcha':
        response = data.get('response', '')
        if response is None or response == '':
            raise AuthError('请进行人机身份验证')
        return await utils.check_recaptcha_response(data['response'])
    elif secret.USE_CAPTCHA == 'aliyun':
        response = data.get('response', '')
        if response is None or response == '':
            raise AuthError('请进行人机身份验证')
        return await utils.check_aliyun_captcha_response(response)
    else:
        return True


class AuthEmailRegParam(BaseModel):
    email: str = Field(description='邮箱', examples=['user@email.com'])
    captcha: dict[str, Any] = Field(description='captcha 服务所需的数据')


@bp.route('/email/register', ['POST'])
@validate(json=AuthEmailRegParam)
@auth_response
async def auth_email_reg(req: Request, body: AuthEmailRegParam, worker: Worker) -> AuthResponse:
    if not secret.EMAIL_AUTH_ENABLE:
        raise AuthError('邮箱登录已禁用')

    if (
        secret.USE_CAPTCHA != 'none'
        and body.email.lower() not in worker.game_nocheck.policy.cur_policy_model.skip_recaptcha_emails
    ):
        worker.log('info', 'auth.email.register', f'email: {body.email}, captcha: {body.captcha}')
        if not (await check_captcha(req, worker, body.captcha)):
            raise AuthError('人机身份验证错误')

    try:
        email_validator.validate_email(body.email, check_deliverability=False)
    except email_validator.EmailNotValidError:
        raise AuthError('非法的邮箱地址')
    VAL_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    if not VAL_EMAIL.match(body.email):
        raise AuthError('邮箱格式错误')

    return f'{body.email.lower()}', {}, 'register'


class AuthEmailLoginParam(BaseModel):
    email: str = Field(description='邮箱', examples=['user@email.com'])
    password: str = Field(description='密码')
    captcha: dict[str, Any] = Field(description='captcha 服务所需的数据')


@bp.route('/email/login', ['POST'])
@validate(json=AuthEmailLoginParam)
@auth_response
async def auth_email_login(req: Request, body: AuthEmailLoginParam, worker: Worker) -> AuthResponse:
    if not secret.EMAIL_AUTH_ENABLE:
        raise AuthError('邮箱登录已禁用')
    try:
        email_validator.validate_email(body.email, check_deliverability=False)
    except email_validator.EmailNotValidError:
        raise AuthError('非法的邮箱地址')
    VAL_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    if not VAL_EMAIL.match(body.email):
        raise AuthError('邮箱格式错误')

    if (
        secret.USE_CAPTCHA != 'none'
        and body.email.lower() not in worker.game_nocheck.policy.cur_policy_model.skip_recaptcha_emails
    ):
        worker.log('info', 'auth.email.register', f'email: {body.email}, captcha: {body.captcha}')
        if not (await check_captcha(req, worker, body.captcha)):
            raise AuthError('人机身份验证错误')

    return f'email:{body.email.lower()}', {'password': body.password}, 'email-login'


@dataclass
class AuthSuParam:
    uid: int


@bp.route('/su', ['POST'])
@validate(json=AuthSuParam)
@auth_response
async def auth_su(_req: Request, body: AuthSuParam, worker: Worker, user: User | None) -> AuthResponse:
    if user is None or not secret.IS_ADMIN(user.model.id):
        raise AuthError('没有权限')
    if worker.game is None:
        raise AuthError('服务繁忙，请稍后再试！')

    su_user = worker.game.users.user_by_id.get(body.uid, None)
    if su_user is None:
        raise AuthError('用户不存在')
    if secret.IS_ADMIN(su_user.model.id):
        raise AuthError('不能切换到管理员账号')

    return su_user
