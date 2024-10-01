import logging
from functools import wraps
from typing import Any

from flask import Flask, redirect, request
from flask_admin import Admin
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from werkzeug import Response

from .views import StatusView, VIEWS, TemplateView, FilesView, DebugView
from .. import secret, utils
from .. import store

logger = logging.getLogger("init")

secret.TEMPLATE_PATH.mkdir(parents=True, exist_ok=True)
secret.UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
secret.SYBIL_LOG_PATH.mkdir(parents=True, exist_ok=True)
secret.MEDIA_PATH.mkdir(parents=True, exist_ok=True)
secret.EXPORT_MEDIA_PATH.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_url_path=f'{secret.ADMIN_URL}/static')

app.config['DEBUG'] = False
app.config['ADMIN_URL'] = secret.ADMIN_URL
app.config['SQLALCHEMY_DATABASE_URI'] = secret.DB_CONNECTOR
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_size': 2,
    'pool_use_lifo': True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret.ADMIN_SESSION_SECRET

db = SQLAlchemy(app, model_class=store.Table)


def secured(cls: Any) -> Any:
    # noinspection PyMethodMayBeStatic
    @wraps(cls, updated=())
    class SecuredView(cls):  # type: ignore[misc]
        def is_accessible(self) -> bool:
            if secret.DEBUG_MODE and secret.DEBUG_WITH_FREE_ADMIN:
                return True

            auth_token = request.cookies.get('auth_token', None)
            if not auth_token:
                return False

            status, info = utils.jwt_decode(auth_token)
            if not status:
                return False
            user_id: int = info["user_id"]  # type: ignore  # known

            if not secret.IS_ADMIN(user_id):
                return False

            return True

        # noinspection PyUnusedLocal
        def inaccessible_callback(self, name: str, **kwargs: Any) -> Any:
            return redirect('/')

    return SecuredView


def remove_suffix(s: str, suffix: str) -> str:
    if s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s


class ReturnView(BaseView):  # type: ignore[misc]
    @expose('/')
    def index(self) -> Response:
        return redirect("/")


with app.app_context():
    admin = Admin(
        app,
        index_view=secured(StatusView)(name='Status', url=f'{secret.ADMIN_URL}/admin'),
        url=f'{secret.ADMIN_URL}/admin',
        template_mode='bootstrap3',
        base_template='base.html',
    )

    admin.add_view(secured(DebugView)(name='Debug'))
    admin.add_view(secured(ReturnView)(name='Return', url=f'{secret.FRONTEND_PORTAL_URL}'))

    for model_name in dir(store):
        if model_name.endswith('Store'):
            logger.info(f'added model: {model_name}')
            admin.add_view(secured(VIEWS.get(model_name, ModelView))(
                getattr(store, model_name), db.session, name=remove_suffix(model_name, 'Store'), category='Models',
            ))

    admin.add_view(secured(TemplateView)(secret.TEMPLATE_PATH, name='Template', category='Files'))
    admin.add_view(secured(FilesView)(secret.MEDIA_PATH, name='Media', endpoint='media', category='Files'))
    admin.add_view(
        secured(FilesView)(secret.UPLOAD_PATH, name='Player Uploaded', endpoint='player-uploaded', category='Files')
    )


@app.route(f'{secret.ADMIN_URL}/')
def index() -> Any:
    return redirect(f'{secret.ADMIN_URL}/admin/')
