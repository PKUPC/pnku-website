import logging
import sys


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
