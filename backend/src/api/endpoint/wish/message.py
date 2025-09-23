from typing import Any, Optional

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import adhoc, secret, utils
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User
from src.store import MessageStore

from . import wish_checker, wish_response


bp: Blueprint = Blueprint('wish-message', url_prefix='/wish/message')


class SendMsgParam(BaseModel):
    team_id: int = Field(description='该对话的team_id')
    type: str = Field(description='消息类型')
    content: str = Field(description='消息内容')


@bp.route('/send_message', ['POST'])
@validate(json=SendMsgParam)
@wish_response
@wish_checker(['player_in_team', 'intro_unlock'])
async def send_message(req: Request, body: SendMsgParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if secret.PLAYGROUND_MODE:
        store_user_log(
            req,
            'api.message.send_message',
            'abnormal',
            '在 playground 模式下发送站内信。',
            {'team_id': body.team_id, 'type': body.type, 'content': body.content},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '在目前的游戏模式下无法使用此操作！'}

    if user.model.user_info.ban_list.ban_message:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if not user.is_staff:
        if user.model.team_id != body.team_id:
            store_user_log(
                req,
                'api.message.send_message',
                'abnormal',
                '提供的队伍 id 不是用户的队伍 id。',
                {'team_id': body.team_id, 'type': body.type, 'content': body.content},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍 id 出错！'}
        elif body.team_id not in worker.game_nocheck.teams.team_by_id:
            store_user_log(
                req,
                'api.message.send_message',
                'abnormal',
                '提供的队伍 id 不存在。',
                {'team_id': body.team_id, 'type': body.type, 'content': body.content},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍id不存在！'}

    if body.type not in MessageStore.CONTENT_TYPE.TYPE_SET:
        store_user_log(
            req,
            'api.message.send_message',
            'abnormal',
            '提供了非法的 content type。',
            {'team_id': body.team_id, 'type': body.type, 'content': body.content},
        )
        return {'status': 'error', 'title': 'WRONG_TYPE', 'message': 'content type 错误'}

    if not (1 <= len(body.content) <= 400):
        store_user_log(
            req,
            'api.message.send_message',
            'abnormal',
            f'消息长度不合法，长度为{len(body.content)}。',
            {'team_id': body.team_id, 'type': body.type, 'content': body.content},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '消息长度错误，消息长度应在1到400之间'}

    if body.team_id == 0:
        store_user_log(
            req,
            'api.message.send_message',
            'abnormal',
            '某个 staff 试图给 staff 队伍发信息。',
            {'team_id': body.team_id, 'type': body.type, 'content': body.content},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不能给 staff 队伍发消息，别捣乱了！'}

    rep = await worker.perform_action(
        glitter.TeamSendMsgReq(
            client=worker.process_name,
            team_id=body.team_id,
            user_id=user.model.id,
            content_type=body.type,
            content=body.content,
            direction=MessageStore.DIRECTION.TO_USER if user.is_staff else MessageStore.DIRECTION.TO_STAFF,
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    return {'status': 'success'}


class ReadMsgParam(BaseModel):
    team_id: int = Field(description='该对话的team_id')
    msg_id: int = Field(description='最后一条已读消息')


@bp.route('/read_message', ['POST'])
@validate(json=ReadMsgParam)
@wish_response
@wish_checker(['player_in_team'])
async def read_message(req: Request, body: ReadMsgParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if user.is_staff:
        store_user_log(
            req,
            'api.message.read_message',
            'abnormal',
            'staff 试图调用这个 API。',
            {'team_id': body.team_id, 'msg_id': body.msg_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': 'staff 不能调这个接口'}

    if user.model.team_id != body.team_id:
        store_user_log(
            req,
            'api.message.read_message',
            'abnormal',
            '用户提交的队伍 id 不是用户自己的队伍 id。',
            {'team_id': body.team_id, 'msg_id': body.msg_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍id出错'}

    rep = await worker.perform_action(
        glitter.TeamReadMsgReq(
            client=worker.process_name,
            team_id=body.team_id,
            msg_id=body.msg_id,
            direction=MessageStore.DIRECTION.TO_USER if user.is_staff else MessageStore.DIRECTION.TO_STAFF,
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    return {}


class GetMsgParam(BaseModel):
    team_id: int = Field(description='要获取哪个team的消息列表')
    start_id: int = Field(description='从哪个消息id开始，如果要获取所有的消息，请设置成0')


@bp.route('/get_message', ['POST'])
@validate(json=GetMsgParam)
@wish_response
@wish_checker(['player_in_team', 'intro_unlock'])
async def get_message(req: Request, body: GetMsgParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if body.start_id < 0:
        store_user_log(
            req,
            'api.message.get_message',
            'abnormal',
            '提供的 start_id 不合法。',
            {'team_id': body.team_id, 'start_id': body.start_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '提供的消息id错误'}

    if not user.is_staff and user.model.team_id != body.team_id:
        store_user_log(
            req,
            'api.message.submit_answer',
            'abnormal',
            '提供的队伍 id 和用户的队伍 id 不一致。',
            {'team_id': body.team_id, 'start_id': body.start_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍id出错'}

    rst = worker.game_nocheck.messages.get_msg_list(body.team_id, body.start_id)

    if rst is None:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '提供的消息id错误'}

    if user.model.group != 'staff':
        rst = [x for x in rst]

    def _wrapped_username(msg: MessageStore) -> str:
        sent_user = worker.game_nocheck.users.user_by_id[msg.user_id]
        if user.is_staff:
            return sent_user.model.user_info.nickname
        elif not sent_user.is_staff:
            return sent_user.model.user_info.nickname
        else:
            return adhoc.STAFF_DISPLAY_NAME

    return {
        'data': [
            {
                'id': msg.id,
                'user_name': _wrapped_username(msg),
                'team_name': worker.game_nocheck.teams.team_by_id[msg.team_id].model.team_name,
                'direction': msg.direction,
                'content_type': msg.content_type,
                'content': utils.pure_render_template(msg.content),
                'timestamp_s': msg.created_at // 1000,
                'player_unread': msg.player_unread,
                'staff_unread': msg.staff_unread,
            }
            for msg in rst
        ]
    }
