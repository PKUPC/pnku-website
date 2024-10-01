import jwt
import time
from src import secret

from typing import Literal


def jwt_encode(payload: dict[str, str | int], exp: int | None = None) -> str:
    current_time = int(time.time())
    payload["iat"] = current_time
    if exp is None:
        exp = current_time + secret.JWT_DEFAULT_TIMEOUT

    payload["exp"] = exp
    token = jwt.encode(payload=payload, key=secret.JWT_SALT, algorithm=secret.JWT_ALGO, headers=secret.JWT_HEADERS)
    return token


def jwt_decode(token: str) -> tuple[Literal[True], dict[str, str | int]] | tuple[Literal[False], str]:
    try:
        info = jwt.decode(token, secret.JWT_SALT, algorithms=['HS256'], verify=True)
        return True, info
    except jwt.exceptions.ExpiredSignatureError:
        return False, "登录已过期，请重新登录"
    except jwt.exceptions.DecodeError:
        return False, "非法登录信息"
    except jwt.exceptions.InvalidTokenError:
        return False, "非法登录信息"
    except Exception:
        return False, "未知错误，请联系管理员"
