from __future__ import annotations

import copy
import time

from typing import TYPE_CHECKING, Any, Dict, Optional

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import adhoc, secret, utils
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User
from src.store import AnnouncementStore

from . import wish_checker, wish_response


if TYPE_CHECKING:
    from src.state import Team

bp = Blueprint('wish-game', url_prefix='/wish/game')

FALLBACK_CAT_COLOR = '#000000'


class GetAreaDetailParam(BaseModel):
    area_name: str = Field(description='area name')


@bp.route('/get_area_detail', ['POST'])
@validate(json=GetAreaDetailParam)
@wish_response
@wish_checker(['player_in_team'])
async def get_area_detail(
    req: Request, body: GetAreaDetailParam, worker: Worker, user: Optional[User]
) -> Dict[str, Any]:
    assert user is not None
    assert user.is_staff or user.team is not None

    not_found = {'status': 'error', 'title': 'NOT FOUND', 'message': '不存在的区域'}

    if body.area_name not in ['intro', 'day1', 'day2', 'day3']:
        return not_found

    if user.is_staff:
        return {'status': 'success', 'data': adhoc.get_area_info(body.area_name, user, worker)}
    assert user.team is not None
    # 检查是否开始游戏
    if body.area_name != 'intro' and not worker.game_nocheck.is_game_begin():
        store_user_log(
            req, 'api.game.get_area_detail', 'abnormal', '游戏未开始时调用了 API。', {'area_name': body.area_name}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '游戏未开始！'}

    # 检查是否未解锁
    if body.area_name in ['intro', 'day1', 'day2', 'day3']:
        if body.area_name == 'intro' and not worker.game_nocheck.is_intro_unlock():
            return not_found
        if body.area_name not in user.team.game_status.unlock_areas:
            worker.log(
                'debug',
                'get_area_detail',
                f'area {body.area_name} not in T#{user.team.model.id}'
                + f'unlock areas {user.team.game_status.unlock_areas}]',
            )
            return not_found

    return {'status': 'success', 'data': adhoc.get_area_info(body.area_name, user, worker)}


@bp.route('/get_puzzle_list', ['POST'])
@wish_response
@wish_checker(['player_in_team'])
async def get_puzzle_list(req: Request, worker: Worker, user: Optional[User]) -> dict[str, Any]:
    assert user is not None
    assert user.is_staff or user.team is not None

    area_list = ['day1', 'day2', 'day3']

    rst_data = []

    if user.is_staff:
        for area_name in area_list:
            rst_data.append(adhoc.get_area_info(area_name, user, worker))
    else:
        # 检查是否开始游戏
        if not worker.game_nocheck.is_game_begin():
            store_user_log(req, 'api.game.get_puzzle_list', 'abnormal', '游戏未开始时调用了 API。', {})
            return {'status': 'error', 'title': 'ABNORMAL', 'message': '游戏未开始！'}
        assert user.team is not None
        for area_name in area_list:
            if area_name in user.team.game_status.unlock_areas:
                rst_data.append(adhoc.get_area_info(area_name, user, worker))

    return {'status': 'success', 'data': rst_data}


TEMPLATE_LIST = [
    ('faq', '选手常见问题', 0),
    ('staff', '工作人员', 9000),
]


