from functools import wraps
from inspect import isawaitable
from typing import Dict, Any, Callable, Tuple, Union, Awaitable
from urllib.parse import quote

import httpx
from sanic import response, Request, HTTPResponse
from sanic.models.handler_types import RouteHandler

from src.custom import store_user_log
from .. import secret
from .. import utils
from ..logic import Worker, glitter
from ..state import User
from ..store import UserStore

LOGIN_MAX_AGE_S = 86400 * 30

AuthResponse = Union[User, Tuple[str, Dict[str, Any], str]]
AuthHandler = Callable[..., Union[AuthResponse, Awaitable[AuthResponse]]]


class AuthError(Exception):
    def __init__(self, message: str):
        self.message: str = message

    def __str__(self) -> str:
        return self.message


def _login(req: Request, worker: Worker, user: User) -> HTTPResponse:
    chk = user.check_login()
    if chk is not None:
        raise AuthError(chk[1])

    store_user_log(req, "auth._login", "login", "", {}, user)

    res = response.redirect(
        secret.FRONTEND_PORTAL_URL
    )
    user.update_cookie(res)
    # 真实的 admin 只在这里加一次（不然 114514 个 warning）
    if secret.IS_ADMIN(user.model.id):
        worker.log('warning', 'auth.login', f'sending admin 2fa cookie to U#{user.model.id}')
        utils.add_cookie(res, 'admin_2fa', secret.ADMIN_2FA_COOKIE, secret.ADMIN_URL, 7 * 24 * 60 * 60)

    res.delete_cookie("oauth_state")
    return res


async def _register_or_login(
        req: Request, worker: Worker, login_key: str, properties: Dict[str, Any],
        group: str) -> HTTPResponse:
    if worker.game is None:
        worker.log('warning', 'api.auth.register_or_login', 'game is not available')
        raise AuthError('服务暂时不可用')
    user = worker.game.users.user_by_login_key.get(login_key)

    if user is None:  # reg new user
        init_info = {}
        if "email" in properties:
            init_info["email"] = properties["email"]
        if "nickname" in properties:
            init_info["nickname"] = properties["nickname"]
        rep = await worker.perform_action(glitter.UserRegReq(
            client=worker.process_name,
            login_key=login_key,
            login_properties=properties,
            init_info=init_info,
            group=group,
        ))
        if rep.result is None:
            user = worker.game.users.user_by_login_key.get(login_key)
            assert user is not None, 'user should be created'
        else:
            raise AuthError(f'注册账户失败：{rep.result}')

    return _login(req, worker, user)


