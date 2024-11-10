from __future__ import annotations

import time

from typing import TYPE_CHECKING, Dict, List, Optional, Set

from src.store import HintStore, HintStoreModel

from .base import WithGameLifecycle


if TYPE_CHECKING:
    from . import Game


class Hints(WithGameLifecycle):
    constructed: bool = False

    def __init__(self, game: Game, stores: list[HintStore]):
        assert not Hints.constructed
        Hints.constructed = True
        self.game: Game = game

        self.list: list[Hint] = []
        self.hint_by_id: Dict[int, Hint] = {}

        # 游戏逻辑相关，hint 分为所有人可见的和特定队伍可见的，分开管理
        self.hint_by_key: dict[str, list[Hint]] = {}

        for store in stores:
            self.list.append(Hint(self.game, store))
        self._after_store_update()

    def _after_store_update(self) -> None:
        self.hint_by_id = {}
        self.hint_by_key = {}

        def sorter(x: Hint) -> tuple[int, int, int]:
            type_id = -1
            if x.model.type == 'BASIC':
                type_id = 1
            elif x.model.type == 'NORMAL':
                type_id = 2
            elif x.model.type == 'ADVANCE':
                type_id = 3

            return type_id, x.model.id, x.model.effective_after_ts

        self.list = sorted(self.list, key=sorter)

        for hint in self.list:
            if not hint.model.enable:
                continue
            self.hint_by_id[hint.model.id] = hint

            self.hint_by_key.setdefault(hint.model.puzzle_key, [])
            self.hint_by_key[hint.model.puzzle_key].append(hint)

    def on_store_update(self, hint_id: int, new_store: Optional[HintStore]) -> None:
        old_hint_list: List[Hint] = [x for x in self.list if x.model.id == hint_id]

        if len(old_hint_list) == 0:  # add
            assert new_store is not None
            self.list.append(Hint(self.game, new_store))
        elif new_store is None:  # delete
            Hint.constructed_ids.remove(hint_id)
            self.list = [x for x in self.list if x.model.id != hint_id]
            # 需要重新计算队伍的 ap 花费
            self.game.need_reload_team_event = True
        else:  # modify
            if old_hint_list[0].model.enable and not new_store.enable:
                self.game.need_reload_team_event = True
            old_hint_list[0].on_store_update(new_store)

        self._after_store_update()

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        for hint in self.list:
            hint.on_preparing_to_reload_team_event(reloading_type)


class Hint(WithGameLifecycle):
    constructed_ids: Set[int] = set()

    def __init__(self, game: Game, store: HintStore):
        assert store.id not in Hint.constructed_ids
        Hint.constructed_ids.add(store.id)

        self.game: Game = game
        self._store: HintStore = store
        self.model: HintStoreModel = store.validated_model()
        assert self.model.puzzle_key in self.game.puzzles.puzzle_by_key
        self.puzzle = self.game.puzzles.puzzle_by_key[self.model.puzzle_key]

    def on_store_update(self, new_store: HintStore) -> None:
        self._store = new_store
        self.model = new_store.validated_model()

    @property
    def effective(self) -> bool:
        if not self.model.enable:
            return False
        if self.model.effective_after_ts > int(time.time()):
            return False
        return True

    @property
    def current_cost(self) -> int:
        base_cost = self.model.extra.cost
        return base_cost

    def describe_type(self) -> str:
        return HintStore.HintType.dict().get(self.model.type, '未知')

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        pass

    def __repr__(self) -> str:
        return self.model.__repr__()
