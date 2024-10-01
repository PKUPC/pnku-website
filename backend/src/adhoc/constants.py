# flask admin 中设置区域会用到
from enum import Enum

from src import secret

STAFF_DISPLAY_NAME = "芈雨"

PUZZLE_CATEGORY_LIST = [
    "day1",
    "day2",
    "day3",
]

AREA_NAME = {"day1": "素青", "day2": "秋蝉", "day3": "临水"}


class AnnouncementCategory(Enum):
    GENERAL = "通用"
    DAY1 = "素青"
    DAY2 = "秋蝉"
    DAY3 = "临水"

    @classmethod
    def name_list(cls) -> list[str]:
        return [x.name for x in cls]

    @classmethod
    def dict(cls) -> dict[str, str]:
        return {x.name: x.value for x in cls}


if secret.DEBUG_MODE:
    MANUAL_HINT_COOLDOWN = 90
else:
    MANUAL_HINT_COOLDOWN = 2 * 60 * 60
