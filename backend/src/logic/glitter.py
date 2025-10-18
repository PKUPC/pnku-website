from __future__ import annotations

import asyncio
import json
import pickle

from dataclasses import dataclass
from enum import Enum, unique
from typing import Any, Literal

from zmq.asyncio import Socket

from .. import secret, utils


PROTOCOL_VER = 'glitter.alpha.v2'


@unique
class EventType(Enum):
    SYNC = b'\x01'

    RELOAD_GAME_POLICY = b'\x11'
    RELOAD_TRIGGER = b'\x12'

    UPDATE_ANNOUNCEMENT = b'\x21'
    UPDATE_PUZZLE = b'\x22'

    UPDATE_USER = b'\x23'
    NEW_MSG = b'\x26'
    STAFF_READ_MSG = b'\x27'
    PLAYER_READ_MSG = b'\x28'
    UPDATE_MESSAGE = b'\x29'

    NEW_SUBMISSION = b'\x31'
    TICK_UPDATE = b'\x32'
    ANNOUNCEMENT_PUBLISH = b'\x33'

    CREATE_TEAM = b'\x40'
    UPDATE_TEAM_INFO = b'\x41'
    JOIN_TEAM = b'\x42'
    LEAVE_TEAM = b'\x43'
    DISSOLVE_TEAM = b'\x44'
    CHANGE_TEAM_LEADER = b'\x45'
    TEAM_GAME_BEGIN = b'\x46'

    UPDATE_HINT = b'\x50'
    TEAM_EVENT_RECEIVED = b'\x51'

    TEAM_CREATE_TICKET = b'\x60'
    TICKET_MESSAGE = b'\x61'
    TICKET_UPDATE = b'\x62'
    UPDATE_TICKET_MESSAGE = b'\x63'

    REINIT_GAME = b'\x99'


@dataclass
class ActionReq:
    client: str

    @property
    def type(self) -> str:
        return type(self).__name__


@dataclass
class WorkerHeartbeatReq(ActionReq):
    telemetry: dict[str, Any]


@dataclass
class WorkerHelloReq(ActionReq):
    protocol_ver: str


@dataclass
class UserRegReq(ActionReq):
    login_key: str
    login_properties: dict[str, Any]
    init_info: dict[str, Any]
    group: str


@dataclass
class UserResetReq(ActionReq):
    login_key: str
    login_properties: dict[str, Any]
    group: str


@dataclass
class UserUpdateProfileReq(ActionReq):
    uid: int
    profile: dict[str, str | int]


@dataclass
class UserCreateTeamReq(ActionReq):
    uid: int
    team_name: str
    team_info: str
    team_secret: str


@dataclass
class TeamUpdateInfoReq(ActionReq):
    uid: int
    tid: int
    team_name: str
    team_info: str
    team_secret: str


@dataclass
class TeamUpdateExtraTeamInfoReq(ActionReq):
    uid: int
    tid: int
    info_type: str
    data: dict[str, Any]


@dataclass
class UserJoinTeamReq(ActionReq):
    uid: int
    tid: int
    team_secret: str


@dataclass
class UserLeaveTeamReq(ActionReq):
    uid: int
    tid: int


@dataclass
class TeamRemoveUserReq(ActionReq):
    from_id: int
    uid: int
    tid: int


@dataclass
class TeamChangeLeaderReq(ActionReq):
    from_id: int
    uid: int
    tid: int


@dataclass
class UserAgreeTermReq(ActionReq):
    uid: int


@dataclass
class SubmitAnswerReq(ActionReq):
    user_id: int
    puzzle_key: str
    content: str


@dataclass
class TeamSendMsgReq(ActionReq):
    user_id: int
    team_id: int
    content_type: str
    content: str
    direction: str


@dataclass
class TeamReadMsgReq(ActionReq):
    team_id: int
    msg_id: int
    direction: str


@dataclass
class TeamBuyHintReq(ActionReq):
    user_id: int
    team_id: int
    hint_id: int
    puzzle_key: str


@dataclass
class TeamCreateTicketReq(ActionReq):
    extra: dict[str, Any]
    user_id: int
    team_id: int
    ticket_type: str
    subject: str
    first_message: str


@dataclass
class TicketMessageReq(ActionReq):
    ticket_id: int
    user_id: int
    direction: str
    content_type: str
    content: str


@dataclass
class SetTicketStatusReq(ActionReq):
    user_id: int
    ticket_id: int
    status: Literal['OPEN', 'CLOSED']


@dataclass
class VMe50Req(ActionReq):
    staff_id: int
    team_id: int
    currency_type: str
    change: int
    reason: str


@dataclass
class PuzzleActionReq(ActionReq):
    user_id: int
    team_id: int
    puzzle_key: str
    content: dict[str, str | int]


@dataclass
class TeamGameBeginReq(ActionReq):
    user_id: int
    team_id: int


ActionResult = dict[str, Any] | None


@dataclass
class ActionRep:
    result: ActionResult
    state_counter: int


CALL_TIMEOUT_MS = 5000


class Action:
    _lock: asyncio.Lock | None = None

    def __init__(self, req: ActionReq):
        self.req: ActionReq = req

    async def _send_req(self, sock: Socket) -> None:
        await sock.send_multipart([secret.GLITTER_SSRF_TOKEN.encode(), pickle.dumps(self.req)])

    @staticmethod
    async def _recv_rep(sock: Socket) -> ActionRep:
        parts = await sock.recv_multipart()
        assert len(parts) == 1, 'malformed action rep packet: should contain one part'
        rep = pickle.loads(parts[0])
        assert isinstance(rep, ActionRep)
        return rep

    # client

    async def call(self, sock: Socket) -> ActionRep:
        if Action._lock is None:
            Action._lock = asyncio.Lock()

        async with Action._lock:
            await self._send_req(sock)
            ret = await self._recv_rep(sock)
            return ret

    # server

    @classmethod
    async def listen(cls, sock: Socket) -> Action | None:
        pkt = await sock.recv_multipart()
        try:
            assert len(pkt) == 2, 'action req packet should contain one part'
            assert pkt[0] == secret.GLITTER_SSRF_TOKEN.encode(), 'invalid ssrf token'
            data = pickle.loads(pkt[1])
            assert isinstance(data, ActionReq), 'malformed action req packet body'
            return cls(data)
        except Exception as e:
            print(utils.get_traceback(e))
            await sock.send_multipart(
                [
                    json.dumps(
                        {
                            'error_msg': 'malformed packet',
                            'state_counter': -1,
                        }
                    ).encode('utf-8')
                ]
            )
            return None

    @staticmethod
    async def reply(rep: ActionRep, sock: Socket) -> None:
        await sock.send_multipart([pickle.dumps(rep)])


SYNC_TIMEOUT_MS = 7000


class Event:
    def __init__(self, type: EventType, state_counter: int, data: int):
        self.type: EventType = type
        self.state_counter: int = state_counter
        self.data: int = data

    # client

    @classmethod
    async def next(cls, sock: Socket) -> Event:
        type, ts, id = await sock.recv_multipart()
        event_type = EventType(type)
        cnt = int(ts.decode('utf-8'))
        data = int(id.decode('utf-8'))
        return cls(type=event_type, state_counter=cnt, data=data)

    # server

    async def send(self, sock: Socket) -> None:
        data: list[bytes] = [
            self.type.value,
            str(self.state_counter).encode('utf-8'),
            str(self.data).encode('utf-8'),
        ]
        await sock.send_multipart(data)