async def _register_or_reset(req: Request, worker: Worker, email: str, properties: Dict[str, Any], group: str) \
        -> HTTPResponse:
    """
        使用邮箱进行注册，注册的时候生成一个随机字符串作为密码
        因为只需要邮箱地址就可以重置密码，为了防止恶意重置（别人的密码？），在用户注册一次之后，应当存储一个 next_password 和 cur_password
        注册账号时，生成的密码存储在 cur_password 中，next_password 设为空
        重设密码时，生成的密码储存在 next_password 中，如果此时 next_password 不为空，会将目前累积的重置次数 + 1
        重设密码后，如果用新密码登录，则将 cur_password 设置为 next_password，将 next_password 设置为空，将累计次数清0
        重设密码时，如果累计次数大于等于3，禁止重设
    """

    if worker.game is None:
        worker.log('warning', 'api.auth.register_with_email', 'game is not available')
        raise AuthError('服务暂时不可用')

    login_key = "email:" + email
    user = worker.game.users.user_by_login_key.get(login_key)

    if user is None:
        salt = utils.gen_random_str(16, crypto=True)
        jwt_salt = utils.gen_random_str(4, crypto=True)
        if secret.MANUAL_AUTH_ENABLED and email in secret.MANUAL_PASSWORDS:
            password = secret.MANUAL_PASSWORDS[email]
        else:
            password = utils.gen_random_str(16, crypto=True)
        password_email_md5 = utils.calc_md5(password + login_key)
        password_md5 = utils.calc_md5(password_email_md5 + salt)

        email_status, info = await utils.send_reg_email(password, email)

        rep = await worker.perform_action(glitter.UserRegReq(
            client=worker.process_name,
            login_key=login_key,
            login_properties={
                "salt": salt,
                "jwt_salt": jwt_salt,
                "cur_password": password_md5,
                "next_password": "",
                "cnt": "0",
                "type": "email",
            },
            init_info={
                "email": email
            },
            group=UserStore.DEFAULT_GROUP,
        ))

        if rep.result is None:
            user = worker.game.users.user_by_login_key.get(login_key)
            assert user is not None, 'user should be created'
            store_user_log(req, "auth._register_or_reset", "register", "", {"init_password": password, "email": email})
        elif not email_status:
            store_user_log(req, "auth._register_or_reset", "register_email_fail", "",
                           {"init_password": password, "email": email})
            raise AuthError(f'重置密码成功，但是邮件发送失败了，请联系工作人员处理！')
        else:
            raise AuthError(f'注册账户失败：{rep.result}')

    else:
        assert user.model.login_properties.type == "email"
        salt = user.model.login_properties.salt
        jwt_salt = utils.gen_random_str(4, crypto=True)
        cur_password_md5 = user.model.login_properties.cur_password
        cur_cnt = int(user.model.login_properties.cnt)
        if cur_cnt >= 3:
            raise AuthError(f'重置密码失败：在使用新密码登陆前，您已经重置了3次密码，如果登陆遇到问题，请联系工作人员。')

        assert salt is not None, 'user should have salt'

        if secret.MANUAL_AUTH_ENABLED and email in secret.MANUAL_PASSWORDS:
            password = secret.MANUAL_PASSWORDS[email]
        else:
            password = utils.gen_random_str(16, crypto=True)
        password_email_md5 = utils.calc_md5(password + login_key)
        password_md5 = utils.calc_md5(password_email_md5 + salt)  # md5 没那么安全，但是也没那么不安全，随机 salt + md5 应该够了
        cur_cnt += 1

        email_status, info = await utils.send_reg_email(password, email)

        rep = await worker.perform_action(glitter.UserResetReq(
            client=worker.process_name,
            login_key=login_key,
            login_properties={
                "salt": salt,
                "jwt_salt": jwt_salt,
                "cur_password": cur_password_md5,
                "next_password": password_md5,
                "cnt": str(cur_cnt),
                "type": "email",
            },
            group=UserStore.DEFAULT_GROUP,
        ))

        if rep.result is None:
            user = worker.game.users.user_by_login_key.get(login_key)
            assert user is not None, 'user should be created'
            store_user_log(req, "auth._register_or_reset", "reset_password", "",
                           {"reset_password": password, "email": email})
        elif not email_status:
            store_user_log(req, "auth._register_or_reset", "register_email_fail", "",
                           {"init_password": password, "email": email})
            raise AuthError(f'重置密码成功，但是邮件发送失败了，请联系工作人员处理！')
        else:
            raise AuthError(f'重置密码失败：{rep.result}')
        pass

    return response.json({"status": "success"})


