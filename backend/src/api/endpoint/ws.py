import json

from collections import Counter
from copy import deepcopy
from typing import TYPE_CHECKING

from sanic import Blueprint, Request
from sanic.server.websockets.impl import WebsocketImplProtocol
from websockets.protocol import State

from src import secret
from src.api import get_cur_user
from src.custom import store_user_log
from src.store import AnnouncementStore


if TYPE_CHECKING:
    from src.logic import Worker

bp = Blueprint('ws', url_prefix='/ws')

MAX_DEVICES_PER_USER = 10

online_uids: dict[int, int] = Counter()


@bp.websocket('/push')
async def push(req: Request, ws: WebsocketImplProtocol) -> None:
    if not secret.WS_PUSH_ENABLED:
        await ws.close(code=4337, reason='推送通知已禁用')
        return

    # xxx: cannot use dependency injection in websocket handlers
    # see https://github.com/sanic-org/sanic-ext/issues/61
    worker: Worker = req.app.ctx.worker
    user = get_cur_user(req)
    telemetry = worker.custom_telemetry_data

    worker.log('debug', 'api.ws.push', f'got connection from {user}')

    if user is None:
        await ws.close(code=4337, reason='未登录')
        return

    chk = user.check_play_game()
    if chk is not None:
        await ws.close(code=4337, reason=chk[1])
        return

    if online_uids[user.model.id] >= MAX_DEVICES_PER_USER:
        await ws.close(code=4337, reason='同时在线设备过多')
        return

    online_uids[user.model.id] += 1
    store_user_log(req, 'ws', 'ws_online', '', {})

    telemetry['ws_online_uids'] = len(online_uids)
    telemetry['ws_online_clients'] = sum(online_uids.values())

    try:
        message_id = worker.next_message_id

        while True:
            async with worker.message_cond:
                await worker.message_cond.wait_for(lambda: message_id < worker.next_message_id)
                if ws.ws_proto.state in [State.CLOSED, State.CLOSING]:
                    return

                while message_id < worker.next_message_id:
                    msg = worker.ws_messages.get(message_id, None)
                    message_id += 1

                    if msg is None or msg.get('type', None) is None:
                        continue

                    msg_type = msg.get('type')
                    payload = deepcopy(msg['payload'])

                    match msg_type:
                        case 'normal':
                            to_groups: list[str] | None = msg.get('to_groups', None)
                            to_users: list[int] | None = msg.get('to_users', None)

                            if to_groups is None or user.model.group in to_groups:
                                if to_users is None or user.model.id in to_users:
                                    store_user_log(req, 'ws.send', 'type_normal', '', payload)
                                    await ws.send(json.dumps(payload))
                        case 'new_announcement':
                            category = msg['category']
                            # 用户当前能看到这个类别的公告才推送
                            if user.is_staff:
                                store_user_log(req, 'ws.send', 'type_new_announcement', '', payload)
                                await ws.send(json.dumps(payload))
                            else:
                                if category == AnnouncementStore.Category.GENERAL.name:
                                    store_user_log(req, 'ws.send', 'type_new_announcement', '', payload)
                                    await ws.send(json.dumps(payload))
                                else:
                                    if (
                                        user.team is not None
                                        and worker.game_nocheck.is_game_begin()
                                        and category in user.team.game_status.unlock_announcement_categories
                                    ):
                                        store_user_log(req, 'ws.send', 'type_new_announcement', '', payload)
                                        await ws.send(json.dumps(payload))
                        case 'first_blood':
                            pass

    finally:
        worker.log('debug', 'api.ws.push', f'disconnected from {user}')
        store_user_log(req, 'ws', 'ws_offline', '', {})
        online_uids[user.model.id] -= 1
        if online_uids[user.model.id] == 0:
            del online_uids[user.model.id]

        telemetry['ws_online_uids'] = len(online_uids)
        telemetry['ws_online_clients'] = sum(online_uids.values())
