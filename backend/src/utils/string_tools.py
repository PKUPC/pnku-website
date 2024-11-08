import datetime
import random
import secrets
import time
from typing import Callable, Union

import pytz


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