async def _login_with_email(req: Request, worker: Worker, login_key: str, properties: Dict[str, Any], group: str) \
        -> HTTPResponse:
    if worker.game is None:
        worker.log('warning', 'api.auth.login_with_email', 'game is not available')
        raise AuthError('服务暂时不可用')

    user = worker.game.users.user_by_login_key.get(login_key)

    if user is None:
        raise AuthError('用户不存在，请先注册')
    else:
        assert user.model.login_properties.type == "email"
        salt = user.model.login_properties.salt
        jwt_salt = user.model.login_properties.jwt_salt
        cur_password_md5 = user.model.login_properties.cur_password
        next_password_md5 = user.model.login_properties.next_password
        cur_cnt = int(user.model.login_properties.cnt)

        input_password_md5 = utils.calc_md5(properties["password"] + salt)

        if cur_cnt == 0:
            assert next_password_md5 == ""
            if input_password_md5 != cur_password_md5:
                raise AuthError('密码错误')
        else:
            assert next_password_md5 != ""
            # 如果使用新密码登录，则原密码失效
            if input_password_md5 == next_password_md5:
                rep = await worker.perform_action(glitter.UserResetReq(
                    client=worker.process_name,
                    login_key=login_key,
                    login_properties={
                        "salt": salt,
                        "jwt_salt": jwt_salt,
                        "cur_password": next_password_md5,
                        "next_password": "",
                        "cnt": "0",
                        "type": "email",
                    },
                    group=UserStore.DEFAULT_GROUP,
                ))
                if rep.result is None:
                    user = worker.game.users.user_by_login_key.get(login_key)
                    assert user is not None, 'user should be created'
                else:
                    raise AuthError(f'登陆失败：{rep.result}')
            # 如果也不是旧密码，则密码错误
            elif input_password_md5 != cur_password_md5:
                raise AuthError('密码错误')
        return _login(req, worker, user)


def auth_response(fn: AuthHandler) -> RouteHandler:
    @wraps(fn)
    async def wrapped(req: Request, *args: Any, **kwargs: Any) -> HTTPResponse:
        worker = req.app.ctx.worker
        try:
            try:
                retval_ = fn(req, *args, **kwargs)
                retval = (await retval_) if isawaitable(retval_) else retval_
                if isinstance(retval, User):
                    return _login(req, worker, retval)
                else:
                    # 为了在使用邮箱注册时复用这个逻辑，进行一个特判
                    # 在调用邮箱注册接口或者更改密码接口时:
                    #   - 函数返回的 group == "register"
                    #   - login_key == "xxx@email.com"
                    #   - properties == {}
                    login_key, properties, group = retval
                    if group == "register":
                        return await _register_or_reset(req, worker, login_key, properties, group)
                    elif group == "email-login":
                        return await _login_with_email(req, worker, login_key, properties, group)
                    elif group == "manual":
                        return await _register_or_login(req, worker, login_key, properties, "player")
                    return await _register_or_login(req, worker, login_key, properties, group)
            except httpx.RequestError as e:
                worker.log('warning', 'api.auth.auth_response', f'request error: {utils.get_traceback(e)}')
                raise AuthError('第三方服务网络错误')
        except AuthError as e:
            if secret.FRONTEND_AUTH_ERROR_URL is None:
                return response.json(
                    {
                        "ok": False,
                        "error_msg": e.message
                    },
                    200
                )
            else:
                return response.redirect(secret.FRONTEND_AUTH_ERROR_URL + f"?msg={e.message}")

    return wrapped


def build_url(url: str, query: Dict[str, str]) -> str:
    assert '?' not in url, 'url should not contain query string part'
    query_str = '&'.join(f'{quote(k)}={quote(v)}' for k, v in query.items())
    return f'{url}?{query_str}'


def oauth2_redirect(url: str, params: Dict[str, str], redirect_url: str) -> HTTPResponse:
    assert '://' in redirect_url, 'redirect url should be absolute'

    state = utils.gen_random_str(32)
    res = response.redirect(build_url(url, {
        **params,
        'redirect_uri': redirect_url,
        'state': state,
    }))

    res.add_cookie("oauth_state", state, samesite="Lax", httponly=True, max_age=600)
    return res


def oauth2_check_state(req: Request) -> None:
    state = req.cookies.get('oauth_state', None)
    if not state:
        raise AuthError('OAuth错误：state无效')
    if state != req.args.get('state', None):
        raise AuthError('OAuth错误：state不匹配')