@bp.route('/game_info', ['POST'])
@wish_response
async def game_info(_req: Request, worker: Worker, user: Optional[User]) -> Dict[str, Any]:
    if worker.game is None:
        return {'status': 'error', 'title': 'NO_GAME', 'message': '服务暂时不可用'}

    cur_tick = worker.game.cur_tick

    worker.log('debug', 'api.wish.game_info', f'{user} trying to get game_info')

    unlock_areas = adhoc.get_unlock_areas_info(user, worker)

    board_key_to_icon = {
        'score_board': 'ranking',
        'first_blood': 'first-blood',
        'speed_run': 'thunder',
    }
    unlock_boards: list[dict[str, str]] = []
    if not secret.PLAYGROUND_MODE and user is not None:
        if user.is_staff:
            for board in worker.game_nocheck.boards:
                unlock_boards.append(
                    {
                        'key': board,
                        'icon': board_key_to_icon.get(worker.game_nocheck.boards[board].key, 'unknown'),
                        'name': worker.game_nocheck.boards[board].name,
                    }
                )
        elif user.team is not None and worker.game_nocheck.is_game_begin():
            for board in user.team.game_status.unlock_boards:
                unlock_boards.append(
                    {
                        'key': board,
                        'icon': board_key_to_icon.get(worker.game_nocheck.boards[board].key, 'unknown'),
                        'name': worker.game_nocheck.boards[board].name,
                    }
                )

    result_dict = {
        'user': None
        if user is None
        else {
            'id': user.model.id,
            'group': user.model.group,
            'group_disp': user.model.group_disp(),
            'profile': {
                'nickname': user.model.user_info.nickname,
                'avatar_url': user.avatar_url,
                'email': user.model.user_info.email,
            },
        },
        'team': None
        if (user is None or user.team is None)
        else {
            'id': user.model.team_id,
            'team_name': user.team.model.team_name,
            'team_info': user.team.model.team_info,
            'team_secret': None if user.team.leader is not user else user.team.model.team_secret,
            'status': user.team.status,
            'gaming': user.team.gaming,
            'extra_status': user.team.model.ban_status,
            'disp_list': user.team.get_disp_list(),
            'leader_id': user.team.model.leader_id,
            'members': [
                {'id': member.model.id, 'nickname': member.model.user_info.nickname, 'avatar_url': member.avatar_url}
                for member in user.team.leader_and_members_modal
            ],
            'recruiting': user.team.model.extra_info.recruiting,
            'recruiting_contact': user.team.model.extra_info.recruiting_contact,
            'spap': user.team.cur_spap,
            'ban_list': {
                'ban_message_until': user.team.model.extra_info.ban_list.ban_message_until_ts,
                'ban_manual_hint_until': user.team.model.extra_info.ban_list.ban_manual_hint_until_ts,
                'ban_recruiting_until': user.team.model.extra_info.ban_list.ban_recruiting_until_ts,
            },
        },
        'game': {
            'login': user is not None,
            'isPrologueUnlock': worker.game_nocheck.is_intro_unlock(),
            'isGameBegin': worker.game_nocheck.is_game_begin(),
            'isGameEnd': worker.game_nocheck.is_game_end(),
            'start_ts': worker.game_nocheck.game_begin_timestamp_s,
            # TODO: 大概没用了
            'aboutTemplates': [
                {key: title} for key, title, effective_after in TEMPLATE_LIST if cur_tick >= effective_after
            ],
            'boards': unlock_boards,
        },
        'feature': {
            'push': secret.WS_PUSH_ENABLED and user is not None and user.check_play_game() is None,
            'debug': secret.DEBUG_MODE,
            'recaptcha': secret.USE_RECAPTCHA,
            'email_login': secret.EMAIL_AUTH_ENABLE,
            'sso_login': secret.SSO_AUTH_ENABLE,
            'playground': secret.PLAYGROUND_MODE,
        },
        'areas': unlock_areas,
    }

    if secret.DEBUG_MODE and result_dict['user'] is not None:
        assert user is not None
        result_dict['user']['login_key_for_debug'] = user.model.login_key  # type: ignore[call-overload, assignment]
    if user is not None and user.is_admin:
        result_dict['user']['admin'] = True  # type: ignore

    return result_dict


# class GetAnnouncementsParam(BaseModel):
#     category: str = Field(description="公告类型")


@bp.route('/get_announcements', ['POST'])
@wish_response
@wish_checker(['user_login'])
async def get_announcements(_req: Request, worker: Worker, user: Optional[User]) -> dict[str, Any]:
    assert user is not None
    assert worker.game is not None

    filtered_list = []
    now_time = time.time()
    for ann in worker.game.announcements.list:
        if now_time < ann.store.publish_at:
            continue
        if user.is_staff:
            filtered_list.append(ann)
        else:
            if ann.store.category == AnnouncementStore.Category.GENERAL.name:
                filtered_list.append(ann)
                continue
            if user.team is None:
                continue
            if worker.game_nocheck.is_game_begin():
                if ann.store.category in user.team.game_status.unlock_announcement_categories:
                    filtered_list.append(ann)

    return {
        'data': [ann.describe_json(user) for ann in filtered_list],
    }


