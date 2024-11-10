import time

from typing import Any, Optional

from pydantic import BaseModel
from sanic import Blueprint, Request
from sanic_ext import validate

from src import adhoc, secret, utils
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User
from src.store import ManualHintModel, TicketMessageStore, TicketStore

from . import wish_checker, wish_response


bp = Blueprint('wish-ticket', url_prefix='/wish/ticket')


class RequestHintParam(BaseModel):
    puzzle_key: str
    content: str


@bp.route('/request_hint', ['POST'])
@validate(json=RequestHintParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def request_hint(req: Request, body: RequestHintParam, worker: Worker, user: Optional[User]) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if secret.PLAYGROUND_MODE:
        store_user_log(
            req,
            'api.ticket.request_hint',
            'abnormal',
            '在 playground 模式下申请神谕。',
            {'body_puzzle_key': body.puzzle_key, 'content': body.content},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '在目前的游戏模式下无法使用此操作！'}

    if user.model.user_info.ban_list.ban_ticket:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if user.is_staff:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': 'staff 不支持该请求。'}

    if not (1 <= len(body.content) <= 400):
        return {'status': 'error', 'title': 'ABNORMAL', 'message': '提问内容的长度应当在1到400字之间。'}

    # 如果要保证一定不能改的话，需要在 reducer 中也检查，但是没必要
    if user.team.model.extra_info.ban_list.ban_manual_hint_until_ts > time.time():
        store_user_log(
            req,
            'api.ticket.request_hint',
            'abnormal',
            '被禁止使用神谕的队伍试图申请神谕。',
            {'body_puzzle_key': body.puzzle_key},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你的队伍被禁止发送站内信！'}

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req, 'api.ticket.request_hint', 'abnormal', 'unhash puzzle_key 失败。', {'body_puzzle_key': body.puzzle_key}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.ticket.request_hint',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if puzzle_key not in user.team.game_status.unlock_puzzle_keys:
        store_user_log(req, 'api.ticket.request_hint', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    subject = '『请求神谕』' + worker.game_nocheck.puzzles.puzzle_by_key[puzzle_key].model.title

    rep = await worker.perform_action(
        glitter.TeamCreateTicketReq(
            client=worker.process_name,
            user_id=user.model.id,
            team_id=user.team.model.id,
            ticket_type=TicketStore.TicketType.MANUAL_HINT.name,
            subject=subject,
            first_message=body.content,
            extra={
                'type': TicketStore.TicketType.MANUAL_HINT.name,
                'puzzle_key': puzzle_key,
            },
        )
    )
    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    store_user_log(req, 'api.ticket.request_hint', 'request_hint', '', {'puzzle_key': puzzle_key})

    return {'status': 'success', 'title': 'SUCCESS', 'message': '完成！'}


class GetHintListParam(BaseModel):
    puzzle_key: str


@bp.route('/get_manual_hints', ['POST'])
@validate(json=GetHintListParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_manual_hints(
    req: Request, body: GetHintListParam, worker: Worker, user: Optional[User]
) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if user.is_staff:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': 'staff 不支持该请求。'}

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req,
            'api.ticket.get_manual_hints',
            'abnormal',
            'unhash puzzle_key 失败。',
            {'body_puzzle_key': body.puzzle_key},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.ticket.get_manual_hints',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if puzzle_key not in user.team.game_status.unlock_puzzle_keys:
        store_user_log(req, 'api.ticket.get_manual_hints', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    hint_list: list[dict[str, Any]] = []
    for ticket in worker.game_nocheck.tickets.tickets_by_team_id.get(user.team.model.id, []):
        if not isinstance(ticket.model.extra, ManualHintModel) or ticket.model.extra.puzzle_key != puzzle_key:
            continue
        hint_list.append(
            {
                'ticket_id': ticket.model.id,
                'last_message_ts': ticket.last_message_ts,
                'staff_replied': ticket.staff_replied,
                'status': ticket.status_repr,
                'subject': ticket.model.subject,
            }
        )
    rst: dict[str, Any] = {'list': hint_list}

    effective_after_ts = user.team.game_status.unlock_puzzle_keys[puzzle_key] + adhoc.MANUAL_HINT_COOLDOWN
    rst['effective_after_ts'] = effective_after_ts
    # 先判断现在是否能申请神谕
    if effective_after_ts > time.time():
        rst['disabled'] = True
        rst['disabled_reason'] = '题目解锁 2 个小时后才能申请神谕。'
    else:
        ticket_list = worker.game_nocheck.tickets.get_tickets_by_team_id_and_type_and_status(
            user.team.model.id, TicketStore.TicketType.MANUAL_HINT.name, TicketStore.TicketStatus.OPEN.name
        )
        if len(ticket_list) > 0:
            rst['disabled'] = True
            rst['disabled_reason'] = '你和芈雨还有未完成的神谕请求，现在不能发起新请求。'
            puzzle_list = []
            for ticket in ticket_list:
                assert ticket.model.extra.type == 'MANUAL_HINT'
                puzzle_list.append(worker.game_nocheck.puzzles.puzzle_by_key[ticket.model.extra.puzzle_key].model.title)

            rst['hints_open'] = puzzle_list

    return {'status': 'success', 'title': 'SUCCESS', 'message': '完成！', 'data': rst}


class GetTicketDetailParam(BaseModel):
    ticket_id: int


@bp.route('/get_ticket_detail', ['POST'])
@validate(json=GetTicketDetailParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_ticket_detail(
    req: Request, body: GetTicketDetailParam, worker: Worker, user: Optional[User]
) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    ticket = worker.game_nocheck.tickets.ticket_by_id.get(body.ticket_id, None)
    if ticket is None:
        store_user_log(
            req, 'api.ticket.get_ticket_detail', 'abnormal', '访问了不存在的工单。', {'ticket_id': body.ticket_id}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的数据！'}
    if not user.is_staff and user.team.model.id != ticket.team.model.id:
        store_user_log(
            req,
            'api.ticket.get_ticket_detail',
            'abnormal',
            '试图访问不属于自己队伍的工单。',
            {'ticket_id': body.ticket_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的数据！'}

    store_user_log(req, 'api.ticket.get_ticket_detail', 'get_ticket_detail', '', {'ticket_id': body.ticket_id})

    def _wrapped_username(msg: TicketMessageStore) -> str:
        sent_user = worker.game_nocheck.users.user_by_id[msg.user_id]
        if user.is_staff:
            return sent_user.model.user_info.nickname
        elif not sent_user.is_staff:
            return sent_user.model.user_info.nickname
        else:
            return adhoc.STAFF_DISPLAY_NAME

    messages = [
        {
            'id': msg.id,
            'user_name': _wrapped_username(msg),
            'team_name': ticket.team.model.team_name,
            'direction': msg.direction,
            'content': utils.pure_render_template(msg.content),
            'timestamp_s': msg.created_at // 1000,
        }
        for msg in ticket.message_list
    ]

    rst: dict[str, Any] = {
        'ticket_id': ticket.model.id,
        'subject': ticket.model.subject,
        'ticket_status': ticket.model.status,
        'staff_replied': ticket.staff_replied,
        'messages': messages,
    }

    # 如果这是一个人工提示，并且管理员还没回复，并且是玩家请求信息，则状态为 disable
    if ticket.model.type == TicketStore.TicketType.MANUAL_HINT.name and not ticket.staff_replied and not user.is_staff:
        rst['disabled'] = True
        rst['disabled_reason'] = '芈雨还没有回复你的请求，你暂时无法和芈雨继续交流。'
    # 如果已关闭
    if ticket.model.status == TicketStore.TicketStatus.CLOSED.name:
        rst['disabled'] = True
        rst['disabled_reason'] = '该会话已关闭，你无法再发送新的信息。'

    return {'status': 'success', 'title': 'SUCCESS', 'message': '完成！', 'data': rst}


class SendMessageParam(BaseModel):
    ticket_id: int
    content: str


@bp.route('/send_message', ['POST'])
@validate(json=SendMessageParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def send_message(req: Request, body: SendMessageParam, worker: Worker, user: Optional[User]) -> dict[str, Any]:
    assert user is not None
    assert worker.game is not None
    assert user.team is not None

    if secret.PLAYGROUND_MODE:
        store_user_log(
            req,
            'api.ticket.send_message',
            'abnormal',
            '在 playground 模式下发送神谕消息。',
            {'ticket_id': body.ticket_id, 'content': body.content},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '在目前的游戏模式下无法使用此操作！'}

    if user.model.user_info.ban_list.ban_ticket:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    ticket = worker.game_nocheck.tickets.ticket_by_id.get(body.ticket_id, None)
    if ticket is None:
        store_user_log(
            req, 'api.ticket.send_message', 'abnormal', '给不存在的工单发送消息。', {'ticket_id': body.ticket_id}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的数据！'}
    if not user.is_staff and user.team.model.id != ticket.team.model.id:
        store_user_log(
            req,
            'api.ticket.send_message',
            'abnormal',
            '给不属于自己队伍的工单发送消息。',
            {'ticket_id': body.ticket_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的数据！'}

    if not (1 <= len(body.content) <= 400):
        store_user_log(req, 'api.ticket.send_message', 'abnormal', '消息长度不合法。', {'content': body.content[:200]})
        return {'status': 'error', 'title': 'ABNORMAL', 'message': '提问内容的长度应当在1到400字之间。'}

    store_user_log(req, 'api.ticket.send_message', 'send_ticket_message', '', {'ticket_id': body.ticket_id})

    direction = (
        TicketMessageStore.Direction.TO_PLAYER.name if user.is_staff else TicketMessageStore.Direction.TO_STAFF.name
    )

    rep = await worker.perform_action(
        glitter.TicketMessageReq(
            client=worker.process_name,
            user_id=user.model.id,
            ticket_id=ticket.model.id,
            content_type=TicketMessageStore.ContentType.TEXT.name,
            content=body.content,
            direction=direction,
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    return {'status': 'success', 'title': 'SUCCESS', 'message': '发送成功！'}


class SetTicketStatusParam(BaseModel):
    ticket_id: int
    ticket_status: str


@bp.route('/set_ticket_status', ['POST'])
@validate(json=SetTicketStatusParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def set_ticket_status(
    req: Request, body: SetTicketStatusParam, worker: Worker, user: Optional[User]
) -> dict[str, Any]:
    assert user is not None
    assert worker.game is not None
    assert user.team is not None

    if secret.PLAYGROUND_MODE:
        store_user_log(
            req,
            'api.ticket.set_ticket_status',
            'abnormal',
            '在 playground 模式下设置神谕状态。',
            {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '在目前的游戏模式下无法使用此操作！'}

    if user.model.user_info.ban_list.ban_ticket:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if not user.is_staff:
        store_user_log(
            req,
            'api.ticket.set_ticket_status',
            'abnormal',
            '玩家试图改变神谕状态。',
            {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你无法使用这个操作！'}

    if body.ticket_status not in ['OPEN', 'CLOSED']:
        store_user_log(
            req,
            'api.ticket.set_ticket_status',
            'abnormal',
            '不存在的状态。',
            {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status},
        )

    ticket = worker.game_nocheck.tickets.ticket_by_id.get(body.ticket_id, None)
    if ticket is None:
        store_user_log(
            req,
            'api.ticket.set_ticket_status',
            'abnormal',
            '给不存在的工单设置状态。',
            {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的数据！'}
    if not user.is_staff and user.team.model.id != ticket.team.model.id:
        store_user_log(
            req,
            'api.ticket.set_ticket_status',
            'abnormal',
            '给不属于自己队伍的工单设置状态。',
            {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的数据！'}

    # 用户只能关闭，不能打开
    if not user.is_staff and body.ticket_status == 'OPEN':
        store_user_log(
            req,
            'api.ticket.set_ticket_status',
            'abnormal',
            '玩家试图重新打开工单。',
            {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你不能重新打开工单！异常行为已记录！'}

    store_user_log(
        req, 'api.ticket.set_ticket_status', '', '', {'ticket_id': body.ticket_id, 'ticket_status': body.ticket_status}
    )

    rep = await worker.perform_action(
        glitter.SetTicketStatusReq(
            client=worker.process_name,
            user_id=user.model.id,
            ticket_id=ticket.model.id,
            status=body.ticket_status,  # type: ignore
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    return {'status': 'success', 'title': 'SUCCESS', 'message': '发送成功！'}
