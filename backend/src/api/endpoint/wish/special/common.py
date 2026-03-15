from typing import Any

from sanic import Request

from src.custom import store_user_log
from src.logic import Worker
from src.state import User


def common_check(req: Request, worker: Worker, user: User, puzzle_key: str, body_str: str) -> dict[str, Any] | None:
    assert user.team is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if not user.is_staff:
        if puzzle_key not in user.team.game_state.unlock_puzzle_keys:
            store_user_log(
                req,
                f'api.special.{puzzle_key}',
                'abnormal',
                f'试图在 {puzzle_key} 解锁前调用对应接口。',
                {'body_str': body_str},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '非法操作！'}

    return None
