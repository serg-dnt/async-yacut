import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_TIME_LIMIT = None
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    YANDEX_API_BASE = 'https://cloud-api.yandex.net/v1/disk/'
