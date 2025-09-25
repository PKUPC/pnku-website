"""
队伍相关的 api
"""

import time

from typing import Any

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import adhoc, secret, utils
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User
from src.store import TeamStore

from . import wish_checker, wish_response


bp: Blueprint = Blueprint('wish-team', url_prefix='/wish/team')


class CreateTeamParam(BaseModel):
    team_name: str = Field(description='队伍名称')
    team_info: str = Field(description='队伍简介')
    team_secret: str = Field(description='队伍邀请口令')


@bp.route('/create_team', ['POST'])
@validate(json=CreateTeamParam)
@wish_response
@wish_checker(['user_login'])
async def create_team(req: Request, body: CreateTeamParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}
    # 以下可以直接判断
    if not (0 < len(body.team_name) <= 20):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍名称长度应该在1到20之间'}
    if not (0 <= len(body.team_info) <= 200):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍简介长度应该在0到200之间'}
    if not (10 <= len(body.team_secret) <= 20):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍邀请码长度应该在10到20之间'}
    if not utils.check_string(body.team_name):
        return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名包含非法 unicode 控制符，请不要做奇怪的尝试'}
    if not utils.check_string(body.team_info):
        return {
            'status': 'error',
            'title': 'BAD_NAME',
            'message': '队伍简介包含非法 unicode 控制符，请不要做奇怪的尝试',
        }
    if not (2 <= utils.count_non_blank_in_string(body.team_name)):
        return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名应至少包含2个非空白字符'}
    # 以下状态可能会变，还需要再 reducer 中检查
    if user.model.team_id is not None:
        return {'status': 'error', 'title': 'IN_TEAM', 'message': '你已经在队伍中'}
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员不能组队'}
    if body.team_name in worker._game.teams.team_name_set:
        return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名不能和现存队伍名重复'}

    rep = await worker.perform_action(
        glitter.UserCreateTeamReq(
            client=worker.process_name,
            uid=user.model.id,
            team_name=body.team_name,
            team_info=body.team_info,
            team_secret=body.team_secret,
        )
    )

    store_user_log(
        req,
        'api.team.create_team',
        'create_team',
        '',
        {'team_name': body.team_name, 'team_info': body.team_info, 'team_secret': body.team_secret},
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    assert user.team is not None
    assert user.team.leader is user
    assert user.team.model.leader_id == user.model.id
    assert user.team.model.id == user.model.team_id
    # worker.log("debug", "api.team.create_team", f"{user} create team {user.team}")
    # worker.log("debug", "api.team.create_team", f"{user.team}'s leader is {user.team.leader}")
    # worker.log("debug", "api.team.create_team", f"{user.team}'s members is {user.team.members}")

    return {}


class UpdateTeamInfoParam(BaseModel):
    team_name: str = Field(description='队伍名称')
    team_info: str = Field(description='队伍简介')
    team_secret: str = Field(description='队伍邀请口令')


@bp.route('/update_team', ['POST'])
@validate(json=UpdateTeamInfoParam)
@wish_response
@wish_checker(['player_in_team'])
async def update_team(req: Request, body: UpdateTeamInfoParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if not (0 < len(body.team_name) <= 20):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍名称长度应该在1到20之间'}
    if not (0 <= len(body.team_info) <= 200):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍简介长度应该在0到200之间'}
    if not (10 <= len(body.team_secret) <= 20):
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍邀请码长度应该在10到20之间'}
    if not utils.check_string(body.team_name):
        return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名包含非法 unicode 控制符，请不要做奇怪的尝试'}
    if not utils.check_string(body.team_info):
        return {
            'status': 'error',
            'title': 'BAD_NAME',
            'message': '队伍简介包含非法 unicode 控制符，请不要做奇怪的尝试',
        }
    if not (2 <= utils.count_non_blank_in_string(body.team_name)):
        return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名应至少包含2个非空白字符'}
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员不能更改队伍信息！'}

    # 以下状态需要在 reducer 中检查
    assert user.team is not None
    # 如果已经在队里，必须要是队长
    if user.team.model.leader_id != user.model.id:
        store_user_log(
            req,
            'api.team.update_team',
            'abnormal',
            '非队长试图更改信息。',
            {'team_name': body.team_name, 'team_info': body.team_info, 'team_secret': body.team_secret},
        )
        return {'status': 'error', 'title': 'NO_PERMISSION', 'message': '你不是队长，没有权限更改队伍信息'}
    # 游戏开始后禁止修改
    if user.team.gaming and body.team_name != user.team.model.team_name:
        return {
            'status': 'error',
            'title': 'BAD_REQUEST',
            'message': '在开始游戏后禁止修改队伍名称，如有需要请联系工作人员。',
        }
    # 队伍名不能和现存队伍名重复
    if body.team_name != user.team.model.team_name and body.team_name in worker.game_nocheck.teams.team_name_set:
        return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名不能和现存队伍名重复'}
    # 以上状态需要在 reducer 中检查

    rep = await worker.perform_action(
        glitter.TeamUpdateInfoReq(
            client=worker.process_name,
            uid=user.model.id,
            tid=user.team.model.id,
            team_name=body.team_name,
            team_info=body.team_info,
            team_secret=body.team_secret,
        )
    )

    store_user_log(
        req,
        'api.team.update_team',
        'update_team',
        '',
        {'team_name': body.team_name, 'team_info': body.team_info, 'team_secret': body.team_secret},
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    # worker.log("debug", "api.team.update_team", f"update {user.team} info")

    return {}


class UpdateExtraTeamInfoParam(BaseModel):
    type: str = Field(description='类别')
    data: dict[str, Any] = Field(description='数据')


@bp.route('/update_extra_team_info', ['POST'])
@validate(json=UpdateExtraTeamInfoParam)
@wish_response
@wish_checker(['player_in_team'])
async def update_extra_team_info(
    req: Request, body: UpdateExtraTeamInfoParam, worker: Worker, user: User | None
) -> dict[str, Any]:
    assert user is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if body.type not in TeamStore.EXTRA_INFO_TYPES:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '类别错误'}

    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员不能更改队伍信息！'}

    # 以下状态需要在 reducer 中检查
    assert user.team is not None
    # 如果已经在队里，必须要是队长
    if user.team.model.leader_id != user.model.id:
        store_user_log(
            req,
            'api.team.update_extra_team_info',
            'abnormal',
            '非队长试图更改信息。',
            {'type': body.type, 'data': body.data},  # type: ignore
        )
        return {'status': 'error', 'title': 'NO_PERMISSION', 'message': '你不是队长，没有权限更改队伍信息'}
    # 以上状态需要在 reducer 中检查

    if body.type == 'recruitment':
        if 'recruiting' not in body.data or not isinstance(body.data.get('recruiting', None), bool):
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '缺少参数 recruiting'}
        if 'recruiting_contact' not in body.data or not isinstance(body.data.get('recruiting_contact', None), str):
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '缺少参数 recruiting_contact'}
        # 如果要保证一定不能改的话，需要在 reducer 中也检查，但是没必要
        if user.team.model.extra_info.ban_list.ban_recruiting_until_ts > time.time():
            store_user_log(
                req,
                'api.team.update_extra_team_info',
                'abnormal',
                '被禁止使用招募的队伍试图修改招募信息。',
                {'type': body.type, 'data': body.data},  # type: ignore
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你的队伍被禁止发送站内信！'}

    rep = await worker.perform_action(
        glitter.TeamUpdateExtraTeamInfoReq(
            client=worker.process_name,
            # tid 这里应该保证存在
            uid=user.model.id,
            tid=user.team.model.id,
            info_type=body.type,
            data=body.data,
        )
    )

    store_user_log(
        req,
        'api.team.update_extra_team_info',
        'update_extra_team_info',
        '',
        {'type': body.type, 'data': body.data},  # type: ignore
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    # worker.log("debug", "api.team.update_team", f"update {user.team} info")

    return {}


class JoinTeamParam(BaseModel):
    team_id: int = Field(description='队伍id')
    team_secret: str = Field(description='队伍邀请口令')


@bp.route('/join_team', ['POST'])
@validate(json=JoinTeamParam)
@wish_response
@wish_checker(['user_login'])
async def join_team(req: Request, body: JoinTeamParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert worker.game is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    # 检查队伍是否存在，不能加入 staff 队伍
    if body.team_id not in worker.game.teams.team_by_id or body.team_id == 0:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的队伍'}
    target_team = worker.game.teams.team_by_id[body.team_id]
    # 如果队伍已经封禁，则禁止加入队伍
    if target_team.model.ban_status == TeamStore.BanStatus.BANNED.name:
        return {'status': 'error', 'title': 'BAD_TEAM', 'message': '队伍已封禁，禁止加入。'}
    # 检查是否已经在队伍里
    if user.team is not None:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你已经在队伍里'}
    # 检查队伍人数限制
    if len(target_team.members) == secret.TEAM_MAX_MEMBER:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍人数达到上限'}
    # 检查 secret
    if target_team.model.team_secret != body.team_secret:
        return {'status': 'error', 'title': 'WRONG_SECRET', 'message': '队伍邀请码错误'}
    if body.team_id == 0:
        store_user_log(
            req,
            'api.team.join_team',
            'abnormal',
            '试图加入非法队伍！',
            {'team_id': body.team_id, 'team_secret': body.team_secret},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '试图加入非法队伍！'}

    rep = await worker.perform_action(
        glitter.UserJoinTeamReq(
            client=worker.process_name, tid=body.team_id, uid=user.model.id, team_secret=body.team_secret
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    store_user_log(
        req, 'api.team.join_team', 'join_team', '', {'team_id': body.team_id, 'team_secret': body.team_secret}
    )

    # worker.log("debug", "api.team.join_team", f"{user} join {user.team}")

    return {}


@bp.route('/leave_team', ['POST'])
@wish_response
@wish_checker(['player_in_team'])
async def leave_team(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if user.team.gaming:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍已经在游戏中，你现在不能离开队伍'}

    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员不能离开队伍！'}

    team_id: int | None = user.model.team_id
    assert team_id is not None

    rep = await worker.perform_action(
        glitter.UserLeaveTeamReq(
            client=worker.process_name,
            tid=team_id,
            uid=user.model.id,
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    store_user_log(req, 'api.team.leave_team', 'leave_team', '', {})

    # worker.log("debug", "api.team.leave_team", f"{user} leave team(T#{team_id})")

    return {}


class RemoveUserParam(BaseModel):
    user_id: int = Field(description='要移除的用户的id')


@bp.route('/remove_user', ['POST'])
@validate(json=RemoveUserParam)
@wish_response
@wish_checker(['player_in_team'])
async def remove_user(req: Request, body: RemoveUserParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if user.team.leader is not user:
        return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不是队长'}
    if body.user_id not in [x.model.id for x in user.team.members]:
        return {'status': 'error', 'title': 'USER_NOT_FOUND', 'message': '要删除的用户不在队伍中'}
    if user.team.gaming:
        return {'status': 'error', 'title': 'TEAM_LOCK', 'message': '队伍已经在游戏中，现在不能移除队伍成员'}
    if user.model.id == body.user_id:
        return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不能移除你自己'}
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员队伍不能移除队员！'}

    team_id: int | None = user.model.team_id
    assert team_id is not None

    rep = await worker.perform_action(
        glitter.TeamRemoveUserReq(client=worker.process_name, from_id=user.model.id, tid=team_id, uid=body.user_id)
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    store_user_log(req, 'api.team.remove_user', 'remove_user', '', {'user_id': body.user_id})

    return {}


class ChangeLeaderParam(BaseModel):
    user_id: int = Field(description='要转移给的用户id')


@bp.route('/change_leader', ['POST'])
@validate(json=ChangeLeaderParam)
@wish_response
@wish_checker(['player_in_team'])
async def change_leader(req: Request, body: ChangeLeaderParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None
    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if user.team.leader is not user:
        return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不是队长'}
    if body.user_id not in [x.model.id for x in user.team.members]:
        return {'status': 'error', 'title': 'USER_NOT_FOUND', 'message': '目标用户不在队伍中'}
    if user.model.id == body.user_id:
        return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不能转移给你自己'}
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员队伍不能转移队长！'}

    assert user.model.team_id is not None
    rep = await worker.perform_action(
        glitter.TeamChangeLeaderReq(
            client=worker.process_name, from_id=user.model.id, tid=user.model.team_id, uid=body.user_id
        )
    )

    if rep.result is not None:
        return utils.unpack_rep(rep.result)

    store_user_log(req, 'api.team.change_leader', 'change_leader', '', {'user_id': body.user_id})

    return {}


@bp.route('/get_ap_change_history', ['POST'])
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_ap_change_history(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'NOT_IMPLEMENT', 'message': 'staff 暂时无法调用这个接口'}
    assert user.team is not None
    res = {'history': user.team.get_ap_change_list()}

    store_user_log(req, 'api.team.get_ap_change_history', 'get_ap_change_history', '', {})

    return res


@bp.route('/get_submission_history', ['POST'])
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_submission_history(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'NOT_IMPLEMENT', 'message': 'staff 暂时无法调用这个接口'}
    assert user.team is not None
    res = {
        'data': {
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
                for idx, sub in enumerate(user.team.game_state.submissions)
            ][::-1],
            'passed_submissions': [
                {
                    'timestamp_s': int(sub.store.created_at / 1000),
                    'gained_score': sub.gained_score(),
                    # "finished": sub.finished,
                }
                for sub in user.team.game_state.success_submissions
            ],
        }
    }

    store_user_log(req, 'api.team.get_submission_history', 'get_submission_history', '', {})

    return res


@bp.route('/get_puzzle_statistics', ['POST'])
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_puzzle_statistics(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    if user.model.group == 'staff':
        return {'status': 'error', 'title': 'NOT_IMPLEMENT', 'message': 'staff 暂时无法调用这个接口'}
    assert user.team is not None

    area_list = ['day1', 'day2', 'day3']

    res = []
    for area_name in area_list:
        if area_name in user.team.game_state.unlock_areas:
            puzzle_structure = worker.game_nocheck.puzzles.puzzles_by_structure.get(area_name, {})
            res_dict: dict[str, Any] = {'name': adhoc.AREA_NAME.get(area_name, 'NONE'), 'puzzles': []}
            for group in puzzle_structure:
                for puzzle in puzzle_structure[group]:
                    unlock_ts = user.team.game_state.unlock_puzzle_keys.get(puzzle.model.key, -1)
                    if unlock_ts == -1:
                        continue
                    passed_ts: int | None = user.team.game_state.passed_puzzle_keys.get(puzzle.model.key, -1)
                    if passed_ts == -1:
                        passed_ts = None
                    time_cost = None
                    if passed_ts is not None:
                        time_cost = passed_ts - unlock_ts
                    wrong, milestone, correct = 0, 0, 0
                    for sub in user.team.get_submissions_by_puzzle_key(puzzle.model.key):
                        if sub.result.type == 'pass' or sub.result.type == 'multipass':
                            correct += 1
                        elif sub.result.type == 'milestone':
                            milestone += 1
                        elif sub.result.type == 'wrong':
                            wrong += 1
                    res_dict['puzzles'].append(
                        {
                            'key': worker.game_nocheck.hash_puzzle_key(user.team.model.id, puzzle.model.key),
                            'title': puzzle.model.title,
                            'unlock_ts': unlock_ts,
                            'passed_ts': passed_ts,
                            'time_cost': time_cost,
                            'pass': correct,
                            'wrong': wrong,
                            'milestone': milestone,
                        }
                    )
            if len(res_dict['puzzles']) > 0:
                res.append(res_dict)

    store_user_log(req, 'api.team.get_puzzle_statistics', 'get_puzzle_statistics', '', {})

    return {'data': res}
