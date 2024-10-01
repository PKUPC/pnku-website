from __future__ import annotations

from typing import TYPE_CHECKING

from . import WithGameLifecycle
from ..store import TicketStore, TicketMessageStore

if TYPE_CHECKING:
    from . import WithGameLifecycle, Game, Team


class Ticket(WithGameLifecycle):
    constructed_ids: set[int] = set()

    def __init__(self, game: Game, store: TicketStore):
        assert store.id not in Ticket.constructed_ids
        Ticket.constructed_ids.add(store.id)
        #
        self.game: Game = game
        self._store: TicketStore = store
        self.model = self._store.validated_model()
        self.message_list: list[TicketMessageStore] = []
        assert self.model.team_id in self.game.teams.team_by_id
        self.team: Team = self.game.teams.team_by_id[self.model.team_id]

    def on_new_message(self, message: TicketMessageStore) -> None:
        self.message_list.append(message)

    def on_update_message(self, message: TicketMessageStore) -> None:
        target_idx = None
        for idx, x in enumerate(self.message_list):
            if x.id == message.id:
                target_idx = idx
                break
        if target_idx is not None:
            self.message_list[target_idx] = message

    def on_store_update(self, store: TicketStore) -> None:
        self._store = store
        self.model = self._store.validated_model()

    @property
    def last_message_ts(self) -> int:
        if len(self.message_list) == 0:
            return 0
        return self.message_list[-1].created_at // 1000

    @property
    def staff_replied(self) -> bool:
        if len(self.message_list) == 0:
            return False
        return self.message_list[-1].direction == TicketMessageStore.Direction.TO_PLAYER.name

    @property
    def status_repr(self) -> str:
        if len(self.message_list) == 0:
            return "异常"
        return TicketStore.TicketStatus.dict().get(self.model.status, "异常")

    @property
    def type_repr(self) -> str:
        if len(self.message_list) == 0:
            return "异常"
        return TicketStore.TicketType.dict().get(self.model.type, "异常")


class Tickets(WithGameLifecycle):
    constructed: bool = False

    def __init__(self, game: Game, ticket_stores: list[TicketStore], ticket_message_stores: list[TicketMessageStore]):
        assert not Tickets.constructed
        Tickets.constructed = True
        #
        self.game: Game = game
        self._stores: list[TicketStore] = ticket_stores
        self.list: list[Ticket] = []
        self.ticket_by_id: dict[int, Ticket] = {}
        self.tickets_by_team_id: dict[int, list[Ticket]] = {}

        # 初始化 ticket
        for store in self._stores:
            self._add_new_ticket(store)

        # 初始化 ticket message
        for message_store in ticket_message_stores:
            assert message_store.ticket_id in self.ticket_by_id
            self.ticket_by_id[message_store.ticket_id].on_new_message(message_store)

    def _add_new_ticket(self, store: TicketStore) -> None:
        ticket = Ticket(self.game, store)
        self.list.append(ticket)
        self.ticket_by_id[ticket.model.id] = ticket
        self.tickets_by_team_id.setdefault(store.team_id, [])
        self.tickets_by_team_id[store.team_id].append(ticket)

    def on_create_ticket(self, ticket_store: TicketStore, first_message_store: TicketMessageStore) -> None:
        self._add_new_ticket(ticket_store)
        ticket = self.ticket_by_id[ticket_store.id]
        ticket.on_new_message(first_message_store)

    def on_ticket_message(self, message_store: TicketMessageStore) -> None:
        ticket = self.ticket_by_id[message_store.ticket_id]
        ticket.on_new_message(message_store)

    def on_update_ticket_message(self, message_store: TicketMessageStore) -> None:
        ticket = self.ticket_by_id[message_store.ticket_id]
        ticket.on_update_message(message_store)

    def count_by_team_id_and_type_and_status(self, team_id: int, ticket_type: str, status: str) -> int:
        count = 0
        for ticket in self.tickets_by_team_id.get(team_id, []):
            if ticket.model.type == ticket_type and ticket.model.status == status:
                count += 1
        return count

    def get_tickets_by_team_id_and_type_and_status(self, team_id: int, ticket_type: str, status: str) -> list[Ticket]:
        rst = []
        for ticket in self.tickets_by_team_id.get(team_id, []):
            if ticket.model.type == ticket_type and ticket.model.status == status:
                rst.append(ticket)
        return rst
