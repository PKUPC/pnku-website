import time

from collections.abc import Awaitable, Callable
from typing import Any

from sanic.request import Request

from src import secret, store, utils
from src.adhoc.constants import MANUAL_HINT_COOLDOWN
from src.adhoc.hint import hint_cd_after_puzzle_unlock
from src.custom import store_user_log
from src.state import Game

from . import glitter
from .utils import make_callback_decorator


class Checker:
    on_action, action_listeners = make_callback_decorator('Checker')

    def __init__(self, game: Game) -> None:
        self.game = game
        self.log = game.log

    async def check_action(self, req: glitter.ActionReq, http_req: Request | None = None) -> dict[str, str] | None:
        if isinstance(req, glitter.WorkerHeartbeatReq):
            return None

        self.log('info', 'checker.check_action', f'check action {req.type}')

        async def default(_self: Any, _req: glitter.ActionReq, _http_req: Request | None = None) -> None:
            self.log('info', 'checker.check_action', f'action {req.type} are not registered in Checker.')
            return None

        listener: Callable[[Any, glitter.ActionReq, Request | None], Awaitable[dict[str, str] | None]] = (
            self.action_listeners.get(type(req), default)
        )
        check_result = await listener(self, req, http_req)
        return check_result

    @on_action(glitter.TeamGameBeginReq)
    async def on_team_game_begin(
        self, req: glitter.TeamGameBeginReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        if req.team_id not in self.game.teams.team_by_id:
            return {'status': 'error', 'title': 'abnormal', 'message': '队伍不存在！'}
        cur_team = self.game.teams.team_by_id[req.team_id]
        if cur_team.gaming:
            return {'status': 'error', 'title': '', 'message': '你的队伍已开始游戏'}
        return None

    @on_action(glitter.PuzzleActionReq)
    async def on_puzzle_action(
        self, req: glitter.PuzzleActionReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        team = self.game.teams.team_by_id[req.team_id]
        # 这里已经保证了队伍解锁了这一题目
        if req.puzzle_key == 'day2_02':
            if team.is_staff_team:
                COOLDOWN = 0
            elif secret.DEBUG_MODE:
                COOLDOWN = 10
            else:
                COOLDOWN = 15 * 60
            # 检查距离上次的时间
            actions = team.game_state.puzzle_actions['day2_02']
            if len(actions) > 0:
                last_action = actions[-1]
                time_diff = int(req.content.get('real_seconds', -1)) - int(last_action.content.get('real_seconds', -1))
                if time_diff < COOLDOWN:
                    return {
                        'status': 'error',
                        'title': 'TIME_LIMITED',
                        'message': f'冷却中，请{COOLDOWN - time_diff}秒后再试。',
                    }

        return None

    @on_action(glitter.SubmitAnswerReq)
    async def on_team_submit_answer(
        self, req: glitter.SubmitAnswerReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        assert req.user_id in self.game.users.user_by_id
        assert req.puzzle_key in self.game.puzzles.puzzle_by_key
        user = self.game.users.user_by_id[req.user_id]
        puzzle = self.game.puzzles.puzzle_by_key[req.puzzle_key]

        # 如果是 staff，不用特别检察
        if user.is_staff and puzzle is not None:
            return None
        assert user.team is not None

        if self.game.is_game_end():
            return {'status': 'error', 'title': 'NOT ALLOWED', 'message': '活动已结束，现在暂时不能提交答案。'}

        # 没解锁的题目直接不存在
        # 游戏开始前题目自然都没有解锁，因此这个逻辑也是对的
        if user.team.game_state.puzzle_visible_status(puzzle.model.key) != 'unlock':
            store_user_log(
                http_req,
                'checker.submit_answer',
                'abnormal',
                '试图给没有解锁的题目提交答案。',
                {'puzzle_key': req.puzzle_key, 'content': req.content},
            )
            return {'status': 'error', 'title': '题目不存在', 'message': '请联系网站管理员。'}

        if user.team.preparing:
            store_user_log(
                http_req,
                'checker.submit_answer',
                'abnormal',
                '试图在队伍未开始游戏时提交答案。',
                {'puzzle_key': req.puzzle_key, 'content': req.content},
            )
            return {'status': 'error', 'title': 'NOT_FOUND', 'message': '题目不存在'}

        if utils.clean_submission(req.content) in user.team.game_state.get_submission_set(req.puzzle_key):
            return {'status': 'info', 'title': '重复提交', 'message': '你已经提交过这个答案，请在提交列表查看。'}

        # 理论上在上一步就限制了
        # if user.team in puzzle.passed_teams:
        #     return {"status": "info", "title": "重复提交", "message": "你的队伍已通过这个题"}

        # 限制提交频率
        if not secret.DEBUG_MODE:
            if user.team.last_submission is not None:
                delta = time.time() - user.team.last_submission.store.created_at / 1000
                if delta < 3:
                    return {'status': 'error', 'title': '太快了！', 'message': f'提交太频繁，请等待 {3 - delta:.1f} 秒'}

        if time.time() < user.team.game_state.puzzle_state_by_key[req.puzzle_key].cold_down_ts:
            return {'status': 'error', 'title': '冷却中', 'message': '冷却中，无法提交题目。'}

        return None

    @on_action(glitter.TeamBuyHintReq)
    async def on_team_buy_hint(
        self, req: glitter.TeamBuyHintReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        user_id = req.user_id
        hint_id = req.hint_id
        puzzle_key = req.puzzle_key
        user = self.game.users.user_by_id[user_id]
        assert user.team is not None
        if user.team.preparing:
            store_user_log(
                http_req,
                'checker.on_team_buy_hint',
                'abnormal',
                '试图在队伍开始游戏前购买提示。',
                {'puzzle_key': req.puzzle_key, 'hint_id': req.hint_id},
            )
            return {'status': 'error', 'title': 'NOT_FOUND', 'message': '题目不存在'}

        if hint_id not in self.game.hints.hint_by_id:
            store_user_log(
                http_req,
                'checker.on_team_buy_hint',
                'abnormal',
                '试图购买不存在的提示。',
                {'puzzle_key': req.puzzle_key, 'hint_id': req.hint_id},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '提示不存在'}
        if hint_id in user.team.bought_hint_ids:
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你已经购买过该提示，请勿重复购买'}

        hint = self.game.hints.hint_by_id[hint_id]
        if not hint.effective:
            return {'status': 'error', 'title': 'NOT_EFFECTIVE', 'message': '提示当前不可用'}

        for price in hint.current_price:
            print('DEBUG!!!')
            print(user.team.cur_currency_by_type(price.type))
            print(price.price)
            if user.team.cur_currency_by_type(price.type) < price.price:
                return {'status': 'error', 'title': 'NO_ENOUGH_MONEY', 'message': f'{price.type.value}不足，无法购买'}

        if puzzle_key != hint.model.puzzle_key:
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '提示状态异常，请通知工作人员'}

        current_ts = time.time()
        unlock_puzzle_ts = user.team.game_state.unlock_puzzle_keys[puzzle_key]
        hint_cd = hint_cd_after_puzzle_unlock(hint)
        if unlock_puzzle_ts + hint_cd > current_ts:
            store_user_log(
                http_req,
                'checker.on_team_buy_hint',
                'abnormal',
                '试图购买还没到冷却时间的提示。',
                {'puzzle_key': req.puzzle_key, 'hint_id': req.hint_id},
            )
            return {'status': 'error', 'title': 'ABNORMAL', 'message': '冷却时间未到，不能购买提示！异常行为已记录！'}

        return None

    @on_action(glitter.TicketMessageReq)
    async def on_ticket_message(
        self, req: glitter.TicketMessageReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        ticket = self.game.tickets.ticket_by_id[req.ticket_id]
        user = self.game.users.user_by_id[req.user_id]
        # 如果这个 ticket 是人工提示，且 staff 没有回复，且发送者是普通用户，则拒绝
        if (
            ticket.model.type == store.TicketStore.TicketType.MANUAL_HINT.name
            and not ticket.staff_replied
            and not user.is_staff
        ):
            store_user_log(
                http_req,
                'checker.on_ticket_message',
                'abnormal',
                '试图在工作人员还未回复时发送消息。',
                {'ticket_id': ticket.model.id, 'content': req.content},
            )
            return {
                'status': 'error',
                'title': 'NOT_REPLIED',
                'message': '芈雨还没有回复你的请求，你暂时无法和芈雨继续交流。',
            }
        # 如果工单已关闭
        if ticket.model.status == store.TicketStore.TicketStatus.CLOSED.name:
            store_user_log(
                http_req,
                'checker.on_ticket_message',
                'abnormal',
                '试图给已经关闭的工单发送消息。',
                {'ticket_id': ticket.model.id, 'content': req.content},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '该会话已关闭，你无法再发送新的信息。'}

        return None

    @on_action(glitter.TeamCreateTicketReq)
    async def on_team_create_ticket(
        self, req: glitter.TeamCreateTicketReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        # 判断当前未完成的提示数量
        user = self.game.users.user_by_id[req.user_id]
        assert user.team is not None
        # 判断是否到达解锁时间
        if req.ticket_type == 'MANUAL_HINT':
            puzzle_key = req.extra['puzzle_key']
            if user.team.game_state.unlock_puzzle_keys[puzzle_key] + MANUAL_HINT_COOLDOWN > time.time():
                store_user_log(
                    http_req,
                    'checker.on_team_create_ticket',
                    'abnormal',
                    '试图在还不能购买人工提示的时候购买人工提示。',
                    {'puzzle_key': puzzle_key, 'subject': req.subject},
                )
                return {'status': 'error', 'title': 'REJECTED', 'message': '题目解锁 2 个小时后才能申请神谕。'}

            count = self.game.tickets.count_by_team_id_and_type_and_status(
                user.team.model.id,
                store.TicketStore.TicketType.MANUAL_HINT.name,
                store.TicketStore.TicketStatus.OPEN.name,
            )
            if count > 0:
                return {
                    'status': 'error',
                    'title': 'REJECTED',
                    'message': '你和芈雨还有未完成的神谕请求，现在不能发起新请求。',
                }

        return None

    @on_action(glitter.SetTicketStatusReq)
    async def on_set_ticket_status(
        self, req: glitter.SetTicketStatusReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        # 判断当前未完成的提示数量
        user = self.game.users.user_by_id[req.user_id]
        assert user.team is not None
        ticket = self.game.tickets.ticket_by_id[req.ticket_id]
        # 如果是人工提示且staff没有回复，则玩家不能关闭

        if not user.is_staff and not ticket.staff_replied and req.status == store.TicketStore.TicketStatus.CLOSED.name:
            store_user_log(
                http_req,
                'checker.on_set_ticket_status',
                'abnormal',
                '试图在工作人员回复人工提示前关闭人工提示。',
                {'ticket_id': ticket.model.id},
            )
            return {
                'status': 'error',
                'title': 'REJECTED',
                'message': '芈雨还未回复你的最后一条请求，现在不能结束神谕。',
            }

        return None

    @on_action(glitter.TeamSendMsgReq)
    async def on_send_message(
        self, req: glitter.TeamSendMsgReq, http_req: Request | None = None
    ) -> dict[str, str] | None:
        # 判断当前未完成的提示数量
        user = self.game.users.user_by_id[req.user_id]
        assert user.team is not None

        if not user.is_staff and user.team.model.extra_info.ban_list.ban_message_until_ts > time.time():
            store_user_log(
                http_req,
                'api.message.send_message',
                'abnormal',
                '被禁止发送站内信的队伍发送了站内信。',
                {'team_id': req.team_id, 'type': req.type, 'content': req.content},
            )
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你的队伍被禁止发送站内信！'}

        return None
