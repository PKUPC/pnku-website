from __future__ import annotations

import time

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from src.store import AnnouncementStore

from .. import utils


if TYPE_CHECKING:
    from . import Game, User


class Announcements:
    TS_INF_S = 90000000000  # a timestamp in the future. actually at 4821-12-27

    def __init__(self, game: Game, stores: list[AnnouncementStore]):
        self._game: Game = game
        self.list: list[Announcement] = []
        self.list_by_time: list[Announcement] = []
        self.on_store_reload(stores)
        self.last_push_time = int(time.time())

    def _sort_list(self) -> None:
        self.list = sorted(self.list, key=lambda x: (-x.store.sorting_index, -x.store.publish_at))
        self.list_by_time = self.list[:]
        self.list_by_time = sorted(self.list_by_time, key=lambda x: (-x.store.publish_at))

    def on_store_reload(self, stores: list[AnnouncementStore]) -> None:
        self.list = [Announcement(self._game, x) for x in stores]
        self._sort_list()

    def on_store_update(self, announcement_id: int, new_store: AnnouncementStore | None) -> None:
        other_announcements = [x for x in self.list if x.store.id != announcement_id]

        if new_store is None:  # delete
            self.list = other_announcements
        elif len(other_announcements) == len(self.list):  # create
            self.list = other_announcements + [Announcement(self._game, new_store)]
        else:  # update
            self.list = other_announcements + [Announcement(self._game, new_store)]

        self._sort_list()

        self._game.worker.emit_ws_message({'type': 'normal', 'payload': {'type': 'update_announcements'}})

    @property
    def next_announcement_ts(self) -> int:
        for a in self.list_by_time[::-1]:
            if a.timestamp_s > self.last_push_time:
                return a.timestamp_s
        return Announcements.TS_INF_S

    @property
    def next_announcement(self) -> Announcement | None:
        for a in self.list_by_time[::-1]:
            if a.timestamp_s > self.last_push_time:
                return a
        return None


class Announcement:
    def __init__(self, game: Game, store: AnnouncementStore):
        self._game: Game = game
        self.store: AnnouncementStore = store

        self.title = store.title
        self.timestamp_s = store.publish_at

    def __repr__(self) -> str:
        return repr(self.store)

    @lru_cache(16)
    def _render_template(self, tick: int, group: str | None) -> str:
        try:
            return utils.render_template(self.store.content_template, {'group': group, 'tick': tick})
        except Exception as e:
            self._game.worker.log(
                'error',
                'announcement.render_template',
                f'template render failed: {self.store.id} ({self.store.title}): {utils.get_traceback(e)}',
            )
            return '<i>（模板渲染失败）</i>'

    def describe_json(self, user: User | None) -> dict[str, Any]:
        return {
            'id': self.store.id,
            'category': AnnouncementStore.Category.dict()[self.store.category],
            'publish_at': self.store.publish_at,
            'sorting_index': self.store.sorting_index,
            'title': self.title,
            'content': self._render_template(self._game.cur_tick, None if user is None else user.model.group),
        }
