import re

from dataclasses import dataclass

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


class AuthEmailRegParam(BaseModel):
    email: str = Field(description='邮箱', examples=['user@email.com'])
    captcha: str = Field(description='reCAPTCHA返回的token')


@bp.route('/email/register', ['POST'])
@validate(json=AuthEmailRegParam)
@auth_response
async def auth_email_reg(_req: Request, body: AuthEmailRegParam, _worker: Worker) -> AuthResponse:
    if not secret.EMAIL_AUTH_ENABLE:
        raise AuthError('邮箱登录已禁用')
    try:
        email_validator.validate_email(body.email, check_deliverability=False)
    except email_validator.EmailNotValidError:
        raise AuthError('非法的邮箱地址')
    if secret.USE_RECAPTCHA and not (await utils.check_recaptcha_response(body.captcha)):
        raise AuthError('reCAPTCHA验证错误')
    VAL_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    if not VAL_EMAIL.match(body.email):
        raise AuthError('邮箱格式错误')
    if secret.EMAIL_REG_PERMISSION:
        if body.email.lower() not in secret.VALID_EMAILS:
            raise AuthError('注册限制已启用，该邮箱禁止注册')
    # print(body.email.lower())
    # print(str(body.email.lower()))

    return f'{body.email.lower()}', {}, 'register'


class AuthEmailLoginParam(BaseModel):
    email: str = Field(description='邮箱', examples=['user@email.com'])
    password: str = Field(description='密码')
    captcha: str = Field(description='reCAPTCHA返回的token')


@bp.route('/email/login', ['POST'])
@validate(json=AuthEmailLoginParam)
@auth_response
async def auth_email_login(_req: Request, body: AuthEmailLoginParam, _worker: Worker) -> AuthResponse:
    if not secret.EMAIL_AUTH_ENABLE:
        raise AuthError('邮箱登录已禁用')
    try:
        email_validator.validate_email(body.email, check_deliverability=False)
    except email_validator.EmailNotValidError:
        raise AuthError('非法的邮箱地址')
    VAL_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    if not VAL_EMAIL.match(body.email):
        raise AuthError('邮箱格式错误')
    if secret.USE_RECAPTCHA and not (await utils.check_recaptcha_response(body.captcha)):
        raise AuthError('reCAPTCHA验证错误')
    return f'email:{body.email.lower()}', {'password': body.password}, 'email-login'


@dataclass
class AuthSuParam:
    uid: int


@bp.route('/su', ['POST'])
@validate(query=AuthSuParam)
@auth_response
async def auth_su(_req: Request, query: AuthSuParam, worker: Worker, user: User | None) -> AuthResponse:
    if user is None or not secret.IS_ADMIN(user.model.id):
        raise AuthError('没有权限')
    if worker.game is None:
        raise AuthError('服务暂时不可用')

    su_user = worker.game.users.user_by_id.get(query.uid, None)
    if su_user is None:
        raise AuthError('用户不存在')
    if secret.IS_ADMIN(su_user.model.id):
        raise AuthError('不能切换到管理员账号')

    return su_user
