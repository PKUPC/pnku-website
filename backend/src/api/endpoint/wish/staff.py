from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import utils
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import Submission, Ticket, User

from . import wish_checker, wish_response


bp: Blueprint = Blueprint('wish-staff', url_prefix='/wish/staff')


@bp.route('/get_game_info', ['POST'])
@wish_response
@wish_checker(['user_is_staff'])
async def get_game_info(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    store_user_log(req, 'api.staff.get_staff_info', 'get_staff_info', '', {})

    return {
        'data': {
            'teams': [
                {
                    'team_id': team.model.id,
                    'team_name': team.model.team_name,
                    'last_msg_ts': worker.game_nocheck.messages.get_last_msg_time_by_team_id(team.model.id),
                    'unread': worker.game_nocheck.messages.get_team_unread(team.model.id),
                }
                for team in worker.game_nocheck.teams.list
            ],
            'puzzles': [
                {
                    'key': puzzle.model.key,
                    'title': puzzle.model.title,
                }
                for puzzle in worker.game_nocheck.puzzles.list
            ],
            'puzzle_status': ['答案正确', '答案错误', '里程碑'],
            'ticket_status': ['进行中', '已关闭'],
            'ticket_num': len(worker.game_nocheck.tickets.list),
            'submission_num': len(worker.game_nocheck.submission_list),
        }
    }


class GetTeamDetailParam(BaseModel):
    team_id: int = Field(description='team id')


@bp.route('/get_team_detail', ['POST'])
@validate(json=GetTeamDetailParam)
@wish_response
@wish_checker(['user_is_staff'])
async def get_team_detail(
    req: Request, body: GetTeamDetailParam, worker: Worker, user: User | None
) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    if body.team_id not in worker.game_nocheck.teams.team_by_id:
        return {'status': 'error', 'title': 'NO_TEAM', 'message': '队伍不存在'}

    team = worker.game_nocheck.teams.team_by_id[body.team_id]

    store_user_log(req, 'api.staff.get_team_detail', 'staff_get_team_detail', '', {})

    # 队伍提交信息
    return {
        'team_id': team.model.id,
        'team_name': team.model.team_name,
        'team_info': team.model.team_info,
        'disp_list': team.get_disp_list(),
        'leader_id': team.model.leader_id,
        'members': [
            {'id': member.model.id, 'nickname': member.model.user_info.nickname, 'avatar_url': member.avatar_url}
            for member in team.leader_and_members_modal
        ],
        'cur_ap': team.cur_ap,
        'ap_change': team.ap_change,
        'ap_change_history': team.get_ap_change_list(),
        'spap_change': team.spap_change,
        'submissions': [
            {
                'idx': idx,
                'puzzle': sub.puzzle.model.title,
                'user_name': sub.user.model.user_info.nickname,
                'origin': sub.store.content,
                'cleaned': sub.cleaned_content,
                'status': sub.status,
                'info': sub.result.info,
                'timestamp_s': int(sub.store.created_at / 1000),
            }
            for idx, sub in enumerate(team.game_status.submissions)
        ][::-1],
        'passed_puzzles': [
            {'title': p.model.title, 'timestamp_s': int(s.store.created_at / 1000)}
            for p, s in team.game_status.passed_puzzles
        ],
        'ban_list': {
            'ban_message_until': team.model.extra_info.ban_list.ban_message_until_ts,
            'ban_manual_hint_until': team.model.extra_info.ban_list.ban_manual_hint_until_ts,
            'ban_recruiting_until': team.model.extra_info.ban_list.ban_recruiting_until_ts,
        },
    }


class VMe50Param(BaseModel):
    team_id: int = Field(description='team id')
    ap_change: int = Field(description='体力值的变动量')
    reason: str = Field(description='变动原因')


@bp.route('/v_me_50', ['POST'])
@validate(json=VMe50Param)
@wish_response
@wish_checker(['user_is_staff'])
async def v_me_50(req: Request, body: VMe50Param, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    if user.model.user_info.ban_list.ban_staff:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if body.team_id == 0:
        store_user_log(
            req,
            'api.staff.v_me_50',
            'abnormal',
            '某个 staff 试图变动 staff 队伍的注意力。',
            {'team_id': body.team_id, 'ap_change': body.ap_change, 'reason': body.reason},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不能改变 staff 队伍的注意力，别捣乱了！'}

    if body.team_id not in worker.game_nocheck.teams.team_by_id:
        return {'status': 'error', 'title': 'NO_TEAM', 'message': '队伍不存在'}
    if body.ap_change == 0:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '体力值变动不能为0'}
    if not (0 < len(body.reason) <= 100):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '更改原因的长度应在1到100之间'}

    rep = await worker.perform_action(
        glitter.VMe50Req(
            client=worker.process_name,
            staff_id=user.model.id,
            team_id=body.team_id,
            ap_change=body.ap_change,
            reason=body.reason,
        )
    )

    store_user_log(
        req,
        'api.staff.v_me_50',
        'staff_v_me_50',
        '',
        {'team_id': body.team_id, 'ap_change': body.ap_change, 'reason': body.reason},
    )

    if rep.result is not None:
        return {'status': 'error', 'title': '出错了！', 'message': rep.result}

    return {'data': 'ok'}


@bp.route('/get_team_list', ['POST'])
@wish_response
@wish_checker(['user_is_staff'])
async def get_team_list_staff(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    store_user_log(req, 'api.staff.get_team_list', 'staff_get_team_list', '', {})

    return {
        'data': [
            {
                'team_id': team.model.id,
                'team_name': team.model.team_name,
                'last_msg_ts': worker.game_nocheck.messages.get_last_msg_time_by_team_id(team.model.id),
                'unread': worker.game_nocheck.messages.get_team_unread(team.model.id),
            }
            for team in worker.game_nocheck.teams.list
        ]
    }


class VMe100Param(BaseModel):
    team_id: int = Field(description='team id')
    spap_change: int = Field(description='体力值的变动量')
    reason: str = Field(description='变动原因')


@bp.route('/v_me_100', ['POST'])
@validate(json=VMe100Param)
@wish_response
@wish_checker(['user_is_staff'])
async def v_me_100(req: Request, body: VMe100Param, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    if user.model.user_info.ban_list.ban_staff:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if body.team_id not in worker.game_nocheck.teams.team_by_id:
        return {'status': 'error', 'title': 'NO_TEAM', 'message': '队伍不存在'}
    if body.spap_change == 0:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '体力值变动不能为0'}
    if not (0 < len(body.reason) <= 100):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '更改原因的长度应在1到100之间'}

    rep = await worker.perform_action(
        glitter.VMe100Req(
            client=worker.process_name,
            staff_id=user.model.id,
            team_id=body.team_id,
            ap_change=body.spap_change,
            reason=body.reason,
        )
    )

    store_user_log(
        req,
        'api.staff.v_me_100',
        'staff_v_me_100',
        '',
        {'team_id': body.team_id, 'spap_change': body.spap_change, 'reason': body.reason},
    )

    if rep.result is not None:
        return {'status': 'error', 'title': '出错了！', 'message': rep.result}

    return {'data': 'ok'}


class GetSubmissionListParam(BaseModel):
    team_id: list[int] | None = Field(None)
    puzzle_key: list[str] | None = Field(None)
    puzzle_status: list[str] | None = Field(None)
    sort_field: Literal['timestamp_s'] | None = Field(None)
    sort_order: Literal['ascend', 'descend'] | None = Field(None)
    start_idx: int
    count: int


@bp.route('/get_submission_list', ['POST'])
@validate(json=GetSubmissionListParam)
@wish_response
@wish_checker(['user_is_staff'])
async def get_submission_list(
    req: Request, body: GetSubmissionListParam, worker: Worker, user: User | None
) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    if body.start_idx < 1:
        return {'status': 'error', 'title': 'BAD', 'message': 'start_idx不能小于1'}
    if body.count < 1 or body.count > 100:
        return {'status': 'error', 'title': 'BAD', 'message': 'count不能小于1或大于100'}

    store_user_log(req, 'api.staff.get_submission_list', 'get_submission_list', '', body.model_dump())

    def _filter(x: Submission) -> bool:
        return (
            (body.team_id is None or x.team.model.id in body.team_id)
            and (body.puzzle_status is None or x.status in body.puzzle_status)
            and (body.puzzle_key is None or x.puzzle.model.key in body.puzzle_key)
        )

    filtered_submissions = [x for x in worker.game_nocheck.submission_list if _filter(x)]
    sorted_submissions = filtered_submissions
    if body.sort_field is not None and body.sort_order is not None:
        if body.sort_field == 'timestamp_s':
            sorted_submissions = sorted(
                filtered_submissions, key=lambda x: x.store.created_at, reverse=(body.sort_order == 'descend')
            )
    else:
        sorted_submissions.reverse()
    return {
        'data': {
            'total_num': len(sorted_submissions),
            'list': [
                {
                    'idx': sub.store.id,
                    'puzzle': sub.puzzle.model.title,
                    'puzzle_key': sub.puzzle.model.key,
                    'team': sub.team.model.team_name,
                    'team_id': sub.team.model.id,
                    'user': sub.user.model.user_info.nickname,
                    'origin': sub.store.content,
                    'cleaned': sub.cleaned_content,
                    'status': sub.status,
                    'info': sub.result.info,
                    'timestamp_s': int(sub.store.created_at / 1000),
                }
                for idx, sub in enumerate(sorted_submissions[body.start_idx - 1 : body.start_idx + body.count - 1])
            ],
        }
    }


class GetTicketListParam(BaseModel):
    team_id: list[int] | None = Field(None)
    status: list[str] | None = Field(None)
    staff_replied: list[bool] | None = Field(None)
    sort_field: Literal['last_message_ts'] | None = Field(None)
    sort_order: Literal['ascend', 'descend'] | None = Field(None)
    start_idx: int
    count: int


@bp.route('/get_tickets', ['POST'])
@validate(json=GetTicketListParam)
@wish_response
@wish_checker(['user_is_staff'])
async def get_tickets(req: Request, body: GetTicketListParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff

    if body.start_idx < 1:
        return {'status': 'error', 'title': 'BAD', 'message': 'start_idx不能小于1'}
    if body.count < 1 or body.count > 100:
        return {'status': 'error', 'title': 'BAD', 'message': 'count不能小于1或大于100'}

    store_user_log(req, 'api.staff.get_tickets', 'get_tickets', '', body.model_dump())

    def _filter(x: Ticket) -> bool:
        return (
            (body.team_id is None or x.team.model.id in body.team_id)
            and (body.status is None or x.status_repr in body.status)
            and (body.staff_replied is None or x.staff_replied in body.staff_replied)
        )

    filtered_tickets = [x for x in worker.game_nocheck.tickets.list if _filter(x)]
    sorted_tickets = filtered_tickets
    if body.sort_order is not None and body.sort_field is not None:
        if body.sort_field == 'last_message_ts':
            sorted_tickets = sorted(
                filtered_tickets, key=lambda x: x.last_message_ts, reverse=(body.sort_order == 'descend')
            )
    else:
        sorted_tickets.reverse()

    list_result = [
        {
            'ticket_id': ticket.model.id,
            'team_id': ticket.team.model.id,
            'team_name': ticket.team.model.team_name,
            'last_message_ts': ticket.last_message_ts,
            'staff_replied': ticket.staff_replied,
            'status': ticket.status_repr,
            'subject': ticket.model.subject,
            'ticket_type': ticket.type_repr,
        }
        for ticket in sorted_tickets[body.start_idx - 1 : body.start_idx + body.count - 1]
    ]
    return {
        'status': 'success',
        'title': 'SUCCESS',
        'message': '完成！',
        'data': {'total_num': len(sorted_tickets), 'list': list_result},
    }


class UpdateExtraTeamInfoParam(BaseModel):
    team_id: int
    type: str = Field(description='类别')
    data: dict[str, Any] = Field(description='数据')


@bp.route('/update_extra_team_info', ['POST'])
@validate(json=UpdateExtraTeamInfoParam)
@wish_response
@wish_checker(['user_is_staff'])
async def update_extra_team_info(
    req: Request, body: UpdateExtraTeamInfoParam, worker: Worker, user: User | None
) -> dict[str, Any]:
    assert user is not None

    if user.model.user_info.ban_list.ban_staff:
        return {'status': 'error', 'title': 'BANNED', 'message': '您已被禁用该功能！'}

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    # if body.type not in TeamStore.EXTRA_INFO_TYPES:
    #     return {"status": "error", "title": "BAD_REQUEST", "message": "类别错误"}

    if body.type != 'ban_list':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不支持的操作。'}

    if body.team_id not in worker.game_nocheck.teams.team_by_id:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍 id 不存在。'}

    extra_data: dict[str, str] = {}
    extra_data['ban_message_until'] = body.data.get('ban_message_until', '2024-01-01 00:00')
    extra_data['ban_manual_hint_until'] = body.data.get('ban_manual_hint_until', '2024-01-01 00:00')
    extra_data['ban_recruiting_until'] = body.data.get('ban_recruiting_until', '2024-01-01 00:00')
    try:
        datetime.strptime(extra_data['ban_message_until'], '%Y-%m-%d %H:%M')
        datetime.strptime(extra_data['ban_manual_hint_until'], '%Y-%m-%d %H:%M')
        datetime.strptime(extra_data['ban_recruiting_until'], '%Y-%m-%d %H:%M')
    except ValueError:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '时间格式错误！'}

    rep = await worker.perform_action(
        glitter.TeamUpdateExtraTeamInfoReq(
            client=worker.process_name,
            # tid 这里应该保证存在
            uid=user.model.id,
            tid=body.team_id,
            info_type=body.type,
            data=extra_data,
        )
    )

    store_user_log(
        req,
        'api.staff.update_extra_team_info',
        'update_extra_team_info',
        '',
        {'type': body.type, 'data': body.data},  # type: ignore
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    return {}
