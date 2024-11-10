from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .data import AREA_LIST


if TYPE_CHECKING:
    from src.logic import Worker
    from src.state import User


def get_unlock_areas_info(user: User | None, worker: Worker) -> list[dict[str, Any]]:
    # 未登录或者封禁玩家
    if user is None:
        return [AREA_LIST[0]]
    # staff
    if user.is_staff:
        return [AREA_LIST[2], AREA_LIST[3], AREA_LIST[4], AREA_LIST[5]]
    # 普通玩家
    assert user.model.group == 'player'
    # 如果序章还没开放
    if not worker.game_nocheck.is_intro_unlock():
        return [AREA_LIST[0]]
    # 序章开放到游戏开始前
    elif not worker.game_nocheck.is_game_begin():
        # 如果没组队则前往组队
        if user.team is None:
            return [AREA_LIST[1]]
        return [AREA_LIST[2]]
    # 游戏开始后
    else:
        # 如果没组队则前往组队
        if user.team is None:
            return [AREA_LIST[1]]

        rst: list[dict[str, Any]] = [AREA_LIST[2]]
        if user.team is not None:
            if 'day1' in user.team.game_status.unlock_areas:
                rst.append(AREA_LIST[3])
            if 'day2' in user.team.game_status.unlock_areas:
                rst.append(AREA_LIST[4])
            if 'day3' in user.team.game_status.unlock_areas:
                rst.append(AREA_LIST[5])
        return rst