@bp.route('/get_schedule', ['POST'])
@wish_response
async def get_schedule(_req: Request, worker: Worker) -> Dict[str, Any]:
    if worker.game is None:
        return {'status': 'error', 'title': 'NO_GAME', 'message': '服务暂时不可用'}

    return {
        'data': [
            {
                'timestamp_s': trigger.timestamp_s,
                'name': trigger.name,
                'status': (
                    'prs'
                    if trigger.tick == worker.game.cur_tick
                    else 'ftr'
                    if trigger.tick > worker.game.cur_tick
                    else 'pst'
                ),
            }
            for trigger in worker.game.trigger.stores
        ]
    }


class GetBoardParam(BaseModel):
    board_key: str


@bp.route('/get_board', ['POST'])
@validate(json=GetBoardParam)
@wish_response
@wish_checker(['player_in_team'])
async def get_board(req: Request, body: GetBoardParam, worker: Worker, user: Optional[User]) -> Dict[str, Any]:
    assert user is not None

    board_key = body.board_key

    if not user.is_staff:
        assert user.team is not None
        if not worker.game_nocheck.is_game_begin():
            store_user_log(
                req, 'api.game.get_board', 'abnormal', '游戏未开始时调用了 API。', {'board_key': body.board_key}
            )
            return {'status': 'error', 'title': 'NOT_FOUND', 'message': '排行榜不存在！'}
        if board_key not in user.team.game_status.unlock_boards:
            store_user_log(
                req,
                'api.game.get_board',
                'abnormal',
                'board_key 不在玩家的 unlock_boards 中。',
                {'board_key': body.board_key},
            )
            return {'status': 'error', 'title': 'NOT_FOUND', 'message': '排行榜不存在！'}

    b = worker.game_nocheck.boards.get(board_key, None)
    if b is None:
        return {'status': 'error', 'title': 'NOT_FOUND', 'message': '排行榜不存在'}

    # 在首杀榜上屏蔽没有解锁的题目
    # 游戏结束后就开放
    if board_key == 'first_blood' and not user.is_staff:
        if not worker.game_nocheck.is_game_begin():
            return {
                'data': {
                    'list': [],
                    'type': b.board_type,
                    'desc': b.desc,
                }
            }
        else:
            rendered = copy.deepcopy(b.get_rendered(user.is_staff))
            for item in rendered['list']:
                puzzle_list = item['list']

                for puzzle in puzzle_list:
                    is_lock = True
                    puzzle_key = puzzle['key']
                    if (
                        user is not None
                        and user.team is not None
                        and user.team.gaming
                        and user.team.game_status.puzzle_visible_status(puzzle_key) != 'lock'
                    ):
                        is_lock = False
                    if is_lock:
                        puzzle['title'] = 'unknown'
                        puzzle['key'] = utils.calc_sha1(puzzle['key'] + 'lock')
                    else:
                        assert user.team is not None
                        puzzle['key'] = worker.game_nocheck.hash_puzzle_key(user.team.model.id, puzzle_key)

                # 新加的逻辑，看不到未解锁题目的情况
                item['list'] = [puzzle for puzzle in puzzle_list if puzzle['title'] != 'unknown']

                if user is None or user.team is None or not user.team.gaming:
                    item['name'] = 'unknown'

            # 看不到未解锁区域的情况
            rendered['list'] = [area for area in rendered['list'] if area['name'] != 'unknown']

            return {
                'data': {
                    **rendered,
                    'type': b.board_type,
                    'desc': b.desc,
                }
            }

    return {
        'data': {
            **b.get_rendered(user.is_staff),
            'type': b.board_type,
            'desc': b.desc,
        }
    }


