from __future__ import annotations

import asyncio
import time

from typing import TYPE_CHECKING, Optional

import zmq

from sanic.request import Request
from zmq.asyncio import Socket

from .. import secret, utils
from . import glitter
from .base import StateContainerBase
from .glitter import WorkerHeartbeatReq


if TYPE_CHECKING:
    pass


class Worker(StateContainerBase):
    RECOVER_INTERVAL_S = 3
    HEARTBEAT_THROTTLE_S = 9
    HEARTBEAT_TIMEOUT_S = 7

    def __init__(self, process_name: str, receiving_messages: bool = False):
        super().__init__(process_name, receiving_messages=receiving_messages)

        self.action_socket: Socket = self.glitter_ctx.socket(zmq.REQ)
        self.event_socket: Socket = self.glitter_ctx.socket(zmq.SUB)

        self.action_socket.setsockopt(zmq.RCVTIMEO, glitter.CALL_TIMEOUT_MS)
        self.action_socket.setsockopt(zmq.SNDTIMEO, glitter.CALL_TIMEOUT_MS)
        self.action_socket.setsockopt(zmq.REQ_RELAXED, 1)
        self.event_socket.setsockopt(zmq.RCVTIMEO, glitter.SYNC_TIMEOUT_MS)

        self.action_socket.connect(secret.GLITTER_ACTION_SOCKET_ADDR)
        self.event_socket.connect(secret.GLITTER_EVENT_SOCKET_ADDR)
        self.event_socket.setsockopt(zmq.SUBSCRIBE, b'')

        self.state_counter = -1
        self.state_counter_cond: asyncio.Condition = asyncio.Condition()

        self.last_heartbeat_time: float = 0
        self._heartbeat_task: asyncio.Task[None] | None = None

    async def _sync_with_reducer(self, *, throttled: bool = True) -> None:
        self.game_dirty = True
        self.log('debug', 'reducer.sync_with_reducer', 'sent handshake')

        while True:
            try:
                hello_res = await glitter.Action(
                    glitter.WorkerHelloReq(client=self.process_name, protocol_ver=glitter.PROTOCOL_VER)
                ).call(self.action_socket)
            except Exception as e:
                self.log(
                    'error',
                    'reducer.before_run',
                    f'exception during handshake, will try again: {utils.get_traceback(e)}',
                )
                await asyncio.sleep(self.RECOVER_INTERVAL_S)
            else:
                if hello_res.result is not None:
                    self.log('critical', 'worker.before_run', f'handshake failure: {hello_res.result}')
                    raise RuntimeError(f'handshake failure: {hello_res.result}')

                break

        self.log('debug', 'worker.sync_with_reducer', 'begin sync')

        while True:
            try:
                # need to reconstruct current tick from a sync frame
                while True:
                    event = await glitter.Event.next(self.event_socket)
                    if event.type == glitter.EventType.SYNC:
                        break

                self.log(
                    'info', 'worker.sync_with_reducer', f'got sync data, tick={event.data}, count={event.state_counter}'
                )
                self.state_counter = event.state_counter
                await self.init_game(event.data)

                async with self.state_counter_cond:
                    self.state_counter_cond.notify_all()
            except Exception as e:
                self.log(
                    'error',
                    'worker.sync_with_reducer',
                    f'exception during sync, will try again: {utils.get_traceback(e)}',
                )
                await asyncio.sleep(self.RECOVER_INTERVAL_S)
            else:
                break

        self.log('debug', 'worker.sync_with_reducer', 'game state reconstructed')

        if throttled:
            await asyncio.sleep(self.RECOVER_THROTTLE_S)
        self.game_dirty = False

    async def _before_run(self) -> None:
        self.log('debug', 'worker.before_run', 'before_run')
        await super()._before_run()

        # reduce the possibility of losing initial event_socket packets
        # (we are still sound in this case, but some time is wasted waiting for next SYNC)
        await asyncio.sleep(0.4)

        await self._sync_with_reducer(throttled=False)

    async def _mainloop(self) -> None:
        self.log('success', 'worker.mainloop', 'started to receive events')
        while True:
            try:
                event = await glitter.Event.next(self.event_socket)
            except zmq.error.Again as e:
                self.log('warning', 'worker.mainloop', f'event receive timeout, will recover: {utils.get_traceback(e)}')
                await self._sync_with_reducer()
                continue
            except Exception as e:
                self.log(
                    'error',
                    'worker.mainloop',
                    f'exception during event receive, will recover: {utils.get_traceback(e)}',
                )
                await self._sync_with_reducer()
                continue

            # in rare cases when zeromq reaches high-water-mark, we may lose packets!
            if event.state_counter not in [self.state_counter, self.state_counter + 1]:
                if event.state_counter < self.state_counter:
                    self.log(
                        'warning',
                        'worker.mainloop',
                        f'state counter mismatch, maybe reducer restarted, will recover: worker {self.state_counter} reducer {event.state_counter}',
                    )
                else:
                    self.log(
                        'error',
                        'worker.mainloop',
                        f'state counter mismatch, maybe lost event, will recover: worker {self.state_counter} reducer {event.state_counter}',
                    )
                await self._sync_with_reducer()
            else:
                self.state_counter = event.state_counter
                await self.process_event(event)
                async with self.state_counter_cond:
                    self.state_counter_cond.notify_all()

                # send heartbeat if needed
                self._heartbeat_task = asyncio.create_task(self.send_heartbeat())

    async def perform_action(self, req: glitter.ActionReq, http_req: Request | None = None) -> glitter.ActionRep:
        if req.type != 'WorkerHeartbeatReq':
            self.log('info', 'worker.perform_action', f'call {req.type}')

        # 参数检查
        check_result = await self.checker.check_action(req, http_req)
        if check_result is not None:
            return glitter.ActionRep(result=utils.pack_rep(check_result), state_counter=-1)

        with utils.log_slow(self.log, 'worker.perform_action', f'perform action {req.type}'):
            rep = await glitter.Action(req).call(self.action_socket)

        if req.type != 'WorkerHeartbeatReq':
            self.log('debug', 'worker.perform_action', f'called {req.type}, state counter is {rep.state_counter}')

        # rep中的 state_counter 表示这个请求处理完时所处的状态，reducer 每次emit event会更新一次状态
        # 每个 worker 轮流处理自己队列中的状态，当处理到rep中的state_counter后，说明这个请求对应的操作
        # 已经处理完了
        # sync state after call
        if rep.state_counter > self.state_counter:
            try:
                async with self.state_counter_cond:
                    cond = self.state_counter_cond.wait_for(lambda: self.state_counter >= rep.state_counter)
                    await asyncio.wait_for(cond, glitter.CALL_TIMEOUT_MS / 1000)
            except TimeoutError:
                self.log(
                    'error', 'worker.perform_action', f'state sync timeout: {self.state_counter} -> {rep.state_counter}'
                )
                raise RuntimeError('timed out syncing state with reducer')

            self.log('debug', 'worker.perform_action', f'state counter synced to {self.state_counter}')

        return rep

    async def process_event(self, event: glitter.Event) -> None:
        if event.type != glitter.EventType.SYNC:
            self.log(
                'debug', 'worker.process_event', f'got event {event.type} {event.data} (count={event.state_counter})'
            )
        await super().process_event(event)

    async def send_heartbeat(self) -> None:
        if time.time() - self.last_heartbeat_time <= self.HEARTBEAT_THROTTLE_S:
            return
        self.last_heartbeat_time = time.time()

        try:
            await asyncio.wait_for(
                self.perform_action(WorkerHeartbeatReq(client=self.process_name, telemetry=self.collect_telemetry())),
                self.HEARTBEAT_TIMEOUT_S,
            )

            # periodically wake up ws so it has opportunity to quit if ws is closed
            self.emit_ws_message({'type': 'heartbeat_sent', 'payload': {}})
        except Exception as e:
            self.log('error', 'worker.mainloop', f'heartbeat error, will ignore: {utils.get_traceback(e)}')
