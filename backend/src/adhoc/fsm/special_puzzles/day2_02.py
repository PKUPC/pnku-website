from __future__ import annotations

import time

from collections.abc import Hashable
from typing import TYPE_CHECKING

from ..team_puzzle_status import TeamPuzzleStatus


if TYPE_CHECKING:
    from src.state import Puzzle, Team
    from src.store import PuzzleActionEvent

    from ..team_game_state import TeamGameStatus


class Day202Status(TeamPuzzleStatus):
    def __init__(self, game_status: TeamGameStatus, team: Team, puzzle: Puzzle):
        super().__init__(game_status, team, puzzle)
        self.real_seconds = -1
        self.target_seconds = -1

    def get_render_info(self) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        virtual_seconds = int(time.time())
        if self.real_seconds != -1:
            virtual_seconds = virtual_seconds - self.real_seconds + self.target_seconds
        else:
            virtual_seconds += 8 * 3600
        virtual_hour = (virtual_seconds // 3600) % 24
        virtual_minute = (virtual_seconds // 60) % 60
        return ('hour', virtual_hour), ('minute', virtual_minute)

    def on_puzzle_action(self, event: PuzzleActionEvent) -> None:
        self.real_seconds = int(event.content.get('real_seconds', -1))
        self.target_seconds = int(event.content.get('target_seconds', -1))
