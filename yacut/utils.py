import asyncio
import aiohttp
import random
import string
from flask import current_app

from .models import URLMap


ALLOWED_CHARS = string.ascii_letters + string.digits


def get_unique_short_id(length: int = 6) -> str:
    while True:
        short_id = ''.join(random.choices(ALLOWED_CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


async def _upload_single_file(session, file_storage, folder='Uploader'):
    base = current_app.config.get('YANDEX_API_BASE')
    filename = file_storage.filename
    path = f'{folder}/{filename}'

    async with session.get(
        f'{base}resources/upload',
        params={'path': path, 'overwrite': 'true'},
    ) as resp:
        data = await resp.json()
        href = data.get('href')
        if not href:
            raise RuntimeError(
                'Не удалось получить URL для загрузки файлов на Яндекс Диск'
            )

    file_storage.stream.seek(0)

    async with session.put(
            href, data=file_storage.stream
    ) as upload_resp:
        if upload_resp.status not in (200, 201, 202, 204):
            raise RuntimeError(
                f'Ошибка загрузки файла {filename} на Яндекс Диск'
            )

    async with session.get(
        f'{base}resources/download',
        params={'path': path},
    ) as meta_resp:
        meta = await meta_resp.json()
        public_url = meta.get('href')
        if not public_url:
            raise RuntimeError(
                f'Не удалось получить public_url для файла {filename}'
            )
    return filename, public_url


async def _upload_files_to_yandex_disk_async(files):
    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise RuntimeError('Токен Яндекс Диска не настроен')
    headers = {'Authorization': f'OAuth {token}'}

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [
            _upload_single_file(session, file_storage)
            for file_storage in files
        ]
        return await asyncio.gather(*tasks)


def upload_files_to_yandex_disk(files):
    if not files:
        return []
    return asyncio.run(_upload_files_to_yandex_disk_async(files))