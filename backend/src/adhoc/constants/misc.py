from src import secret


STAFF_DISPLAY_NAME = '芈雨'

PUZZLE_CATEGORY_LIST = [
    'day1',
    'day2',
    'day3',
]

AREA_NAME = {'day1': '素青', 'day2': '秋蝉', 'day3': '临水'}

if secret.DEBUG_MODE:
    MANUAL_HINT_COOLDOWN = 90
else:
    MANUAL_HINT_COOLDOWN = 2 * 60 * 60
