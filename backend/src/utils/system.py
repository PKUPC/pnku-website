import asyncio
import os
import time
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Dict, Iterator, Literal, Union

import psutil

LogLevel = Literal['debug', 'wish', 'info', 'warning', 'error', 'critical', 'success']


def get_traceback(e: Exception) -> str:
    return repr(e) + '\n' + ''.join(traceback.format_exception(type(e), e, e.__traceback__))


@contextmanager
def log_slow(logger: Callable[[LogLevel, str, str], None], module: str, func: str, threshold: float = 0.3) \
        -> Iterator[None]:
    t1 = time.monotonic()
    try:
        yield
    finally:
        t2 = time.monotonic()
        if t2 - t1 > threshold:
            logger('warning', module, f'took {t2 - t1:.2f}s to {func}')


@contextmanager
def chdir(wd: Union[str, Path]) -> Iterator[None]:
    cur_dir = os.getcwd()
    try:
        os.chdir(wd)
        yield
    finally:
        os.chdir(cur_dir)


def sys_status() -> Dict[str, Union[int, float]]:
    load_1, load_5, load_15 = psutil.getloadavg()
    vmem = psutil.virtual_memory()
    smem = psutil.swap_memory()
    disk = psutil.disk_usage('/')
    G = 1024 ** 3

    cpu_count = psutil.cpu_count(logical=False)
    return {
        'process': len(psutil.pids()),

        'n_cpu': cpu_count if cpu_count is not None else 0,
        'load_1': load_1,
        'load_5': load_5,
        'load_15': load_15,

        'ram_total': vmem.total / G,
        'ram_used': vmem.used / G,
        'ram_free': vmem.available / G,

        'swap_total': smem.total / G,
        'swap_used': smem.used / G,
        'swap_free': smem.free / G,

        'disk_total': disk.total / G,
        'disk_used': disk.used / G,
        'disk_free': disk.free / G,
    }


def fix_zmq_asyncio_windows() -> None:
    # RuntimeError: Proactor event loop does not implement add_reader family of methods required for zmq.
    # zmq will work with proactor if tornado >= 6.1 can be found.
    # Use `asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())` or install 'tornado>=6.1' to avoid this error.
    try:
        if isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):  # type: ignore  # known
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore  # known
    except AttributeError:
        pass
