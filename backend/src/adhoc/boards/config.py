from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Board
from .first_blood_board import FirstBloodBoard
from .score_board import ScoreBoard
from .speed_run_board import SpeedRunBoard


if TYPE_CHECKING:
    from src.state import Game


def get_boards(game: Game) -> dict[str, Board]:
    return {
        'score_board': ScoreBoard('score_board', '排名', None, game),
        'first_blood': FirstBloodBoard('first_blood', '一血榜', None, game),
        'speed_run': SpeedRunBoard(
            'speed_run', '速通榜', '本榜仅供参考！注：由于开赛时服务器出现问题，前 5 题是直接公开的。', game
        ),
    }
