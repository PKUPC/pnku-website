from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from sanic import Request
from sanic.server.websockets.impl import WebsocketImplProtocol

from src.api import get_cur_user
from src.custom import store_user_log
from src.sync.core.sync_integration import SyncIntegration

from ..sync import bp


if TYPE_CHECKING:
    from src.logic import Worker
    from src.state import User


MAX_DEVICES_PER_USER = 10

online_uids: dict[int, int] = Counter()


def check(req: Request, user: User | None, worker: Worker, puzzle_key: str) -> tuple[bool, str]:
    """
    返回 (True, real_puzzle_key) 或者 (False, error_message)
    """
    if user is None:
        return False, '未登录'
    if user.team is None:
        store_user_log(
            req, 'sync.puzzle', 'abnormal', '用户未组队', {'puzzle_key': puzzle_key, 'user_id': user.model.id}
        )
        return False, '用户未组队'

    team_id, real_puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, puzzle_key)

    # 找不到原始 puzzle_key
    if real_puzzle_key is None:
        store_user_log(
            req,
            'sync.puzzle',
            'abnormal',
            '找不到原始 puzzle_key。',
            {'puzzle_key': puzzle_key, 'user_id': user.model.id},
        )
        return False, '谜题不存在！'

    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'sync.puzzle',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': puzzle_key, 'real_puzzle_key': real_puzzle_key, 'another_team_id': team_id},
        )
        return False, '谜题不存在！'

    # 此时 puzzle_key 一定是存在的，检查解锁状态

    puzzle = worker.game_nocheck.puzzles.puzzle_by_key[real_puzzle_key]

    # 是否是启用了 sync 功能的谜题
    if not puzzle.model.puzzle_metadata.use_sync:
        store_user_log(
            req,
            'sync.puzzle',
            'abnormal',
            '谜题未启用 sync 功能。',
            {'puzzle_key': real_puzzle_key, 'user_id': user.model.id},
        )
        return False, '谜题未启用 sync 功能！'

    # 检查解锁状态
    if not user.is_staff and real_puzzle_key not in user.team.game_state.unlock_puzzle_keys:
        store_user_log(
            req,
            'sync.puzzle',
            'abnormal',
            '题目未解锁。',
            {'body_puzzle_key': puzzle_key, 'real_puzzle_key': real_puzzle_key},
        )
        return False, '谜题不存在！'

    return True, real_puzzle_key


@bp.websocket('/puzzle/<puzzle_key:str>')  # type: ignore[misc]
async def puzzle(req: Request, ws: WebsocketImplProtocol, puzzle_key: str) -> None:
    worker: Worker = req.app.ctx.worker
    sync_integration: SyncIntegration = req.app.ctx.sync_integration
    user = get_cur_user(req)
    telemetry = worker.custom_telemetry_data

    worker.log('debug', 'sync.puzzle', f'got connection from {user}, begin checking!')

    valid, data = check(req, user, worker, puzzle_key)
    if not valid:
        worker.log(
            'debug', 'sync.puzzle', f'check failed for user {user}, puzzle {puzzle_key}, closing connection: {data}'
        )
        await ws.close(code=4337, reason=data)
        return

    assert user is not None
    assert user.team is not None

    if online_uids[user.model.id] >= MAX_DEVICES_PER_USER:
        await ws.close(code=4396, reason='您同时在线的协作题目过多，本页面无法连接协作服务器！')
        return

    online_uids[user.model.id] += 1

    telemetry['ws_online_uids'] = len(online_uids)
    telemetry['ws_online_clients'] = sum(online_uids.values())

    puzzle_key = data

    worker.log('debug', 'sync.puzzle', f'got connection from {user} for puzzle {puzzle_key}')
    store_user_log(
        req, 'sync.puzzle', 'sync_websocket_connected', '', {'puzzle_key': puzzle_key, 'user_id': user.model.id}
    )

    room_id = f'puzzle:{puzzle_key}:team:{user.team.model.id}'
    puzzle_state = user.team.game_state.puzzle_state_by_key[puzzle_key]
    custom_sync_handler = puzzle_state.get_custom_sync_handler()
    custom_sync_doc_initializer = puzzle_state.get_custom_sync_doc_initializer()
    custom_sync_observer_maker = puzzle_state.get_custom_sync_observer_maker()

    if custom_sync_handler is not None:
        worker.log('debug', 'sync.puzzle', f'using custom sync handler for puzzle {puzzle_key}')

    try:
        await sync_integration.handle_sync_websocket(
            ws,
            user,
            room_id,
            custom_handler=custom_sync_handler,
            doc_initializer=custom_sync_doc_initializer,
            observer_maker=custom_sync_observer_maker,
            extra={
                'user': user,
                'puzzle_key': puzzle_key,
            },
        )
    except Exception as e:
        worker.log('error', 'sync.puzzle', f'websocket handler error: {e}')
    finally:
        worker.log('debug', 'sync.puzzle', f'websocket handler finished for {user}, puzzle {puzzle_key}')
        store_user_log(
            req, 'sync.puzzle', 'sync_websocket_disconnected', '', {'puzzle_key': puzzle_key, 'user_id': user.model.id}
        )
        online_uids[user.model.id] -= 1
        if online_uids[user.model.id] == 0:
            del online_uids[user.model.id]

        telemetry['ws_online_uids'] = len(online_uids)
        telemetry['ws_online_clients'] = sum(online_uids.values())
