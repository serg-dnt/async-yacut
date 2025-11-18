from http import HTTPStatus
from flask import jsonify, request, url_for

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id, ALLOWED_CHARS

ALLOWED_CUSTOM_ID_LENGTH = 16


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(force=True, silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    url = data.get('url')
    if not url:
        return jsonify(
            {'message': '"url" является обязательным полем!'}
        ), HTTPStatus.BAD_REQUEST
    custom_id = data.get('custom_id')
    if custom_id:
        if len(custom_id) > ALLOWED_CUSTOM_ID_LENGTH or any(
                ch not in ALLOWED_CHARS for ch in custom_id
        ):
            return (
                jsonify(
                    {'message': 'Указано недопустимое имя для короткой ссылки'}
                ),
                HTTPStatus.BAD_REQUEST
            )
        if custom_id == 'files':
            return (
                jsonify(
                    {
                        'message':
                        'Предложенный вариант короткой ссылки уже существует.'
                    }
                ),
                HTTPStatus.BAD_REQUEST
            )
        if URLMap.query.filter_by(short=custom_id).first():
            return (
                jsonify(
                    {
                        'message':
                        'Предложенный вариант короткой ссылки уже существует.'
                    }
                ),
                HTTPStatus.BAD_REQUEST
            )
        short_id = custom_id
    else:
        short_id = get_unique_short_id()
    url_map = URLMap(original=url, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    short_link = url_for(
        'redirect_to_original', short_id=short_id, _external=True
    )
    return (
        jsonify(
            {
                'url': url,
                'short_link': short_link,
            }
        ),
        HTTPStatus.CREATED
    )


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        return (
            jsonify(
                {'message': 'Указанный id не найден'}
            ),
            HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': url_map.original}), HTTPStatus.OK
