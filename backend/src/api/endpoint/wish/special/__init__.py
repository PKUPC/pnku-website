from sanic import Blueprint


bp: Blueprint = Blueprint('wish-special', url_prefix='/wish/special')

from . import day2_02, day2_05
