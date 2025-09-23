import re

from pathlib import Path

from sanic import Blueprint, HTTPResponse, Request, response

from src import secret, utils
from src.custom import store_user_log
from src.logic.worker import Worker
from src.state import User


bp = Blueprint('template', url_prefix='/template')

TEMPLATE_PATH = secret.TEMPLATE_PATH
TEMPLATE_PATH.mkdir(parents=True, exist_ok=True)

TEMPLATE_NAME_RE = re.compile(r'^[a-zA-Z0-9\-_]+$')


def etagged_response(req: Request, etag: str, html_body: str) -> HTTPResponse:
    etag = f'W/"{etag}"'

    req_etag = req.headers.get('If-None-Match', None)
    if req_etag == etag:
        return response.html('', status=304, headers={'ETag': etag})
    else:
        return response.html(html_body, headers={'ETag': etag})


_cache: dict[tuple[str, str | None, int], tuple[int, str]] = {}

PUBLIC_TEMPLATE = ['introduction', 'faq', 'tools', 'endoftime']
if secret.DEBUG_MODE:
    PUBLIC_TEMPLATE.append('dev_log')

# ATTENTION: 目前在序章开放后就将 day1_intro 添加到了 unlock_templates 里面去
# 这里额外做一个限制
TEMPLATE_AFTER_GAME_START = {'day1_intro'}


def check_template_permission(filename: str, worker: Worker, user: User | None) -> bool:
    # 写给 admin 看的信息
    if filename == 'admin_doc':
        return user is not None and secret.IS_ADMIN(user.model.id)

    # 公开的模板始终可以访问
    if filename in PUBLIC_TEMPLATE:
        return True
    # 未登录不能访问
    if user is None:
        return False

    # staff 始终可以访问
    if user.model.group == 'staff':
        return True

    assert user is not None
    # 用户封禁、队伍封禁、未组队不能访问
    if user.team is None or user.team.is_banned:
        return False

    # ADHOC
    # 序章判断

    if filename == 'prologue':
        return worker.game_nocheck.is_intro_unlock()

    # 没到时间不能访问
    if filename in TEMPLATE_AFTER_GAME_START and not worker.game_nocheck.is_game_begin():
        return False

    return filename in user.team.game_status.unlock_templates


def is_safe_path(path: str) -> bool:
    normalized_path = Path(path).resolve()
    return path == str(normalized_path)


@bp.route('/<filename:path>')
async def get_template(req: Request, filename: str, worker: Worker, user: User | None) -> HTTPResponse:
    if worker.game is None:
        return response.text('服务暂时不可用', status=403)

    # 更改了模板检查，在 template 下的文件都能访问，并且支持子文件夹
    p = (TEMPLATE_PATH / f'{filename}.md').resolve()

    if not p.is_relative_to(TEMPLATE_PATH):
        store_user_log(req, 'api.get_template', 'abnormal', '试图访问危险路径！', {'template': filename})
        return response.text('?!', status=403)

    if not p.is_file():
        return response.text('没有这个模板', status=404)

    # 鉴权
    if not check_template_permission(filename, worker, user):
        return response.text('没有这个模板', status=404)

    ts = int(p.stat().st_mtime * 1000)

    store_user_log(req, 'api.get_template', 'get_template', '', {'template': filename})

    group = None if user is None else user.model.group
    tick = worker.game.cur_tick
    cache_key = (filename, group, tick)

    cache = _cache.get(cache_key, None)
    if cache is not None and cache[0] == ts:
        return etagged_response(req, str(ts), cache[1])
    else:
        worker.log('debug', 'api.template.get_template', f'rendering and caching {cache_key}')
        with p.open('r', encoding='utf-8') as f:
            md = f.read()

        try:
            html = utils.render_template(md, {'group': group, 'tick': tick})
        except Exception as e:
            worker.log(
                'error', 'api.template.get_template', f'template render failed: {filename}: {utils.get_traceback(e)}'
            )
            return response.text('<i>（模板渲染失败）</i>')

        _cache[cache_key] = (ts, html)
        return etagged_response(req, str(ts), html)
