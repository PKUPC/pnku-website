import time
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sanic import Request
from sanic_ext import validate

from src import utils
from src.custom import store_user_log
from src.api.endpoint.wish import wish_response, wish_checker
from src.logic import Worker
from src.state import User
from src.utils.simple_frequency_limit import get_last_visit, set_last_visit
from . import bp

DATE_LIST = [
    "1900-01-01", "1970-01-01", "2000-01-01", "2000-03-26", "2001-03-25", "2002-03-24", "2003-03-23",
    "2004-02-29", "2005-02-27", "2006-03-05", "2007-02-25", "2008-02-24", "2009-02-22", "2010-03-07",
    "2011-02-27", "2012-02-26", "2013-02-24", "2014-03-02", "2015-02-22", "2016-01-01", "2016-02-28",
    "2016-10-13", "2017-02-26", "2017-10-05", "2018-03-04", "2018-10-10", "2019-02-24", "2019-10-10",
    "2020-02-09", "2020-10-08", "2021-04-25", "2021-10-07", "2022-02-01", "2022-03-27", "2022-09-08",
    "2022-10-06", "2023-01-22", "2023-03-12", "2023-10-05", "2024-01-01", "2024-02-10", "2024-03-10",
    "2024-06-01", "2024-07-01", "2024-07-11", "2024-07-12", "2024-07-13", "2024-07-14", "2024-07-15",
    "2024-07-16", "2024-07-17", "2024-07-18", "2024-07-19", "2024-07-20", "2024-07-21", "2024-07-22",
    "2024-07-23", "2024-07-24", "2024-07-25", "2024-08-01", "2024-09-02", "2025-01-01", "2025-01-29"
]


def is_valid_date(year: int, month: int, day: int) -> bool:
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False


class TimeMachineParam(BaseModel):
    year: int
    month: int
    day: int


@bp.route("/time_machine", ["POST"])
@validate(json=TimeMachineParam)
@wish_response
@wish_checker(["player_in_team", "game_start"])
async def time_machine(req: Request, body: TimeMachineParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if not user.is_staff:
        if not user.team.gaming:
            store_user_log(
                req, "api.special.day2_05", "abnormal", "试图在游戏开始前调用 API。",
                {"year": body.year, "month": body.month, "day": body.day}
            )
            return {"status": "error", "title": "ABNORMAL", "message": "非法操作！"}
        if "day2_05" not in user.team.game_status.unlock_puzzle_keys:
            store_user_log(
                req, "api.special.day2_05", "abnormal", "试图在 day2_05 解锁前调用对应接口。",
                {"year": body.year, "month": body.month, "day": body.day}
            )
            return {"status": "error", "title": "ABNORMAL", "message": "非法操作！"}

    if not is_valid_date(body.year, body.month, body.day):
        store_user_log(
            req, "api.special.day2_05", "abnormal", "发送了不合法的日期。",
            {"year": body.year, "month": body.month, "day": body.day}
        )
        return {
            "status": "error", "title": "BAD_REQUEST",
            "message": "不合法的日期！请选择 1900-01-01 到 2099-12-31 中的合法日期。"
        }
    if body.year < 1900 or body.year > 2099:
        store_user_log(
            req, "api.special.day2_05", "abnormal", "发送了不合法的日期。",
            {"year": body.year, "month": body.month, "day": body.day}
        )
        return {
            "status": "error", "title": "BAD_REQUEST",
            "message": "不合法的日期！请选择 1900-01-01 到 2099-12-31 中的合法日期。"
        }

    current_ms = time.time()
    last_visit = get_last_visit((user.model.id, "day2_05"))
    ms_diff = current_ms - last_visit
    if ms_diff < 3:
        return {
            "status": "error", "title": "FREQUENCY_LIMIT",
            "message": f"请求太快啦！请{3 - ms_diff:.1f} 秒后重试"
        }

    store_user_log(
        req, "api.special.day2_05", "time_machine", "",
        {"year": body.year, "month": body.month, "day": body.day}
    )

    set_last_visit((user.model.id, "day2_05"), current_ms)

    target_year, target_month, target_day = body.year, body.month, body.day
    date_str = f"{target_year}-{target_month:0>2}-{target_day:0>2}"
    target_date = DATE_LIST[0]
    for x in DATE_LIST:
        if date_str >= x:
            target_date = x

    return {
        "status": "success",
        "title": "成功！",
        "message": "你来到了新的一天！（也许是旧的？）",
        "data": utils.media_wrapper(f"puzzle/day2_05/{target_date}.webp")
    }
