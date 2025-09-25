import time

from typing import Any

from pydantic import BaseModel, Field
from sanic import Blueprint, Request
from sanic_ext import validate

from src import adhoc
from src.adhoc.hint import hint_cd_after_puzzle_unlock
from src.custom import store_user_log
from src.logic import Worker, glitter
from src.state import User
from src.store import HintStore

from . import wish_checker, wish_response


bp: Blueprint = Blueprint('wish-puzzle', url_prefix='/wish/puzzle')


class SubmitParam(BaseModel):
    puzzle_key: str = Field(description='Puzzle的key')
    content: str = Field(description='原始提交内容')


@bp.route('/submit_answer', ['POST'])
@validate(json=SubmitParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def submit_answer(req: Request, body: SubmitParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if not (0 < len(body.content) <= 100):
        store_user_log(req, 'api.puzzle.submit_answer', 'abnormal', f'答案长度不合法，长度为{len(body.content)}。', {})
        return {'status': 'error', 'title': '答案过长', 'message': '答案长度应在1到100之间。'}

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req,
            'api.puzzle.submit_answer',
            'abnormal',
            'unhash puzzle_key 失败。',
            {'body_puzzle_key': body.puzzle_key},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.puzzle.submit_answer',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if not user.is_staff and puzzle_key not in user.team.game_state.unlock_puzzle_keys:
        store_user_log(req, 'api.puzzle.submit_answer', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    store_user_log(
        req, 'api.puzzle.submit_answer', 'submit_answer', '', {'puzzle_key': puzzle_key, 'content': body.content}
    )

    puzzle = worker.game_nocheck.puzzles.puzzle_by_key[puzzle_key]
    rep = await worker.perform_action(
        glitter.SubmitAnswerReq(
            client=worker.process_name,
            user_id=user.model.id,
            puzzle_key=puzzle_key,
            content=body.content,
        )
    )

    need_reload = True

    if rep.result is not None:
        res_dict: dict[str, Any] = rep.result
        res_dict['need_reload'] = need_reload
        if res_dict['status'] == 'success':
            store_user_log(
                req,
                'api.puzzle.submit_answer',
                'answer_correct',
                '',
                {'puzzle_key': puzzle.model.key, 'content': body.content},
            )
            res_dict['need_reload'] = True
        elif res_dict['status'] == 'error':
            res_dict['need_reload'] = True
        elif res_dict['status'] == 'info':
            store_user_log(
                req,
                'api.puzzle.submit_answer',
                'milestone',
                '',
                {'puzzle_key': puzzle.model.key, 'content': body.content},
            )
        return res_dict
    # 这个 reducer 一定不会返回 None
    assert False


class GetSubmissionsParam(BaseModel):
    puzzle_key: str = Field(description='Puzzle的key')


@bp.route('/get_submissions', ['POST'])
@validate(json=GetSubmissionsParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_submissions(req: Request, body: GetSubmissionsParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req,
            'api.puzzle.get_submissions',
            'abnormal',
            'unhash puzzle_key 失败。',
            {'body_puzzle_key': body.puzzle_key},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.puzzle.get_submissions',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if not user.is_staff and puzzle_key not in user.team.game_state.unlock_puzzle_keys:
        store_user_log(req, 'api.puzzle.get_submissions', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    store_user_log(req, 'api.puzzle.get_submissions', 'get_submissions', '', {'puzzle_key': puzzle_key})

    # 分别处理管理员和普通用户
    if user.is_staff:
        return {
            'submissions': [
                {
                    'idx': idx,
                    # user in submission must be in a team
                    'team_name': sub.user.team.model.team_name,  # type: ignore[union-attr]
                    'user_name': sub.user.model.user_info.nickname,
                    'origin': sub.store.content,
                    'cleaned': sub.cleaned_content,
                    'status': sub.status,
                    'info': sub.result.info,
                    'timestamp_s': int(sub.store.created_at / 1000),
                }
                for idx, sub in enumerate(worker.game_nocheck.submissions_by_puzzle_key.get(puzzle_key, []))
            ][::-1]
        }
    else:

        def clean_sub(ori: str) -> str:
            return ori

        return {
            'submissions': [
                {
                    'idx': idx,
                    'team_name': None,
                    'user_name': sub.user.model.user_info.nickname,
                    'origin': clean_sub(sub.store.content),
                    'cleaned': clean_sub(sub.cleaned_content),
                    'status': sub.status,
                    'info': sub.result.info,
                    'timestamp_s': int(sub.store.created_at / 1000),
                }
                for idx, sub in enumerate(user.team.get_submissions_by_puzzle_key(puzzle_key))
            ][::-1]
        }


class GetDetailParam(BaseModel):
    puzzle_key: str = Field(description='Puzzle的key')


@bp.route('/get_detail', ['POST'])
@validate(json=GetDetailParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_detail(req: Request, body: GetDetailParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req,
            'api.puzzle.get_puzzle_details',
            'abnormal',
            'unhash puzzle_key 失败。',
            {'body_puzzle_key': body.puzzle_key},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.puzzle.get_puzzle_details',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if not user.is_staff and puzzle_key not in user.team.game_state.unlock_puzzle_keys:
        store_user_log(req, 'api.puzzle.get_puzzle_details', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    puzzle = worker.game_nocheck.puzzles.puzzle_by_key[puzzle_key]
    if not user.is_staff:
        # 如果不是 unlock，则视为没解锁，状态是 found 也不行
        if user.team.game_state.puzzle_visible_status(puzzle_key) != 'unlock':
            store_user_log(
                req, 'api.puzzle.get_detail', 'abnormal', '试图访问没解锁的题目。', {'puzzle_key': puzzle_key}
            )
            return {'status': 'error', 'title': 'NOT_FOUND', 'message': '题目不存在'}

    store_user_log(req, 'api.puzzle.get_puzzle_details', 'get_puzzle_details', '', {'puzzle_key': puzzle_key})

    puzzle_status = 'untouched'
    if not user.is_staff:
        puzzle_status = puzzle.status_by_team(user.team)
        if user.team.game_state.puzzle_visible_status(puzzle.model.key) == 'found':
            puzzle_status = 'found'

    # found 状态寻思下要不要设置
    # ADHOC
    if puzzle_key == 'day3_premeta':
        puzzle_status = 'special'

    puzzle_list: list[Any] = adhoc.gen_puzzle_structure_by_puzzle(puzzle, user, worker)

    dyn_actions = user.team.game_state.get_dyn_actions(puzzle.model.key)

    return_value = {
        'key': puzzle.model.key,
        'title': puzzle.model.title,
        'desc': puzzle.render_desc(user),
        'actions': puzzle.model.describe_actions() + dyn_actions,
        'status': puzzle_status,
        'puzzle_list': puzzle_list,
        **adhoc.get_more_puzzle_detail(puzzle, user),
    }

    if not user.is_staff:
        assert user.team is not None
        # 游戏结束后这个 assert 可能不成立
        # assert puzzle.model.key in user.team.game_state.unlock_puzzle_keys
        if puzzle.model.key in user.team.game_state.unlock_puzzle_keys:
            return_value['unlock_ts'] = user.team.game_state.unlock_puzzle_keys[puzzle.model.key]
            return_value['cold_down_ts'] = user.team.game_state.puzzle_state_by_key[puzzle.model.key].cold_down_ts
            if puzzle.model.key in user.team.game_state.passed_puzzle_keys:
                return_value['pass_ts'] = user.team.game_state.passed_puzzle_keys[puzzle.model.key]
        return_value['key'] = worker.game_nocheck.hash_puzzle_key(user.team.model.id, puzzle_key)

    if len(puzzle.model.clipboard) > 0:
        return_value['clipboard'] = [x.model_dump() for x in puzzle.model.clipboard]

    return {'data': return_value}


class GetHintsParam(BaseModel):
    puzzle_key: str = Field(description='Puzzle的key')


@bp.route('/get_hints', ['POST'])
@validate(json=GetHintsParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_hints(req: Request, body: GetHintsParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req, 'api.puzzle.get_hints', 'abnormal', 'unhash puzzle_key 失败。', {'body_puzzle_key': body.puzzle_key}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.puzzle.get_hints',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if not user.is_staff and puzzle_key not in user.team.game_state.unlock_puzzle_keys:
        store_user_log(req, 'api.puzzle.get_hints', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    puzzle = worker.game_nocheck.puzzles.puzzle_by_key.get(puzzle_key, None)
    assert puzzle is not None

    store_user_log(
        req,
        'api.puzzle.get_hints',
        'open_hint_list',
        '',
        {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key},
    )

    rst: list[dict[str, str | int]] = []
    current_ts = time.time()
    for hint in worker.game_nocheck.hints.hint_by_key.get(puzzle_key, []):
        if not hint.model.enable:
            continue
        # 普通玩家看不见不满足 effective_after_ts 的提示
        if not user.is_staff and hint.model.effective_after_ts > current_ts:
            continue

        effective_after_ts = hint.model.effective_after_ts
        if not user.is_staff:
            # 对于普通玩家来说，得等待提示解锁
            unlock_puzzle_ts = user.team.game_state.unlock_puzzle_keys[puzzle_key]
            hint_cd = hint_cd_after_puzzle_unlock(hint)
            effective_after_ts = unlock_puzzle_ts + hint_cd

        rst.append(
            {
                'id': hint.model.id,
                'question': hint.model.question,
                'answer': hint.model.answer if (user.is_staff or hint.model.id in user.team.bought_hint_ids) else '',
                'type': HintStore.HintType.dict().get(hint.model.type, '未知'),
                'cost': hint.model.extra.cost,
                'unlock': user.is_staff or hint.model.id in user.team.bought_hint_ids,
                'effective_after_ts': effective_after_ts,
            }
        )

    return {'status': 'success', 'data': {'list': rst}}


class BuyHintParam(BaseModel):
    puzzle_key: str
    hint_id: int


@bp.route('/buy_hint', ['POST'])
@validate(json=BuyHintParam)
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def buy_hint(req: Request, body: BuyHintParam, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    if worker.game_nocheck.is_game_end():
        return {'status': 'error', 'title': 'GAME_END', 'message': '活动已结束！'}

    if user.is_staff:
        store_user_log(
            req, 'api.puzzle.buy_hint', 'abnormal', 'staff 不应该调这个 API。', {'body_puzzle_key': body.puzzle_key}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': 'staff不应该调用这个接口'}
    assert user.team is not None

    team_id, puzzle_key = worker.game_nocheck.unhash_puzzle_key(user.team.model.id, body.puzzle_key)
    # 找不到原始 puzzle_key
    if puzzle_key is None:
        store_user_log(
            req, 'api.puzzle.buy_hint', 'abnormal', 'unhash puzzle_key 失败。', {'body_puzzle_key': body.puzzle_key}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 是其他队伍的 puzzle_key
    if team_id != user.team.model.id:
        store_user_log(
            req,
            'api.puzzle.buy_hint',
            'abnormal',
            '提交了其他队伍的 puzzle_key。',
            {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'another_team_id': team_id},
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}
    # 此时 puzzle_key 一定是存在的
    if puzzle_key not in user.team.game_state.unlock_puzzle_keys:
        store_user_log(req, 'api.puzzle.buy_hint', 'abnormal', '题目未解锁。', {'puzzle_key': puzzle_key})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '谜题不存在！'}

    puzzle = worker.game_nocheck.puzzles.puzzle_by_key.get(puzzle_key, None)
    assert puzzle is not None

    store_user_log(
        req,
        'api.puzzle.buy_hint',
        'buy_hint',
        '',
        {'body_puzzle_key': body.puzzle_key, 'real_puzzle_key': puzzle_key, 'hint_id': body.hint_id},
    )

    assert user.model.team_id is not None

    rep = await worker.perform_action(
        glitter.TeamBuyHintReq(
            client=worker.process_name,
            user_id=user.model.id,
            team_id=user.model.team_id,
            hint_id=body.hint_id,
            puzzle_key=puzzle_key,
        )
    )

    if rep.result is not None:
        return rep.result

    return {'data': 'ok'}
