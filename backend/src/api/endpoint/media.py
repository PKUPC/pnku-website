import datetime

from sanic import Blueprint, HTTPResponse, Request, response

from ... import secret


bp = Blueprint('media', url_prefix='/')

if secret.DEBUG_MODE:

    @bp.route('/dyn_media')
    async def hello(_req: Request) -> HTTPResponse:
        return response.text('hello')

    @bp.route('/media/<filename:path>')
    async def media_files(_req: Request, filename: str) -> HTTPResponse:
        return await response.file(secret.MEDIA_PATH / filename, max_age=datetime.timedelta(days=30).total_seconds())

    @bp.route('/m/<filename:path>')
    async def export_media_files(_req: Request, filename: str) -> HTTPResponse:
        return await response.file(
            secret.EXPORT_MEDIA_PATH / filename, max_age=datetime.timedelta(days=30).total_seconds()
        )

    @bp.route('/t/<filename:path>')
    async def uploaded_files(_req: Request, filename: str) -> HTTPResponse:
        return await response.file(secret.UPLOAD_PATH / filename, max_age=datetime.timedelta(days=30).total_seconds())
