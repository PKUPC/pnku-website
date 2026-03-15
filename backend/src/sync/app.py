import asyncio
import logging
import os
import time

from typing import Any

import httpx

from sanic import Blueprint, Sanic
from sanic.request import Request

from src.api.utils import get_cur_user, get_http_client, handle_error

from .. import secret, utils
from ..logic import Worker
from ..state import User
from .core.leveldb_store import LevelDBStore
from .core.room_manager import RoomManager
from .core.sync_integration import SyncIntegration


utils.fix_zmq_asyncio_windows()

app = Sanic('pnku-website-backend-syncer')
app.config.DEBUG = secret.SANIC_DEBUG
app.config.OAS = False
app.config.PROXIES_COUNT = 1
app.config.KEEP_ALIVE_TIMEOUT = 15
app.config.REQUEST_MAX_SIZE = 1024 * 1024 * (1 + secret.REQUEST_MAX_SIZE_MB)


def get_worker(req: Request) -> Worker:
    return req.app.ctx.worker  # type: ignore[no-any-return]


app.ext.add_dependency(Worker, get_worker)
app.ext.add_dependency(httpx.AsyncClient, get_http_client)
app.ext.add_dependency(User | None, get_cur_user)


@app.before_server_start
async def setup_game_state(cur_app: Sanic, _loop: Any) -> None:  # type:ignore[type-arg]
    worker_name = cur_app.config.get('GS_WORKER_NAME', f'syncer-{os.getpid()}')
    worker = Worker(worker_name, receiving_messages=True)
    cur_app.ctx.worker = worker
    await worker._before_run()
    cur_app.ctx._worker_task = asyncio.create_task(worker._mainloop())
    cur_app.ctx.startup_finished = time.time()

    cur_app.ctx.sync_store = LevelDBStore(secret.SYNC_LEVELDB_PATH)
    cur_app.ctx.room_manager = RoomManager(cur_app.ctx.sync_store)
    cur_app.ctx.sync_integration = SyncIntegration(cur_app.ctx.room_manager, cur_app.ctx.worker)


app.error_handler.add(Exception, handle_error)

from . import sync


svc = Blueprint.group(sync.bp, url_prefix='/service')
app.blueprint(svc)


def start(worker_name: str) -> None:
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

    app.run(**secret.SYNCER_KWARGS, workers=1, single_process=True)  # type: ignore[arg-type]
