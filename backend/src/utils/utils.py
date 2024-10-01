import datetime
import hashlib
import logging
import random
import secrets
import sys
import time
import traceback
from typing import Union, Callable, Any, Type, TypeVar

import pytz

T = TypeVar("T")


def gen_random_str(length: int = 32, *, crypto: bool = False) -> str:
    choice: Callable[[str], str] = secrets.choice if crypto else random.choice  # type: ignore[assignment]
    alphabet = 'qwertyuiopasdfghjkzxcvbnmQWERTYUPASDFGHJKLZXCVBNM23456789'

    return ''.join([choice(alphabet) for _ in range(length)])


def format_timestamp(timestamp_s: Union[float, int]) -> str:
    date = datetime.datetime.fromtimestamp(timestamp_s, pytz.timezone('Asia/Shanghai'))
    t = date.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(timestamp_s, float):
        t += f'.{int((timestamp_s % 1) * 1000):03d}'
    return t


def formatted_ts_to_timestamp(formatted_ts: str) -> int:
    date_obj = datetime.datetime.strptime(formatted_ts, "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(date_obj.timetuple()))
    return ts


def get_traceback(e: Exception) -> str:
    return repr(e) + '\n' + ''.join(traceback.format_exception(type(e), e, e.__traceback__))


def calc_md5(content: str) -> str:
    return hashlib.md5(content.encode(encoding="utf-8")).hexdigest()


def clean_submission(origin: str) -> str:
    rst = ""
    for x in origin:
        if '\u4e00' <= x <= '\u9fff':
            rst += x
        elif '0' <= x <= '9':
            rst += x
        elif 'a' <= x.lower() <= 'z':
            rst += x.upper()
    return rst


def check_string(origin: str) -> bool:
    blacklist = {
        "\u200B", "\u200C", "\u200D", "\u200E", "\u200F",
        "\u202A", "\u202B", "\u202C", "\u202D", "\u202E",
        "\u2060", "\u2061", "\u2062", "\u2063", "\u2064", "\u2065", "\u2066", "\u2067", "\u2068",
        "\u2069", "\u206A", "\u206B", "\u206C", "\u206D", "\u206E", "\u206F"
    }
    for x in origin:
        if x in blacklist:
            return False
    return True


def count_blank_in_string(origin: str) -> int:
    blank_list = {
        "\u0009", "\u0020", "\u00A0", "\u2000", "\u2001", "\u2002", "\u2003", "\u2004", "\u2005", "\u2006", "\u2007",
        "\u2008", "\u2009", "\u200A", "\u202F", "\u205F", "\u3000", "\u200B", "\u200C", "\u200D", "\u2060", "\uFEFF",
    }
    count = 0
    for x in origin:
        if x in blank_list:
            count += 1
    return count


def count_non_blank_in_string(origin: str) -> int:
    return len(origin) - count_blank_in_string(origin)


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


def get_value(d: dict[str, Any], key: str, cls: Type[T]) -> T:
    assert key in d
    value = d[key]
    assert isinstance(value, cls)
    return value
