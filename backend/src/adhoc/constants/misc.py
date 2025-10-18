from src import secret


STAFF_DISPLAY_NAME = '芈雨'

PUZZLE_CATEGORY_LIST = [
    'day1',
    'day2',
    'day3',
]

# TODO: 之前随手写的，以后都需要统一一下设计
AREA_NAME = {'day1': '素青', 'day2': '秋蝉', 'day3': '临水'}

# 序章开放后游戏开始前可以访问的区域吗，get_area_detail 鉴权时会用到
VALID_AREA_BEFORE_GAME_START = ['intro']
# 所有有效的区域名称，包括除了谜题区域之外的区域
VALID_AREA_NAMES = ['intro', 'day1', 'day2', 'day3']
# 仅包含谜题的区域
PUZZLE_AREA_NAMES = ['day1', 'day2', 'day3']

if secret.DEBUG_MODE:
    MANUAL_HINT_COOLDOWN = 90
else:
    MANUAL_HINT_COOLDOWN = 2 * 60 * 60
