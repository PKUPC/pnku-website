from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.state import User

STORY_LIST = [
    {
        "subtitle": "开始",
        "list": [
            {"title": "游戏简介", "template": "introduction"},
            {"title": "序章", "template": "prologue"},
        ],
    },
    {
        "subtitle": "第一日",
        "list": [
            {"title": "与素青的初见", "template": "day1_intro"},
            {"title": "囚禁于沉睡遗迹", "template": "day1_meta"},
        ],
    },
    {
        "subtitle": "第二日",
        "list": [
            {"title": "与秋蝉的初见", "template": "day2_intro"},
            {"title": "乞求春风再临", "template": "day2_meta"},
        ],
    },
    {
        "subtitle": "第三日",
        "list": [
            {"title": "与临水的初见", "template": "day3_intro"},
            {"title": "这明灭宇宙", "template": "day3_premeta"},
            {"title": "任造化落骰-A", "template": "day3_meta1"},
            {"title": "任造化落骰-B", "template": "day3_meta2"},
            {"title": "任造化落骰-C", "template": "day3_meta3"},
        ],
    },
    {
        "subtitle": "尾声",
        "list": [
            {"title": "尾声", "template": "ending"},
            {"title": "工作人员", "template": "staff"},
        ],
    }
]


def get_story_list(user: User) -> list[dict[str, Any]]:
    if user.is_staff:
        return STORY_LIST

    rst = []
    for group in STORY_LIST:
        rst_group: dict[str, Any] = {"subtitle": group["subtitle"], "list": []}
        for story in group["list"]:
            if story["template"] in user.team.game_status.unlock_templates:  # type: ignore
                rst_group["list"].append(story)

        if len(rst_group["list"]) > 0:
            rst.append(rst_group)

    return rst
