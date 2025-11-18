from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import (
    DataRequired, URL, Length, Optional, Regexp, ValidationError
)

from yacut.models import URLMap


FORBIDDEN_SHORT_IDS = {'files'}


class URLForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL')
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=16, message='Максимум 16 символов'),
            Regexp(
                regex=r'^[A-Za-z0-9]+$',
                message='Можно использовать только латинские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if not field.data:
            return
        short = field.data
        if short in FORBIDDEN_SHORT_IDS:
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        if URLMap.query.filter_by(short=short).first():
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Файлы для загрузки',
        validators=[
            DataRequired(message='Выберете хотя бы один файл'),
        ]
    )
    submit = SubmitField('Загрузить')

    def validate_files(self, field):
        if not field.data or len(field.data) == 0:
            raise ValidationError('Выберете хотя бы один файл')
