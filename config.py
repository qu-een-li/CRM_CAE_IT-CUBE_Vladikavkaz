import os


KEY_CSRF = 'yandexlyceum_secret_key'

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'teachers')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024