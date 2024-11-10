from sanic import Blueprint, HTTPResponse, Request

from src import custom


bp = Blueprint('sybil', url_prefix='/sybil')


@bp.route('/report', methods=['POST'])
def recv_sybil_report(req: Request) -> HTTPResponse:
    return custom.handle_report(req)


@bp.route('/event', methods=['POST'])
def recv_sybil_event(req: Request) -> HTTPResponse:
    return custom.handle_event(req)
