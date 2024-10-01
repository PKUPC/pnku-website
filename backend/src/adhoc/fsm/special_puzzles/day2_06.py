from __future__ import annotations

import time
from typing import Hashable, Any, TYPE_CHECKING

from src import utils
from ..team_puzzle_status import TeamPuzzleStatus

if TYPE_CHECKING:
    from src.state import Team, Puzzle
    from ..team_game_state import TeamGameStatus


def get_media_name(seconds: int, team_id: int) -> str:
    num_map = [4, 9, 3, 5, 13, 17, 14, 2, 15, 16, 7, 11, 12, 10, 6, 8, 18, 1]
    name_map = ["music", "road", "question", "weather"]
    num_index = (seconds // 600) % 18
    num = num_map[num_index]
    name_index = (team_id * 10000 + (seconds // 600) + 3) % 4
    name = name_map[name_index]
    return name + str(num)


class Day206Status(TeamPuzzleStatus):

    def __init__(self, game_status: TeamGameStatus, team: Team, puzzle: Puzzle):
        super().__init__(game_status, team, puzzle)
        self.media_url = ""
        self.second_difference = -1

    def _set_current_media_url(self) -> None:
        current_seconds = int(time.time())
        game_start_timestamp = self.team.game.game_begin_timestamp_s
        second_difference = current_seconds - game_start_timestamp
        media_name = get_media_name(second_difference, self.team.model.id)
        self.media_url = utils.media_wrapper(f"puzzle/day2_06/32k_{media_name}.m4a")
        self.second_difference = second_difference

    def get_render_info(self) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        self._set_current_media_url()
        second_difference = self.second_difference
        days = (second_difference // 86400) % 9
        second_difference %= 86400
        hours = second_difference // 3600
        second_difference %= 3600
        minutes = second_difference // 60

        return (
            ("media_url", self.media_url),
            ("day", days), ("hours", hours), ("minutes", minutes)
        )

    def get_dyn_actions(self) -> list[dict[str, Any]]:
        self._set_current_media_url()
        return [
            {
                "type": "media",
                "name": "音频文件",
                "media_url": self.media_url,
            }
        ]
