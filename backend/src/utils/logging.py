import logging
import sys
import time

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Literal


LogLevel = Literal['debug', 'wish', 'info', 'warning', 'error', 'critical', 'success']


def make_logging_handlers(formatter: logging.Formatter) -> list[logging.Handler]:
    # 设置stdout处理器，仅输出DEBUG和INFO级别的日志
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)  # 只允许DEBUG和INFO级别的日志通过
    stdout_handler.setFormatter(formatter)

    # 设置stderr处理器，输出WARNING及以上级别的日志
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)  # WARNING, ERROR, CRITICAL
    stderr_handler.setFormatter(formatter)
    return [stdout_handler, stderr_handler]


@contextmanager
def log_slow(
    logger: Callable[[LogLevel, str, str], None], module: str, func: str, threshold: float = 0.3
) -> Iterator[None]:
    t1 = time.monotonic()
    try:
        yield
    finally:
        t2 = time.monotonic()
        if t2 - t1 > threshold:
            logger('warning', module, f'took {t2 - t1:.2f}s to {func}')
