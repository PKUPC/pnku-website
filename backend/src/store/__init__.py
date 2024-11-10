from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Table(DeclarativeBase):  # type: ignore[misc]
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


from .announcement_store import AnnouncementStore
from .game_policy_store import GamePolicyStore, GamePolicyStoreModel, PolicyModel
from .hint_store import HintStore, HintStoreModel
from .log_store import LogStore
from .log_user_store import LogUserStore
from .message_store import MessageStore
from .puzzle_store import PuzzleStore, PuzzleStoreModel
from .submission_store import SubmissionStore
from .team_event_store import (
    BuyNormalHintEvent,
    GameStartEvent,
    PuzzleActionEvent,
    StaffModifyApEvent,
    StaffModifySpApEvent,
    SubmissionEvent,
    TeamEventStore,
)
from .team_store import TeamStore
from .ticket_message_store import TicketMessageStore
from .ticket_store import ManualHintModel, TicketStore, TicketStoreModel
from .trigger_store import TriggerStore
from .user_store import UserStore