@bp.route('/team_ap_detail', ['POST'])
@wish_response
@wish_checker(['player_in_team'])
async def get_team_ap_detail(_req: Request, worker: Worker, user: Optional[User]) -> Dict[str, Any]:
    assert user is not None
    if user.is_staff:
        return {
            'team_ap_change': 0,
            'ap_increase_policy': worker.game_nocheck.policy.ap_increase_policy,
        }
    assert user.team is not None

    return {
        'data': {
            'team_ap_change': user.team.ap_change,
            'ap_increase_policy': worker.game_nocheck.policy.calc_ap_increase_policy_by_team(user.team),
        }
    }


class GameStartParam(BaseModel):
    content: str


@bp.route('/game_start', ['POST'])
@validate(json=GameStartParam)
@wish_response
@wish_checker(['player_in_team'])
async def game_start(req: Request, body: GameStartParam, worker: Worker, user: Optional[User]) -> Dict[str, Any]:
    assert user is not None and user.team is not None

    if not worker.game_nocheck.is_intro_unlock() and not user.is_staff:
        store_user_log(req, 'api.game.game_start', 'abnormal', '序章开放前调用了 API。', {'content': body.content})
        return {'status': 'error', 'title': 'ABNORMAL', 'message': '序章尚未开放。'}

    store_user_log(req, 'api.game.game_start', 'game_start', '', {'content': body.content})

    reply = adhoc.game_start_reply(body.content)
    if reply['status'] == 'success' and reply['title'] == '答案正确！':
        if user.is_staff:
            return {'status': 'success', 'title': '答案正确！', 'message': '游戏开始！但是你是工作人员，所以无事发生。'}
        # 需要判断是否已经开始游戏，在 checker 中判断
        rep = await worker.perform_action(
            glitter.TeamGameBeginReq(
                client=worker.process_name,
                user_id=user.model.id,
                team_id=user.team.model.id,
            )
        )
        if rep.result is not None:
            return utils.unpack_rep(rep.result)

    return reply


# TODO: 目前似乎没用
# @bp.route('/get_message_status', ['POST'])
# @wish_response
# async def get_message_status(_req: Request, worker: Worker, user: Optional[User]) -> Dict[str, Any]:
#     if worker.game is None:
#         return {"status": "error", "title": "NO_GAME", "message": "服务暂时不可用"}
#
#     return {
#         "unread": 0 if user is None else (
#             worker.game.messages.total_staff_unread_cnt if user.model.group == "staff" else (
#                 0 if user.model.team_id is None else
#                 worker.game.messages.message_by_team_id[user.model.team_id].player_unread_count
#                 if user.model.team_id in worker.game.messages.message_by_team_id else 0
#             )
#         )
#     }


@bp.route('/get_team_list', ['POST'])
@wish_response
@wish_checker(['user_login'])
async def get_team_list(_req: Request, worker: Worker, user: Optional[User]) -> Dict[str, Any]:
    assert user is not None
    assert worker.game is not None

    def _recruiting(team: Team) -> bool:
        if (
            len(team.members) == secret.TEAM_MAX_MEMBER
            or team.model.extra_info.ban_list.ban_recruiting_until_ts > time.time()
        ):
            return False
        return team.model.extra_info.recruiting

    res = {
        'team_list': [
            {
                'team_id': team.model.id,
                'team_name': team.model.team_name,
                'team_info': team.model.team_info,
                'team_members': team.member_info_list,
                'recruiting': _recruiting(team),
                'recruiting_contact': team.model.extra_info.recruiting_contact,
            }
            for team in worker.game.teams.list
        ]
    }

    return res


@bp.route('/get_story_list', ['POST'])
@wish_response
@wish_checker(['player_in_team', 'game_start'])
async def get_story_list(req: Request, worker: Worker, user: Optional[User]) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if not user.is_staff:
        if not worker.game_nocheck.is_game_begin():
            store_user_log(req, 'api.game.get_story_list', 'abnormal', '游戏开始前调用了 API。', {})
            return {'status': 'error', 'title': 'ABNORMAL', 'message': '游戏未开始！'}
        if not user.team.gaming:
            store_user_log(req, 'api.game.get_story_list', 'abnormal', '在队伍开始游戏前调用了 API。', {})
            return {'status': 'error', 'title': 'ABNORMAL', 'message': '队伍未开始游戏！'}

    rst = adhoc.get_story_list(user)

    return {'status': 'success', 'data': rst}
