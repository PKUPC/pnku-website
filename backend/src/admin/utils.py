from __future__ import annotations

import asyncio

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from flask import current_app

from src.logic import glitter


if TYPE_CHECKING:
    from src.logic.reducer import Reducer

T = TypeVar('T')


def run_reducer_callback(callback: Callable[[Reducer], T]) -> T:
    loop: asyncio.AbstractEventLoop = current_app.config['reducer_loop']
    reducer: Reducer = current_app.config['reducer_obj']

    async def task() -> T | Exception:
        try:
            return callback(reducer)
        except Exception as e:
            return e

    future = asyncio.run_coroutine_threadsafe(task(), loop)
    result = future.result()
    if isinstance(result, Exception):
        raise result
    return result


def emit_event(event_type: glitter.EventType, id: int | None = None) -> None:
    loop: asyncio.AbstractEventLoop = current_app.config['reducer_loop']
    reducer: Reducer = current_app.config['reducer_obj']

    async def task() -> None:
        reducer.state_counter += 1
        event = glitter.Event(event_type, reducer.state_counter, id or 0)
        await reducer.emit_event(event)

    asyncio.run_coroutine_threadsafe(task(), loop)
