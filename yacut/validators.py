from typing import re

from yacut.error_handlers import InvalidAPIUsage


def validate_request_data(data):

    if not data:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса'
        )

    if 'url' not in data:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!'
        )


def validate_custom_id(custom_id):

    if len(custom_id) > MAX_CUSTOM_ID_LENGTH:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )

    if not re.match(CUSTOM_ID_PATTERN, custom_id):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки')

    if URLMap.query.filter_by(short=custom_id).first():
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )