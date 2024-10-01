from .announcement_view import AnnouncementView
from .debug_view import DebugView
from .files_view import FilesView
from .game_policy_view import GamePolicyView
from .hint_view import HintView
from .log_user_view import LogUserView
from .log_view import LogView
from .message_view import MessageView
from .puzzle_view import PuzzleView
from .status_view import StatusView
from .submission_view import SubmissionView
from .team_event_view import TeamEventView
from .team_view import TeamView
from .template_view import TemplateView
from .ticket_message_view import TicketMessageView
from .ticket_view import TicketView
from .trigger_view import TriggerView
from .user_view import UserView

VIEWS = {
    'AnnouncementStore': AnnouncementView,
    'GamePolicyStore': GamePolicyView,
    'LogStore': LogView,
    'SubmissionStore': SubmissionView,
    'TeamStore': TeamView,
    'TriggerStore': TriggerView,
    'UserStore': UserView,
    'MessageStore': MessageView,
    "PuzzleStore": PuzzleView,
    "HintStore": HintView,
    "TeamEventStore": TeamEventView,
    "TicketStore": TicketView,
    "TicketMessageStore": TicketMessageView,
    "LogUserStore": LogUserView,
}
