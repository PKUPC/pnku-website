from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Table(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


from .announcement_store import AnnouncementStore
from .game_policy_store import GamePolicyStore, GamePolicyStoreModel, PolicyModel
from .hint_store import HintStore, HintStoreModel
from .log_store import LogStore
from .log_user_store import LogUserStore
from .message_store import MessageModel, MessageStore
from .puzzle_store import PuzzleStore, PuzzleStoreModel
from .submission_store import SubmissionStore
from .team_event_store import (
    BuyNormalHintEvent,
    GameStartEvent,
    PuzzleActionEvent,
    StaffModifyApEvent,
    SubmissionEvent,
    TeamEventStore,
    TeamEventType,
)
from .team_store import TeamStore
from .ticket_message_store import TicketMessageModel, TicketMessageStore
from .ticket_store import ManualHintModel, TicketStore, TicketStoreModel
from .trigger_store import TriggerStore
from .user_store import UserStore


__all__ = [
    'Table',
    'AnnouncementStore',
    'GamePolicyStore',
    'GamePolicyStoreModel',
    'PolicyModel',
    'HintStore',
    'HintStoreModel',
    'LogStore',
    'LogUserStore',
    'MessageModel',
    'MessageStore',
    'PuzzleStore',
    'PuzzleStoreModel',
    'SubmissionStore',
    'TeamEventStore',
    'TeamEventType',
    'BuyNormalHintEvent',
    'GameStartEvent',
    'PuzzleActionEvent',
    'StaffModifyApEvent',
    'SubmissionEvent',
    'TeamStore',
    'TicketMessageModel',
    'TicketMessageStore',
    'TicketStore',
    'ManualHintModel',
    'TicketStoreModel',
    'TriggerStore',
    'UserStore',
]
