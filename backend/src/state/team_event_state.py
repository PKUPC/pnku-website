from __future__ import annotations

from typing import TYPE_CHECKING

from ..store import TeamEventStore, StaffModifyApEvent, BuyNormalHintEvent

if TYPE_CHECKING:
    from . import Game


class TeamEvent:
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, store: TeamEventStore):
        assert store.id not in TeamEvent.constructed_ids
        TeamEvent.constructed_ids.add(store.id)
        # team event 的 store 是不会变的
        self.game: Game = game
        self._store: TeamEventStore = store
        self.model = self._store.validated_model()

        assert self._store.team_id in self.game.teams.team_by_id
        self.team = self.game.teams.team_by_id[self._store.team_id]
        self.ap_change = 0

    def describe_cost(self) -> str:
        match self.model.info:
            case StaffModifyApEvent():
                if self.ap_change < 0:
                    desc = f"工作人员扣除了注意力，原因是："
                else:
                    desc = f"工作人员发放了注意力，原因是："
                desc += self.model.info.reason
                return desc
            case BuyNormalHintEvent(hint_id=hint_id):
                assert hint_id in self.game.hints.hint_by_id
                hint = self.game.hints.hint_by_id[hint_id]
                puzzle = self.game.puzzles.puzzle_by_key[hint.model.puzzle_key]
                user = self.game.users.user_by_id.get(self.model.user_id, None)
                user_name = user.model.user_info.nickname if user is not None else "未知"
                # 『 』
                desc = f"玩家 {user_name} 购买了题目《{puzzle.model.title}》的提示，提示类型为『{hint.describe_type()}』，"
                desc += f"提示标题为：\"{hint.model.question}\""
                return desc
            case _:
                assert False, "wrong team event type"

    def ap_change_or_zero(self) -> int:
        # TODO
        return 0

    def __repr__(self) -> str:
        return self._store.__repr__()
