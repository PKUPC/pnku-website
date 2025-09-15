from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING, Literal

import httpx


if TYPE_CHECKING:
    from . import utils

###
# 功能设置
###

# 开启后会启用手动自由登陆模式，以及一些其他的功能
DEBUG_MODE = True
# 只有在 DEBUG_MODE 开启时有效，开启此选项后可以自由访问后台，不会检查是否为 admin 用户
DEBUG_WITH_FREE_ADMIN = True
# playground 模式会关闭站内信、神谕等互动功能，用于赛后开放一个可以游玩的环境
PLAYGROUND_MODE = False
# 是否开启 RECAPTCHA
USE_RECAPTCHA = False
# 队伍人数限制
TEAM_MAX_MEMBER = 5
# 使用邮箱注册
EMAIL_AUTH_ENABLE = True
# 使用 sso 注册（目前一直没有使用过）
SSO_AUTH_ENABLE = False
# 使用 websocket 推送
WS_PUSH_ENABLED = True
# 启用存档 api，用于导出存档用的 json 数据
USE_ARCHIVE_API = False
# 是否重新 hash media 文件名
HASH_MEDIA_FILENAME = False
# puzzle_key hash 方法 "none": 不 hash, "key_only": 只 hash puzzle_key, "key_and_team": hash team_id + puzzle_key
HASH_PUZZLE_KEY: Literal['none', 'key_only', 'key_and_team'] = 'none'
# 性能警报设置
HEALTH_CHECK_THROTTLE = {
    'ram_throttle': 0.2,  # 剩余空间小于此比例报警
    'disk_throttle': 0.1,  # 剩余空间小于此比例报警
    'cpu_throttle': 2 / 3,  # 占用率大于此比例报警（已考虑多核情况）
}


# 根据 userid 直接判断是否是 admin，并不在游戏数据库中判断
def IS_ADMIN(user_id: int) -> bool:
    ADMIN_UIDS = [1]
    return user_id in ADMIN_UIDS


# JWT 相关设置
JWT_ALGO = 'HS256'
JWT_HEADERS = {'alg': 'HS256', 'typ': 'JWT'}
JWT_SALT = 'xxx'
JWT_DEFAULT_TIMEOUT = 6 * 60 * 60  # 单位秒

###
# 密钥设置
###

# 飞书群中的简单推送机器人的推送地址
# 参见 https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
FEISHU_WEBHOOK_ADDR = 'https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx'

# 一些随机字符串

ADMIN_SESSION_SECRET = 'xxx'
GLITTER_SSRF_TOKEN = 'xxx'
ADMIN_2FA_COOKIE = 'xxx'
MEDIA_HASH_SALT = 'xxx'
PUZZLE_KEY_HASH_SALT = 'xxx'

###
# 部署设置
###

# 数据库连接字符串
DB_CONNECTOR = 'mysql+pymysql://username:password@host:port/database?charset=utf8mb4'

# 各种文件的存储路径
BASE_PATH = '/path/to/base'
TEMPLATE_PATH = pathlib.Path(BASE_PATH + '/templates').resolve()
UPLOAD_PATH = pathlib.Path(BASE_PATH + '/upload').resolve()  # 用户上传文件的文件夹
MEDIA_PATH = pathlib.Path(BASE_PATH + '/media').resolve()  # 原始 MEDIA 文件
EXPORT_MEDIA_PATH = pathlib.Path(BASE_PATH + '/m').resolve()  # 对外暴露的 MEDIA，对文件名做了哈希，自动生成
SYBIL_LOG_PATH = pathlib.Path(BASE_PATH + '/sybil_log').resolve()
EXTRA_DATA_PATH = pathlib.Path(BASE_PATH + '/extra').resolve()

# windows 上的 pyzmq 可能用不了 ipc，在 windows 上开发时可以使用 tcp
# GLITTER_ACTION_SOCKET_ADDR = 'tcp://localhost:10000'
# GLITTER_EVENT_SOCKET_ADDR = 'tcp://localhost:10001'
GLITTER_ACTION_SOCKET_ADDR = 'ipc://action.sock'
GLITTER_EVENT_SOCKET_ADDR = 'ipc://event.sock'

# worker 数量
N_WORKERS = 1

SANIC_DEBUG = DEBUG_MODE
WORKER_API_SERVER_KWARGS = lambda idx0: {  # will be passed to `Sanic.run` # noqa: E731
    'host': '127.0.0.1',
    'port': 10010 + idx0,
    'debug': False,
    'access_log': False,  # nginx already does this. disabling sanic access log makes it faster.
}

# flask admin 的端口
REDUCER_ADMIN_SERVER_ADDR = ('127.0.0.1', 10009)

# email 设置
EMAIL_TESTER = 'tester@email.com'
EMAIL_SENDER = 'user@email.com'
EMAIL_USERNAME = 'username'
EMAIL_PASSWORD = 'password'
EMAIL_HOSTNAME = 'smtp.email.com'
EMAIL_PORT = 25
EMAIL_TIMEOUT = 3
EMAIL_USE_TLS = False

# oauth 超时时间
OAUTH_HTTP_TIMEOUT = 20

# 玩家的 request 的大小设置，这是在 sanic 中设置的，如果用了 nginx 等工具，还需要设置 nginx 中的限制
REQUEST_MAX_SIZE_MB = 20

STDOUT_LOG_LEVEL: list[utils.LogLevel] = ['debug', 'wish', 'info', 'success']
STDERR_LOG_LEVEL: list[utils.LogLevel] = ['warning', 'error', 'critical']
DB_LOG_LEVEL: list[utils.LogLevel] = ['info', 'warning', 'error', 'critical', 'success']
PUSH_LOG_LEVEL: list[utils.LogLevel] = ['warning', 'error', 'critical']

# URLS

ADMIN_URL = '/megumi'  # flask admin 的前缀

# recaptcha

RE_CAPTCHA_SECRET = 'xxx'
RE_CAPTCHA_VERIFY_ADDR = 'https://recaptcha.net/recaptcha/api/siteverify'

# OAUTH 设置（目前没有启用）

FRONTEND_PORTAL_URL = '/'  # redirected to this after (successful or failed) login
FRONTEND_AUTH_ERROR_URL = '/login/error'
BACKEND_HOSTNAME = 'localhost'  # used for oauth redirects
BACKEND_SCHEME = 'http'  # used for oauth redirects

OAUTH_HTTP_MOUNTS: dict[str, httpx.AsyncBaseTransport | None] = {
    # will be passed to `httpx.AsyncClient`, see https://www.python-httpx.org/advanced/transports/#routing
    'all://*github.com': None,  # httpx.AsyncHTTPTransport(proxy='http://127.0.0.1:7890'),
}


def BUILD_OAUTH_CALLBACK_URL(url: str) -> str:
    return url  # change this if you want to rewrite the oauth callback url


###
# 用户设置
###

MANUAL_AUTH_ENABLED = DEBUG_MODE  # 是否允许手动创建用户
# 为某些账号设置固定密码而不是随机密码，在开发阶段可能会方便一些
# 只有当 MANUAL_AUTH_ENABLED 启用时才会启用（即 DEBUG 模式）
MANUAL_PASSWORDS: dict[str, str] = {'user@email.com': 'password'}

EMAIL_REG_PERMISSION = False  # 是否使用邮箱限制，开启后只允许白名单内的邮箱注册
VALID_EMAILS: set[str] = set()  # 邮箱白名单
