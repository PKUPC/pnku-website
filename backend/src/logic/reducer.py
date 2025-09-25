from __future__ import annotations

import asyncio
import copy
import json
import time

from collections.abc import Awaitable, Callable, Sequence
from functools import cache
from typing import Any

import zmq

from sqlalchemy import and_, select
from zmq.asyncio import Socket

from src import secret, utils
from src.state import Announcements, Trigger
from src.store import (
    MessageStore,
    SubmissionStore,
    TeamEventStore,
    TeamEventType,
    TeamStore,
    TicketMessageStore,
    TicketStore,
    UserStore,
)

from . import glitter
from .base import StateContainerBase
from .glitter import ActionResult
from .utils import make_callback_decorator


@cache
def make_datebase_error(message: str) -> dict[str, str]:
    return {'status': 'error', 'title': 'DATABASE_ERROR', 'message': message}


CRITICAL_ERROR: dict[str, str] = {
    'status': 'error',
    'title': 'CRITICAL_ERROR',
    'message': '出大问题了，快联系工作人员！',
}


class Reducer(StateContainerBase):
    SYNC_THROTTLE_S = 1
    SYNC_INTERVAL_S = 3

    on_action, action_listeners = make_callback_decorator('Reducer')

    def __init__(self, process_name: str):
        super().__init__(process_name, use_boards=False)

        self.action_socket: Socket = self.glitter_ctx.socket(zmq.REP)
        self.event_socket: Socket = self.glitter_ctx.socket(zmq.PUB)

        self.action_socket.setsockopt(zmq.RCVTIMEO, self.SYNC_INTERVAL_S * 1000)
        self.action_socket.setsockopt(zmq.SNDTIMEO, glitter.CALL_TIMEOUT_MS)
        self.event_socket.setsockopt(zmq.SNDTIMEO, glitter.SYNC_TIMEOUT_MS)

        self.action_socket.bind(secret.GLITTER_ACTION_SOCKET_ADDR)
        self.event_socket.bind(secret.GLITTER_EVENT_SOCKET_ADDR)

        self.announcement_updater_task: asyncio.Task[None] | None = None
        self.tick_updater_task: asyncio.Task[None] | None = None
        self.health_check_task: asyncio.Task[None] | None = None

        self.received_telemetries: dict[str, tuple[float, dict[str, Any]]] = {process_name: (0, {})}

        self.last_emit_sync_time: float = 0

    async def _before_run(self) -> None:
        await super()._before_run()

        # self.log('info', 'reducer.before_run', 'started to initialize media files')
        # await utils.prepare_media_files()

        self.log('info', 'reducer.before_run', 'started to initialize game')
        await self.init_game(0)
        await self._update_tick()
        self.game_dirty = False

    @on_action(glitter.WorkerHelloReq)
    async def on_worker_hello(self, req: glitter.WorkerHelloReq) -> ActionResult:
        client_ver = req.protocol_ver
        if client_ver != glitter.PROTOCOL_VER:
            return {
                'status': 'error',
                'title': 'PROTOCOL_VERSION_MISMATCH',
                'message': f'protocol version mismatch: worker {req.protocol_ver}, reducer {glitter.PROTOCOL_VER}',
            }
        else:
            await self.emit_sync()
            return None

    @on_action(glitter.UserRegReq)
    async def on_user_reg(self, req: glitter.UserRegReq) -> ActionResult:
        if req.login_key in self._game.users.user_by_login_key:
            return make_datebase_error('user already exists')

        with self.SqlSession() as session:
            user = UserStore(
                login_key=req.login_key,
                login_properties=req.login_properties,
                enabled=True,
                group=req.group,
                user_info={'nickname': 'nickname', 'email': 'default@example.com'},
            )
            session.add(user)
            session.flush()
            uid = user.id
            assert uid is not None, 'created user not in db'

            user_info = {'nickname': 'nickname', 'email': 'default@example.com'}

            if 'email' in req.init_info:
                user_info['email'] = req.init_info['email']
            elif req.login_properties['type'] == 'manual':
                user_info['email'] = 'manual@example.com'
            elif req.login_properties['type'] == 'email':
                user_info['email'] = req.login_key[6:]

            if 'nickname' in req.init_info:
                user_info['nickname'] = req.init_info['nickname']
            else:
                user_info['nickname'] = f'user #{uid}'

            user.user_info = user_info

            session.commit()
            self.state_counter += 1

        await self.emit_event(glitter.Event(glitter.EventType.UPDATE_USER, self.state_counter, uid))
        return None

    @on_action(glitter.UserResetReq)
    async def on_user_reset(self, req: glitter.UserResetReq) -> ActionResult:
        assert req.login_key in self._game.users.user_by_login_key
        cur_user = self._game.users.user_by_login_key[req.login_key]

        with self.SqlSession() as session:
            user: UserStore | None = session.execute(
                select(UserStore).where(UserStore.id == cur_user.model.id)
            ).scalar()
            assert user is not None
            user.login_properties = req.login_properties
            session.commit()

            uid = user.id
            assert uid is not None, 'created user not in db'

            session.commit()
            self.state_counter += 1

        await self.emit_event(glitter.Event(glitter.EventType.UPDATE_USER, self.state_counter, uid))
        return None

    @on_action(glitter.UserUpdateProfileReq)
    async def on_user_update_profile(self, req: glitter.UserUpdateProfileReq) -> ActionResult:
        uid = int(req.uid)

        with self.SqlSession() as session:
            user: UserStore | None = session.query(UserStore).filter_by(id=uid).with_for_update().scalar()
            if user is None:
                return make_datebase_error('user not found')
            new_user_info = copy.deepcopy(user.user_info)
            new_user_info.update({'nickname': req.profile['nickname']})
            user.user_info = new_user_info
            user.updated_at = int(1000 * time.time())

            session.commit()
            self.state_counter += 1

        await self.emit_event(glitter.Event(glitter.EventType.UPDATE_USER, self.state_counter, uid))
        return None

    @on_action(glitter.UserAgreeTermReq)
    async def on_user_agree_term(self, req: glitter.UserAgreeTermReq) -> ActionResult:
        uid = int(req.uid)

        with self.SqlSession() as session:
            user: UserStore | None = session.execute(select(UserStore).where(UserStore.id == uid)).scalar()
            if user is None:
                return make_datebase_error('user not found')

            # user.terms_agreed = True
            session.commit()
            self.state_counter += 1

        await self.emit_event(glitter.Event(glitter.EventType.UPDATE_USER, self.state_counter, uid))
        return None

    @on_action(glitter.UserCreateTeamReq)
    async def on_user_create_team(self, req: glitter.UserCreateTeamReq) -> ActionResult:
        uid = req.uid
        user_state = self._game.users.user_by_id[uid]

        if user_state.model.team_id is not None:
            return {'status': 'error', 'title': 'IN_TEAM', 'message': '你已经在队伍中'}
        if user_state.model.group == 'staff':
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '工作人员不能组队'}
        if req.team_name in self._game.teams.team_name_set:
            return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名不能和现存队伍名重复'}

        with self.SqlSession() as session:
            user: UserStore | None = session.execute(select(UserStore).where(UserStore.id == uid)).scalar()
            if user is None:
                return make_datebase_error('user not found')

            # create team
            team = TeamStore(
                leader_id=uid,
                team_name=req.team_name,
                team_info=req.team_info,
                team_secret=req.team_secret,
                status=TeamStore.DEFAULT_STATUS,
                extra_info={},
            )

            session.add(team)
            session.flush()

            assert team.id is not None, 'team not in db'
            user.team_id = team.id

            session.flush()
            session.commit()

        # 创建队伍时需要更新的信息
        self.state_counter += 1
        tid: int = team.id
        await self.emit_event(glitter.Event(glitter.EventType.CREATE_TEAM, self.state_counter, tid))
        return None

    @on_action(glitter.TeamUpdateInfoReq)
    async def on_team_update_profile(self, req: glitter.TeamUpdateInfoReq) -> ActionResult:
        user = self._game.users.user_by_id[req.uid]
        # 检查是否已经在队伍里
        if user.team is None:
            return {'status': 'error', 'title': 'NOT_IN_TEAM', 'message': '你还没组队'}
        # 如果已经在队里，必须要是队长
        elif user.team.model.leader_id != user.model.id:
            return {'status': 'error', 'title': 'NO_PERMISSION', 'message': '你不是队长，没有权限更改队伍信息'}
        # 游戏开始后禁止修改
        if user.team.gaming and req.team_name != user.team.model.team_name:
            return {
                'status': 'error',
                'title': 'BAD_REQUEST',
                'message': '在开始游戏后禁止修改队伍名称，如有需要请联系工作人员。',
            }
        # 队伍名不能和现存队伍名重复
        if req.team_name != user.team.model.team_name and req.team_name in self._game.teams.team_name_set:
            return {'status': 'error', 'title': 'BAD_NAME', 'message': '队伍名不能和现存队伍名重复'}

        tid = req.tid

        with self.SqlSession() as session:
            team: TeamStore | None = session.execute(select(TeamStore).where(TeamStore.id == tid)).scalar()
            if team is None:
                return make_datebase_error('team not found')

            team.updated_at = int(1000 * time.time())
            team.team_name = req.team_name
            team.team_info = req.team_info
            team.team_secret = req.team_secret

            session.commit()
            self.state_counter += 1
        # 更新队伍信息
        await self.emit_event(glitter.Event(glitter.EventType.UPDATE_TEAM_INFO, self.state_counter, tid))
        return None

    @on_action(glitter.TeamUpdateExtraTeamInfoReq)
    async def on_team_update_extra_info(self, req: glitter.TeamUpdateExtraTeamInfoReq) -> ActionResult:
        user = self._game.users.user_by_id[req.uid]
        if not user.is_staff:
            # 检查是否已经在队伍里
            if user.team is None:
                return {'status': 'error', 'title': 'NOT_IN_TEAM', 'message': '你还没组队'}
            # 如果已经在队里，必须要是队长
            elif user.team.model.leader_id != user.model.id:
                return {'status': 'error', 'title': 'NO_PERMISSION', 'message': '你不是队长，没有权限更改队伍信息'}

        tid = req.tid

        with self.SqlSession() as session:
            team: TeamStore | None = session.execute(select(TeamStore).where(TeamStore.id == tid)).scalar()
            if team is None:
                assert False

            new_extra_info = copy.deepcopy(team.extra_info)
            if req.info_type == 'recruitment':
                new_extra_info.update(
                    {
                        'recruiting': req.data.get('recruiting', False),
                        'recruiting_contact': req.data.get('recruiting_contact', ''),
                    }
                )
            elif req.info_type == 'ban_list':
                new_extra_info.update({'ban_list': req.data})
            team.extra_info = new_extra_info
            team.updated_at = int(1000 * time.time())

            session.commit()
            self.state_counter += 1
        # 更新队伍信息
        await self.emit_event(glitter.Event(glitter.EventType.UPDATE_TEAM_INFO, self.state_counter, tid))
        return None

    @on_action(glitter.UserJoinTeamReq)
    async def on_user_join_team(self, req: glitter.UserJoinTeamReq) -> ActionResult:
        tid = req.tid
        uid = req.uid
        u = self._game.users.user_by_id[uid]

        # 检查队伍是否存在
        if tid not in self._game.teams.team_by_id:
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不存在的队伍'}
        target_team = self._game.teams.team_by_id[tid]
        # 如果队伍已经封禁，则禁止加入队伍
        if target_team.model.ban_status == TeamStore.BanStatus.BANNED.name:
            return {'status': 'error', 'title': 'BAD_TEAM', 'message': '队伍已封禁，禁止加入。'}
        # 检查是否已经在队伍里
        if u.team is not None:
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你已经在队伍里'}
        # 检查队伍人数限制
        if len(target_team.members) == secret.TEAM_MAX_MEMBER:
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍人数达到上限'}
        # 检查 secret
        if target_team.model.team_secret != req.team_secret:
            return {'status': 'error', 'title': 'WRONG_SECRET', 'message': '队伍邀请码错误'}

        with self.SqlSession() as session:
            # noinspection DuplicatedCode
            team: TeamStore | None = session.execute(select(TeamStore).where(TeamStore.id == tid)).scalar()
            assert team is not None
            user: UserStore | None = session.execute(select(UserStore).where(UserStore.id == uid)).scalar()
            assert user is not None
            user.team_id = team.id
            session.commit()

        self.state_counter += 1
        # 更新队伍信息
        await self.emit_event(glitter.Event(glitter.EventType.JOIN_TEAM, self.state_counter, uid))
        return None

    @on_action(glitter.UserLeaveTeamReq)
    async def on_user_leave_team(self, req: glitter.UserLeaveTeamReq) -> ActionResult:
        tid = req.tid
        uid = req.uid
        u = self._game.users.user_by_id[uid]

        if u.model.group != 'staff' and u.model.team_id is None:
            return {'status': 'error', 'title': 'NO_TEAM', 'message': '用户不在队伍中'}
        # 检查队伍状态
        assert u.team is not None
        if u.team.gaming:
            return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '队伍已经在游戏中，你现在不能离开队伍'}

        with self.SqlSession() as session:
            team: TeamStore | None = session.execute(select(TeamStore).where(TeamStore.id == tid)).scalar()
            assert team is not None
            user: UserStore | None = session.execute(select(UserStore).where(UserStore.id == uid)).scalar()
            assert user is not None

            team_dissolved = uid == team.leader_id

            if team_dissolved:
                # 如果是队长离开，则队伍解散
                team_state = self._game.teams.team_by_id[team.id]
                for member in team_state.members:
                    teammate: UserStore | None = session.execute(
                        select(UserStore).where(UserStore.id == member.model.id)
                    ).scalar()
                    if teammate is None:
                        continue
                    teammate.team_id = None
                    # 删除队伍信息
                team.status = TeamStore.Status.DISSOLVED.name
            # 普通队员离开
            else:
                user.team_id = None

            session.commit()
        self.state_counter += 1
        if team_dissolved:
            await self.emit_event(glitter.Event(glitter.EventType.DISSOLVE_TEAM, self.state_counter, tid))
        else:
            await self.emit_event(glitter.Event(glitter.EventType.LEAVE_TEAM, self.state_counter, uid))
        return None

    @on_action(glitter.TeamRemoveUserReq)
    async def on_team_remove_user(self, req: glitter.TeamRemoveUserReq) -> ActionResult:
        target_uid = req.uid
        from_uid = req.from_id
        from_user = self._game.users.user_by_id[from_uid]

        if from_user.model.group != 'staff' and from_user.model.team_id is None:
            return {'status': 'error', 'title': 'NO_TEAM', 'message': '用户不在队伍中'}
        assert from_user.team is not None
        if from_user.team.leader is not from_user:
            return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不是队长'}
        if target_uid not in [x.model.id for x in from_user.team.members]:
            return {'status': 'error', 'title': 'USER_NOT_FOUND', 'message': '要删除的用户不在队伍中'}
        if from_user.team.gaming:
            return {'status': 'error', 'title': 'TEAM_LOCK', 'message': '队伍已经在游戏中，现在不能移除队伍成员'}

        if from_uid == target_uid:
            return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不能移除你自己'}

        with self.SqlSession() as session:
            user: UserStore | None = session.execute(select(UserStore).where(UserStore.id == target_uid)).scalar()
            assert user is not None
            user.team_id = None
            session.commit()

        self.state_counter += 1
        # 视作用户离队
        await self.emit_event(glitter.Event(glitter.EventType.LEAVE_TEAM, self.state_counter, target_uid))
        return None

    @on_action(glitter.TeamChangeLeaderReq)
    async def on_team_change_leader(self, req: glitter.TeamChangeLeaderReq) -> ActionResult:
        target_uid = req.uid
        from_uid = req.from_id
        from_user = self._game.users.user_by_id[from_uid]
        if from_user.model.group != 'staff' and from_user.model.team_id is None:
            return {'status': 'error', 'title': 'NO_TEAM', 'message': '用户不在队伍中'}
        assert from_user.team is not None
        if from_user.team.leader is not from_user:
            return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不是队长'}
        if target_uid not in [x.model.id for x in from_user.team.members]:
            return {'status': 'error', 'title': 'USER_NOT_FOUND', 'message': '目标用户不在队伍中'}
        if from_user.model.id == target_uid:
            return {'status': 'error', 'title': 'PERMISSION_DENIED', 'message': '你不能转移给你自己'}

        tid = req.tid

        with self.SqlSession() as session:
            team: TeamStore | None = session.execute(select(TeamStore).where(TeamStore.id == tid)).scalar()
            assert team is not None
            user: UserStore | None = session.execute(select(UserStore).where(UserStore.id == target_uid)).scalar()
            assert user is not None

            team.leader_id = target_uid
            session.commit()

        self.state_counter += 1
        # 更新队伍信息
        await self.emit_event(glitter.Event(glitter.EventType.CHANGE_TEAM_LEADER, self.state_counter, tid))

        return None

    @on_action(glitter.SubmitAnswerReq)
    async def on_submit_answer(self, req: glitter.SubmitAnswerReq) -> ActionResult:
        user = self._game.users.user_by_id[req.user_id]
        assert user.team is not None

        with self.SqlSession() as session:
            submission = SubmissionStore(
                user_id=int(req.user_id),
                puzzle_key=req.puzzle_key,
                content=req.content,
            )
            session.add(submission)
            # 需要用事务保证提交记录和添加 team event 是同时更新的
            session.flush()
            assert submission.id is not None, 'created submission not in db'

            team_event = TeamEventStore(
                user_id=req.user_id,
                team_id=user.team.model.id,
                info={
                    'type': TeamEventType.SUBMISSION.name,
                    'submission_id': submission.id,
                },
            )
            session.add(team_event)
            session.flush()
            assert team_event.id is not None, 'created team_event not in db'
            team_event.validated_model()
            session.commit()
            self.state_counter += 1
        tid: int = team_event.id
        # 理论上应当在添加完成 team event 之后读取结果，但是有点麻烦，因为没做 team_event_by_id
        # 先 test 应当是一样的
        submission_result = user.team.game_state.test_submission(req.puzzle_key, req.content)
        await self.emit_event(glitter.Event(glitter.EventType.NEW_SUBMISSION, self.state_counter, tid))

        res = {'status': 'error', 'title': '未知错误！', 'message': '请联系网站管理员。'}

        if submission_result.type == 'wrong':
            res = {'status': 'error', 'title': '答案错误！', 'message': '答案错误！你没有得到任何信息！'}
        elif submission_result.type == 'milestone':
            res = {'status': 'info', 'title': '里程碑！', 'message': f'你收到了一条信息：\n{submission_result.info}'}
        elif submission_result.type == 'pass':
            res = {'status': 'success', 'title': '答案正确！', 'message': f'{submission_result.info}'}
        elif submission_result.type == 'multipass':
            res = {'status': 'success', 'title': '答案正确！', 'message': f'{submission_result.info}'}
        elif submission_result.type == 'staff_pass':
            res = {'status': 'success', 'title': '答案正确！', 'message': f'{submission_result.info}'}
        elif submission_result.type == 'staff_wrong':
            res = {'status': 'error', 'title': '答案错误！', 'message': f'{submission_result.info}'}
        return res

    @on_action(glitter.TeamBuyHintReq)
    async def on_team_buy_hint(self, req: glitter.TeamBuyHintReq) -> str | None:
        with self.SqlSession() as session:
            team_event = TeamEventStore(
                user_id=req.user_id,
                team_id=req.team_id,
                info={
                    'type': TeamEventType.BUY_NORMAL_HINT.name,
                    'hint_id': req.hint_id,
                },
            )
            session.add(team_event)
            session.flush()
            assert team_event.id is not None, CRITICAL_ERROR
            team_event.validated_model()
            session.commit()
            self.state_counter += 1
        team_event_id: int = team_event.id
        await self.emit_event(glitter.Event(glitter.EventType.TEAM_EVENT_RECEIVED, self.state_counter, team_event_id))
        return None

    @on_action(glitter.VMe50Req)
    async def on_v_me_50(self, req: glitter.VMe50Req) -> str | None:
        with self.SqlSession() as session:
            team_event = TeamEventStore(
                user_id=req.staff_id,
                team_id=req.team_id,
                info={
                    'type': TeamEventType.STAFF_MODIFY_CURRENCY.name,
                    'currency_type': req.currency_type,
                    'delta': req.change,
                    'reason': req.reason,
                },
            )
            session.add(team_event)
            session.flush()
            assert team_event.id is not None, 'created team_event not in db'
            team_event.validated_model()
            session.commit()
            self.state_counter += 1
        team_event_id: int = team_event.id
        await self.emit_event(glitter.Event(glitter.EventType.TEAM_EVENT_RECEIVED, self.state_counter, team_event_id))
        return None

    @on_action(glitter.TeamGameBeginReq)
    async def on_team_game_begin(self, req: glitter.TeamGameBeginReq) -> str | None:
        with self.SqlSession() as session:
            team_event = TeamEventStore(
                user_id=req.user_id, team_id=req.team_id, info={'type': TeamEventType.GAME_START.name}
            )
            session.add(team_event)
            session.flush()
            assert team_event.id is not None, 'create team_event failed'
            team_event.validated_model()
            session.commit()
            self.state_counter += 1

        team_event_id: int = team_event.id
        await self.emit_event(glitter.Event(glitter.EventType.TEAM_EVENT_RECEIVED, self.state_counter, team_event_id))
        return None

    @on_action(glitter.TeamSendMsgReq)
    async def on_team_send_msg(self, req: glitter.TeamSendMsgReq) -> str | None:
        is_staff = req.direction == MessageStore.DIRECTION.TO_USER
        with self.SqlSession() as session:
            msg = MessageStore(
                team_id=req.team_id,
                user_id=req.user_id,
                content_type=req.content_type,
                content=req.content,
                # 发消息的人默认已读之前的所有消息
                player_unread=True if is_staff else False,
                staff_unread=False if is_staff else True,
                direction=req.direction,
            )
            session.add(msg)
            session.flush()
            current_msg_id: int | None = msg.id
            assert current_msg_id is not None, 'created message not in db'

            if is_staff:
                # 如果是 staff 发的信息，应当将 staff 和这个队伍以前的对话均视为 staff 已读
                # staff 只有在回信息的时候会将这个设置为已读，不回信息就一直是未读
                msgs1: Sequence[MessageStore] = (
                    session.execute(
                        select(MessageStore).where(
                            and_(
                                MessageStore.team_id == msg.team_id,
                                MessageStore.id <= msg.id,
                                MessageStore.staff_unread,
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                if len(msgs1) > 0:
                    for msg in msgs1:
                        msg.staff_unread = False
            else:
                # 虽然这里可以考虑不维护玩家已读状态，但还是考虑一下
                # 理论上来说，玩家只要点进站内信界面就会发一个已读消息的 req
                # 所以如果这时候还有未读信息，那只能说玩家自己调用的这个 api 或者哪里写出了 bug
                msgs2: Sequence[MessageStore] = (
                    session.execute(
                        select(MessageStore).where(
                            and_(
                                MessageStore.team_id == msg.team_id,
                                MessageStore.id <= msg.id,
                                MessageStore.player_unread,
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                if len(msgs2) > 0:
                    for msg in msgs2:
                        msg.player_unread = False
            # 这里不需要手动发送已读信息的 Event
            # 在发送信息的 Event 中，会自动设置已读状态

            session.commit()
            self.state_counter += 1

        if not is_staff:
            user = self._game.users.user_by_id[req.user_id]
            assert user.team is not None
            asyncio.get_event_loop().create_task(
                self.push_message(
                    f'[新消息提醒]\n'
                    f'队伍 {user.team.model.team_name} (#{req.team_id}) 发送了一条站内信\n'
                    # f"发送者: {user.store.profile.nickname_or_null} (#{req.user_id})\n"
                    f'时间: {utils.format_timestamp(msg.created_at // 1000)}\n'
                    '------------------------------------------------------------\n'
                    f'{req.content}',
                    'chat',
                )
            )
        else:
            # staff 回复站内信
            team = self._game.teams.team_by_id[req.team_id]
            user = self._game.users.user_by_id[req.user_id]
            asyncio.get_event_loop().create_task(
                self.push_message(
                    f'[消息回复记录]\n'
                    # f"工作人员 {user.store.profile.nickname_or_null} (#{req.user_id}) 回复了一条站内信\n"
                    f'目标队伍为 {team.model.team_name} (#{req.team_id})\n'
                    f'时间: {utils.format_timestamp(msg.created_at // 1000)}\n'
                    '------------------------------------------------------------\n'
                    f'{req.content}',
                    'chat',
                )
            )

        await self.emit_event(glitter.Event(glitter.EventType.NEW_MSG, self.state_counter, current_msg_id))

        return None

    @on_action(glitter.TeamReadMsgReq)
    async def on_team_read_msg(self, req: glitter.TeamReadMsgReq) -> str | None:
        is_staff = req.direction == MessageStore.DIRECTION.TO_USER
        # 不允许 staff 直接调用 read_msg 接口
        assert not is_staff

        with self.SqlSession() as session:
            # if is_staff:
            #     msgs: List[MessageStore] = session.execute(
            #         select(MessageStore)
            #         .where(and_(MessageStore.id <= req.msg_id, MessageStore.staff_unread))
            #         .order_by(MessageStore.id)
            #     ).scalars().all()
            #     if len(msgs) == 0:
            #         return None
            #     for msg in msgs:
            #         msg.staff_unread = False
            #     session.commit()
            #     last_msg_id = msgs[-1].id
            # else:
            msgs: Sequence[MessageStore] = (
                session.execute(
                    select(MessageStore)
                    .where(
                        and_(
                            MessageStore.team_id == req.team_id,
                            MessageStore.id <= req.msg_id,
                            MessageStore.player_unread,
                        )
                    )
                    .order_by(MessageStore.id)
                )
                .scalars()
                .all()
            )
            if len(msgs) == 0:
                return None
            for msg in msgs:
                msg.player_unread = False
            session.commit()

            self.state_counter += 1

        # if is_staff:
        #     await self.emit_event(glitter.Event(glitter.EventType.STAFF_READ_MSG, self.state_counter, last_msg_id))
        # else:

        await self.emit_event(glitter.Event(glitter.EventType.PLAYER_READ_MSG, self.state_counter, req.msg_id))
        return None

    @on_action(glitter.PuzzleActionReq)
    async def on_puzzle_action(self, req: glitter.PuzzleActionReq) -> str | None:
        with self.SqlSession() as session:
            team_event = TeamEventStore(
                user_id=req.user_id,
                team_id=req.team_id,
                info={
                    'type': TeamEventType.PUZZLE_ACTION.name,
                    'puzzle_key': req.puzzle_key,
                    'content': req.content,
                },
            )
            session.add(team_event)
            session.flush()
            assert team_event.id is not None, 'create team_event failed'
            team_event.validated_model()
            session.commit()
            self.state_counter += 1

        team_event_id: int = team_event.id
        await self.emit_event(glitter.Event(glitter.EventType.TEAM_EVENT_RECEIVED, self.state_counter, team_event_id))
        return None

    @on_action(glitter.TeamCreateTicketReq)
    async def on_team_create_ticket(self, req: glitter.TeamCreateTicketReq) -> str | None:
        with self.SqlSession() as session:
            ticket_store = TicketStore(
                user_id=req.user_id,
                team_id=req.team_id,
                subject=req.subject,
                status=TicketStore.TicketStatus.OPEN.name,
                type=req.ticket_type,
                extra=req.extra,
            )
            session.add(ticket_store)
            session.flush()
            assert ticket_store.id is not None, CRITICAL_ERROR

            ticket_message_store = TicketMessageStore(
                ticket_id=ticket_store.id,
                user_id=req.user_id,
                direction=TicketMessageStore.Direction.TO_STAFF.name,
                content_type=TicketMessageStore.ContentType.TEXT.name,
                content=req.first_message,
            )
            session.add(ticket_message_store)
            session.flush()
            assert ticket_message_store.id is not None, CRITICAL_ERROR
            session.commit()

            self.state_counter += 1
        # event 目前 event 只能接受一个单 int data，使用 first message 的 id 可以确定是哪个 ticket 和对应的 message
        await self.emit_event(
            glitter.Event(glitter.EventType.TEAM_CREATE_TICKET, self.state_counter, ticket_message_store.id)
        )
        return None

    @on_action(glitter.TicketMessageReq)
    async def on_ticket_message(self, req: glitter.TicketMessageReq) -> str | None:
        with self.SqlSession() as session:
            ticket_message_store = TicketMessageStore(
                ticket_id=req.ticket_id,
                user_id=req.user_id,
                direction=req.direction,
                content_type=TicketMessageStore.ContentType.TEXT.name,
                content=req.content,
            )
            session.add(ticket_message_store)
            session.flush()
            assert ticket_message_store.id is not None, CRITICAL_ERROR
            session.commit()

            self.state_counter += 1
        # event 目前 event 只能接受一个单 int data，使用 first message 的 id 可以确定是哪个 ticket 和对应的 message
        await self.emit_event(
            glitter.Event(glitter.EventType.TICKET_MESSAGE, self.state_counter, ticket_message_store.id)
        )
        return None

    @on_action(glitter.SetTicketStatusReq)
    async def on_set_ticket_status(self, req: glitter.SetTicketStatusReq) -> str | None:
        with self.SqlSession() as session:
            ticket: TicketStore | None = session.execute(
                select(TicketStore).where(TicketStore.id == req.ticket_id)
            ).scalar()
            assert ticket is not None, CRITICAL_ERROR
            ticket.status = req.status
            session.commit()
            self.state_counter += 1

        await self.emit_event(glitter.Event(glitter.EventType.TICKET_UPDATE, self.state_counter, ticket.id))
        return None

    @on_action(glitter.WorkerHeartbeatReq)
    async def on_worker_heartbeat(self, req: glitter.WorkerHeartbeatReq) -> str | None:
        self.received_telemetries[req.client] = (time.time(), req.telemetry)
        return None

    async def _update_tick(self, ts: int | None = None) -> int:  # return: when it expires
        if ts is None:
            ts = int(time.time())

        old_tick = self._game.cur_tick
        new_tick, expires = self._game.trigger.get_tick_at_time(ts)

        # DO NOT SET self._game.cur_tick = new_tick HERE because emit_event will process this and fire `on_tick_update`
        if new_tick != old_tick:
            self.log('info', 'reducer.update_tick', f'set tick {old_tick} -> {new_tick}')

            self.state_counter += 1
            await self.emit_event(glitter.Event(glitter.EventType.TICK_UPDATE, self.state_counter, new_tick))

        return expires

    async def _tick_updater_daemon(self) -> None:
        ts = time.time()
        while True:
            expires = await self._update_tick(int(ts))
            self.log(
                'debug',
                'reducer.tick_updater_daemon',
                f'next tick in {"+INF" if expires == Trigger.TS_INF_S else int(expires - ts)} seconds',
            )
            await asyncio.sleep(expires - ts + 0.2)
            ts = expires

    async def _announcement_updater_daemon(self) -> None:
        ts = time.time()
        while True:
            next_announcement_ts = self._game.announcements.next_announcement_ts
            if ts < next_announcement_ts:
                self.log(
                    'debug',
                    'reducer.announcement_updater_daemon',
                    f'next tick in {"+INF" if next_announcement_ts == Announcements.TS_INF_S else int(next_announcement_ts - ts)} seconds',
                )
                await asyncio.sleep(next_announcement_ts - ts + 0.2)
                ts = next_announcement_ts
            else:
                self.state_counter += 1
                self.log(
                    'info',
                    'reducer.update_announcement',
                    f'new announcement at {utils.format_timestamp(next_announcement_ts)}',
                )
                await self.emit_event(
                    glitter.Event(glitter.EventType.ANNOUNCEMENT_PUBLISH, self.state_counter, next_announcement_ts)
                )

    async def _health_check_daemon(self) -> None:
        while True:
            await asyncio.sleep(300)

            ws_online_uids = 0
            ws_online_clients = 0

            ts = time.time()
            for client, (last_ts, tel_data) in self.received_telemetries.items():
                if client != self.process_name and ts - last_ts > 60:
                    self.log(
                        'error', 'reducer.health_check_daemon', f'client {client} not responding in {ts - last_ts:.1f}s'
                    )
                if not tel_data.get('game_available', True):
                    self.log('error', 'reducer.health_check_daemon', f'client {client} game not available')

                ws_online_uids += tel_data.get('ws_online_uids', 0)
                ws_online_clients += tel_data.get('ws_online_clients', 0)

            st = utils.sys_status()
            if st['load_5'] > st['n_cpu'] * secret.HEALTH_CHECK_THROTTLE.get('cpu_throttle', 2 / 3):
                self.log(
                    'error',
                    'reducer.health_check_daemon',
                    f'system load too high: {st["load_1"]:.2f} {st["load_5"]:.2f} {st["load_15"]:.2f}',
                )
            if st['ram_free'] / st['ram_total'] < secret.HEALTH_CHECK_THROTTLE.get('ram_throttle', 0.2):
                self.log(
                    'error',
                    'reducer.health_check_daemon',
                    f'free ram too low: {st["ram_free"]:.2f}G out of {st["ram_total"]:.2f}G',
                )
            if st['disk_free'] / st['disk_total'] < secret.HEALTH_CHECK_THROTTLE.get('disk_throttle', 0.1):
                self.log(
                    'error',
                    'reducer.health_check_daemon',
                    f'free space too low: {st["disk_free"]:.2f}G out of {st["disk_total"]:.2f}G',
                )

            encoded = json.dumps(
                [
                    time.time(),
                    {
                        'load': [st['load_1'], st['load_5'], st['load_15']],
                        'ram': [st['ram_used'], st['ram_free']],
                        'n_user': len(self._game.users.list),
                        'n_online_uid': ws_online_uids,
                        'n_online_client': ws_online_clients,
                        'n_submission': len(self._game.submissions_by_id),
                        'n_corr_submission': self._game.n_corr_submission,
                    },
                ]
            ).encode('utf-8')

            with (secret.SYBIL_LOG_PATH / 'sys.log').open('ab') as f:
                f.write(encoded + b'\n')

    async def handle_action(self, action: glitter.Action) -> ActionResult:
        async def default(_self: Any, req: glitter.ActionReq) -> ActionResult:
            return {'status': 'error', 'title': 'UNKNOWN_ACTION', 'message': f'unknown action: {req.type}'}

        check_result = await self.checker.check_action(action.req)
        if check_result is not None:
            return check_result

        listener: Callable[[Any, glitter.ActionReq], Awaitable[ActionResult]] = self.action_listeners.get(
            type(action.req), default
        )

        with utils.log_slow(self.log, 'reducer.handle_action', f'handle action {action.req.type}'):
            listener_result = await listener(self, action.req)
            # TODO: 可以在这里自动打包 dict
            return listener_result

    async def process_event(self, event: glitter.Event) -> None:
        await super().process_event(event)
        if event.type == glitter.EventType.UPDATE_ANNOUNCEMENT:
            if self.announcement_updater_task is not None:
                self.announcement_updater_task.cancel()
                self.announcement_updater_task = asyncio.create_task(self._announcement_updater_daemon())
        if event.type == glitter.EventType.RELOAD_TRIGGER:
            # restart tick updater deamon because next tick time may change
            if self.tick_updater_task is not None:
                self.tick_updater_task.cancel()
                self.tick_updater_task = asyncio.create_task(self._tick_updater_daemon())

    async def emit_event(self, event: glitter.Event) -> None:
        self.log('info', 'reducer.emit_event', f'emit event {event.type}')
        await self.process_event(event)

        with utils.log_slow(self.log, 'reducer.emit_event', f'emit event {event.type}'):
            await event.send(self.event_socket)

    async def emit_sync(self) -> None:
        if time.time() - self.last_emit_sync_time <= self.SYNC_THROTTLE_S:
            return
        self.last_emit_sync_time = time.time()

        # self.log('debug', 'reducer.emit_sync', f'emit sync ({self.state_counter})')
        with utils.log_slow(self.log, 'reducer.emit_sync', 'emit sync'):
            await glitter.Event(glitter.EventType.SYNC, self.state_counter, self._game.cur_tick).send(self.event_socket)

    async def _mainloop(self) -> None:
        self.log('success', 'reducer.mainloop', 'started to receive actions')
        self.announcement_updater_task = asyncio.create_task(self._announcement_updater_daemon())
        self.tick_updater_task = asyncio.create_task(self._tick_updater_daemon())
        self.health_check_task = asyncio.create_task(self._health_check_daemon())

        while True:
            try:
                action: glitter.Action | None = await glitter.Action.listen(self.action_socket)
            except zmq.error.Again:  # timeout, means no action in this interval
                await self.emit_sync()
                continue
            except Exception as e:
                self.log('error', 'reducer.mainloop', f'exception during action receive, will try again: {e}')
                await self.emit_sync()
                await asyncio.sleep(self.SYNC_INTERVAL_S)
                continue

            if action is None:
                continue

            if isinstance(action.req, glitter.WorkerHelloReq):
                self.log('debug', 'reducer.mainloop', f'got worker hello from {action.req.client}')
            elif isinstance(action.req, glitter.WorkerHeartbeatReq):
                pass
            else:
                self.log('info', 'reducer.mainloop', f'got action {action.req.type} from {action.req.client}')

            old_counter = self.state_counter

            try:
                err = await self.handle_action(action)

                if err is not None and action.req.type != 'SubmitAnswerReq':
                    self.log('warning', 'reducer.handle_action', f'error for action {action.req.type}: {err}')
            except Exception as e:
                self.log(
                    'critical',
                    'reducer.handle_action',
                    f'exception, will report as internal error: {utils.get_traceback(e)}',
                )
                err = {
                    'status': 'error',
                    'title': 'INTERNAL_ERROR',
                    'message': '内部错误，已记录日志，如果您经常遇到此问题，请反馈给工作人员。',
                }

            if self.state_counter != old_counter:
                self.log('debug', 'reducer.mainloop', f'state counter {old_counter} -> {self.state_counter}')

            assert self.state_counter - old_counter in [0, 1], 'action handler incremented state counter more than once'

            try:
                if action is not None:
                    with utils.log_slow(self.log, 'reducer.mainloop', f'reply to action {action.req.type}'):
                        await action.reply(
                            glitter.ActionRep(result=err, state_counter=self.state_counter), self.action_socket
                        )

                if not isinstance(action.req, glitter.WorkerHeartbeatReq):
                    await self.emit_sync()
            except Exception as e:
                self.log(
                    'critical',
                    'reducer.mainloop',
                    f'exception during action reply, will recover: {utils.get_traceback(e)}',
                )
                self.state_counter = 1  # then workers will re-sync themselves
                continue
