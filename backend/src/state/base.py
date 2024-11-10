from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .team_event_state import TeamEvent


class WithGameLifecycle(ABC):
    def on_tick_change(self) -> None:
        pass

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        pass

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        pass

    def on_team_event_reload_done(self) -> None:
        pass
