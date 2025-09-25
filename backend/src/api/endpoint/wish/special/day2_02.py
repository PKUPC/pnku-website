import time

from typing import Any

from pydantic import BaseModel
from sanic import Request
from sanic_ext import validate

from src import utils
from src.api.endpoint.wish import wish_checker, wish_response
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User

from . import bp


class ChangeTimeParam(BaseModel):
    hour: int
    minute: int


@bp.route('/time_garden', ['POST'])
@validate(json=ChangeTimeParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def time_garden(req: Request, body: ChangeTimeParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if not user.is_staff:
        if 'day2_02' not in user.team.game_state.unlock_puzzle_keys:
            store_user_log(
                req,
                'api.special.day2_02',
                'abnormal',
                '试图在 day2_02 解锁前调用对应接口。',
                {'hour': body.hour, 'minute': body.minute},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '非法操作！'}

    if body.hour < 0 or body.hour > 23 or body.minute < 0 or body.minute > 59:
        store_user_log(
            req,
            'api.special.day2_02',
            'abnormal',
            '给接口发送了非法的时间。',
            {'hour': body.hour, 'minute': body.minute},
        )
        return {'status': 'error', 'title': 'ABNORMAL', 'message': f'{body.hour}:{body.minute} 是一个非法时间！'}

    store_user_log(req, 'api.special.day2_02', 'time_garden', '', {'hour': body.hour, 'minute': body.minute})

    rep = await worker.perform_action(
        glitter.PuzzleActionReq(
            client=worker.process_name,
            user_id=user.model.id,
            team_id=user.team.model.id,
            puzzle_key='day2_02',
            content={'real_seconds': int(time.time()), 'target_seconds': (body.hour * 60 + body.minute) * 60},
        )
    )
    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    return {
        'status': 'success',
        'title': '成功',
        'message': '花园的时间被改变了！',
        'need_reload_info': True,
    }
