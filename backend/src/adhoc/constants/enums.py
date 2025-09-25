from typing import Literal

from src.utils import EnhancedEnum


class PuzzleVisibleStatus(EnhancedEnum):
    UNLOCK = 'unlock'
    LOCK = 'lock'
    FOUND = 'found'


PuzzleVisibleStatusLiteral = Literal['unlock', 'lock', 'found']
