import os
import uuid

from typing import Any, Optional

from sanic import Blueprint, Request

from src import secret
from src.custom import store_user_log
from src.logic import Worker
from src.state import User

from . import wish_checker, wish_response


bp: Blueprint = Blueprint('wish-upload', url_prefix='/wish/upload')


@bp.route('/upload_image', ['POST'])
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def upload_image(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    if secret.PLAYGROUND_MODE:
        store_user_log(req, 'api.upload.upload_image', 'abnormal', '在 playground 模式上传图片。', {})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '在目前的游戏模式下无法使用此操作！'}
    if req.files is None or 'file' not in req.files:
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '没有上传图片！'}
    uploaded_file = req.files.get('file')
    assert uploaded_file is not None
    if uploaded_file.type != 'image/webp' and uploaded_file.type != 'image/jpeg':
        store_user_log(
            req, 'api.upload.upload_image', 'abnormal', '不支持的文件类型！', {'file_type': uploaded_file.type}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '不支持的文件类型！'}
    if len(uploaded_file.body) > 512 * 1024:
        store_user_log(
            req, 'api.upload.upload_image', 'abnormal', '图片文件过大！', {'file_size': len(uploaded_file.body)}
        )
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '图片文件过大！'}
    if user.team.model.extra_info.ban_list.ban_upload_image:
        store_user_log(req, 'api.upload.upload_image', 'abnormal', '已禁用上传图片功能！', {})
        return {'status': 'error', 'title': 'BAD_REQUEST', 'message': '你的队伍已经被禁止上传图片！'}

    file_suffix = '.webp' if uploaded_file.type == 'image/webp' else '.jpeg'
    filename = str(uuid.uuid4()) + file_suffix
    target_folder = (secret.UPLOAD_PATH / str(user.team.model.id)).resolve()
    target_folder.mkdir(parents=True, exist_ok=True)

    cur_file_cnt = len(os.listdir(target_folder))
    print(cur_file_cnt)
    if cur_file_cnt >= user.team.model.extra_info.upload_image_limit:
        return {
            'status': 'error',
            'title': 'BAD_REQUEST',
            'message': '你的队伍可以上传的图片已达上限！如有需要，请联系工作人员。',
        }

    store_user_log(
        req,
        'api.upload.upload_image',
        'upload_image',
        '',
        {'filename': filename, 'origin_filename': uploaded_file.name},
    )

    target_file = (secret.UPLOAD_PATH / str(user.team.model.id) / filename).resolve()

    with target_file.open('wb') as f:
        f.write(uploaded_file.body)

    return {'status': 'success'}


@bp.route('/get_uploaded_images', ['POST'])
@wish_response
@wish_checker(['team_is_gaming', 'game_start'])
async def get_uploaded_images(req: Request, worker: Worker, user: User | None) -> dict[str, Any]:
    assert user is not None
    assert user.team is not None

    target_folder = (secret.UPLOAD_PATH / str(user.team.model.id)).resolve()
    target_folder.mkdir(parents=True, exist_ok=True)
    files = [file for file in target_folder.iterdir() if file.is_file()]
    files.sort(key=lambda x: x.stat().st_ctime, reverse=True)
    relative_files = [file.relative_to(secret.UPLOAD_PATH) for file in files]
    file_urls = ['/t/' + str(file) for file in relative_files]

    rst: dict[str, Any] = {'list': [{'url': x} for x in file_urls]}
    if user.team.model.extra_info.ban_list.ban_upload_image:
        rst['disabled'] = True
        rst['disable_reason'] = '你的队伍已经被禁止上传图片！'
    elif len(file_urls) >= user.team.model.extra_info.upload_image_limit:
        rst['disabled'] = True
        rst['disable_reason'] = '你的队伍上传图片的数量已达上限！如有需要，请联系工作人员。'

    return {'status': 'success', 'data': rst}
