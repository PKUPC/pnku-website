from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from src import utils
from src.state.base import WithGameLifecycle


if TYPE_CHECKING:
    from src.state import Game, Team, User

    ScoreBoardItemType = tuple[Team, int]


class Board(WithGameLifecycle, ABC):
    def __init__(self, board_type: str, key: str, name: str, desc: str | None, game: Game):
        self.board_type = board_type
        self.key = key
        self.name = name
        self.desc = desc
        self._game = game
        self._rendered_admin: dict[str, Any] | None = None
        self._rendered_normal: dict[str, Any] | None = None

        self.etag_admin = utils.gen_random_str(24)
        self.etag_normal = utils.gen_random_str(24)

    def get_rendered(self, is_admin: bool) -> dict[str, Any]:
        if is_admin:
            if self._rendered_admin is None:
                with utils.log_slow(
                    self._game.worker.log, 'board.render', f'render {self.board_type} board (admin) {self.name}'
                ):
                    self._rendered_admin = self._render(is_admin=True)

            return self._rendered_admin
        else:
            if self._rendered_normal is None:
                with utils.log_slow(
                    self._game.worker.log, 'board.render', f'render {self.board_type} board {self.name}'
                ):
                    self._rendered_normal = self._render(is_admin=False)

            return self._rendered_normal

    def get_more_info(self, user: User) -> dict[str, Any]:
        return {}

    def clear_render_cache(self) -> None:
        self._rendered_admin = None
        self._rendered_normal = None

    @staticmethod
    def _admin_knowledge(team: Team) -> list[dict[str, str]]:
        """
        用于在排行榜上显示一些 staff 才能看到的信息
        默认是用 antd 的 tag 表示的，需要 text 和 color 两个字段，示例如下：

        [
            {
                'text': 'haha',
                'color': 'default',
            }
        ]

        """
        return []

    @abstractmethod
    def _render(self, is_admin: bool) -> dict[str, Any]:
        raise NotImplementedError()

    def on_tick_change(self) -> None:
        self.clear_render_cache()
