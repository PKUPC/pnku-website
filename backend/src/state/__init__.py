from __future__ import annotations

from abc import ABC


class WithGameLifecycle(ABC):
    def on_tick_change(self) -> None:
        pass

    def on_preparing_to_reload_team_event(self, reloading_type: str) -> None:
        pass

    def on_team_event(self, event: TeamEvent, is_reloading: bool) -> None:
        pass

    def on_team_event_reload_done(self) -> None:
        pass


from .trigger_state import Trigger
from .board_state import Board, ScoreBoard, FirstBloodBoard, SimpleScoreBoard
from .game_policy_state import GamePolicy
from .submission_state import Submission, SubmissionResult
from .user_state import User, Users
from .announcement_state import Announcement, Announcements
from .team_state import Team, Teams
from .message_state import Messages
from .puzzle_state import Puzzle, Puzzles
from .hint_state import Hint, Hints
from .team_event_state import TeamEvent
from .ticket_state import Tickets, Ticket
from .game_state import Game
