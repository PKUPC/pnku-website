from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Table(DeclarativeBase):  # type: ignore[misc]
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


from .announcement_store import AnnouncementStore
from .game_policy_store import GamePolicyStore, GamePolicyStoreModel, PolicyModel
from .log_store import LogStore
from .submission_store import SubmissionStore
from .trigger_store import TriggerStore
from .user_store import UserStore
from .team_store import TeamStore
from .message_store import MessageStore
from .puzzle_store import PuzzleStore, PuzzleStoreModel
from .hint_store import HintStore, HintStoreModel
from .team_event_store import (
    TeamEventStore, SubmissionEvent, GameStartEvent, BuyNormalHintEvent, StaffModifyApEvent, StaffModifySpApEvent,
    PuzzleActionEvent
)
from .ticket_store import TicketStore, TicketStoreModel, ManualHintModel
from .ticket_message_store import TicketMessageStore
from .log_user_store import LogUserStore
