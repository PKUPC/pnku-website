from __future__ import annotations

import time

from typing import Hashable

from src import utils

from ..team_puzzle_status import TeamPuzzleStatus


class Day203Status(TeamPuzzleStatus):
    def get_render_info(self) -> tuple[tuple[str, str | int | tuple[Hashable, ...]], ...]:
        game_start_seconds = self.team.game.game_begin_timestamp_s
        current_seconds = int(time.time())
        hours = (current_seconds - game_start_seconds) // 3600
        id1 = hours % 6 + 1
        id2 = hours % 8 + 1
        id3 = hours % 4 + 1
        id4 = hours % 5 + 1
        id5 = hours % 7 + 1
        id6 = hours % 9 + 1

        fig1 = f'puzzle/day2_03/SUB1/SUB1-{id1}.webp'
        fig2 = f'puzzle/day2_03/SUB2/SUB2-{id2}.webp'
        fig3 = f'puzzle/day2_03/SUB3/SUB3-{id3}.webp'
        fig4 = f'puzzle/day2_03/SUB4/SUB4-{id4}.webp'
        fig5 = f'puzzle/day2_03/SUB5_v3/SUB5-{id5}.webp'
        fig6 = f'puzzle/day2_03/SUB6_v2/SUB6-{id6}.webp'

        return (
            ('fig1', utils.media_wrapper(fig1)),
            ('fig2', utils.media_wrapper(fig2)),
            ('fig3', utils.media_wrapper(fig3)),
            ('fig4', utils.media_wrapper(fig4)),
            ('fig5', utils.media_wrapper(fig5)),
            ('fig6', utils.media_wrapper(fig6)),
        )
