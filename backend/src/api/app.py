import asyncio
import logging
import os
import time

from typing import Any, Optional

import httpx

from sanic import Blueprint, HTTPResponse, Sanic, response
from sanic.exceptions import SanicException
from sanic.request import Request
from sanic_ext.exceptions import ValidationError

from .. import secret, utils
from ..logic import Worker
from ..state import User
from . import get_cur_user


utils.fix_zmq_asyncio_windows()

app = Sanic('pnku3-backend')
app.config.DEBUG = secret.SANIC_DEBUG
app.config.OAS = False
app.config.PROXIES_COUNT = 1
app.config.KEEP_ALIVE_TIMEOUT = 15
app.config.REQUEST_MAX_SIZE = 1024 * 1024 * (1 + secret.REQUEST_MAX_SIZE_MB)


def get_http_client(_req: Request) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        http2=True,
        mounts=secret.OAUTH_HTTP_MOUNTS,
        timeout=secret.OAUTH_HTTP_TIMEOUT,
    )


def get_worker(req: Request) -> Worker:
    return req.app.ctx.worker  # type: ignore[no-any-return]


app.ext.add_dependency(Worker, get_worker)
app.ext.add_dependency(httpx.AsyncClient, get_http_client)
app.ext.add_dependency(User | None, get_cur_user)


@app.before_server_start
async def setup_game_state(cur_app: Sanic, _loop: Any) -> None:  # type:ignore[type-arg]
    worker_name = cur_app.config.get('GS_WORKER_NAME', f'worker-{os.getpid()}')
    worker = Worker(worker_name, receiving_messages=True)
    cur_app.ctx.worker = worker
    await worker._before_run()
    cur_app.ctx._worker_task = asyncio.create_task(worker._mainloop())
    cur_app.ctx.startup_finished = time.time()


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


app.error_handler.add(Exception, handle_error)

from .endpoint import archive, auth, media, sybil, template, wish, ws


app.blueprint(media.bp)
svc = Blueprint.group(auth.bp, wish.bp, template.bp, ws.bp, sybil.bp, archive.bp, url_prefix='/service')
app.blueprint(svc)


def start(idx0: int, worker_name: str) -> None:
    app.config.GS_WORKER_NAME = worker_name

    formatter = logging.Formatter(
        f'[%(asctime)s] [{worker_name}] [%(levelname)s] [Sanic] %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z'
    )
    logging_handlers = utils.make_logging_handlers(formatter)
    sanic_logger = logging.getLogger('sanic.root')
    sanic_logger.setLevel(logging.INFO)
    for handler in sanic_logger.handlers[:]:
        sanic_logger.removeHandler(handler)
    for handler in logging_handlers:
        sanic_logger.addHandler(handler)

    app.run(**secret.WORKER_API_SERVER_KWARGS(idx0), workers=1, single_process=True)  # type: ignore[no-untyped-call]
