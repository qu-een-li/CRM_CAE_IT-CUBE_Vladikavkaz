import os

KEY_CSRF = "yandexlyceum_secret_key"
KEY_API = "AizdvTuXgfoBlLspQmBPdRuVAaKbsGZk"
UPLOAD_FOLDER = os.path.join("static", "uploads", "teachers")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
PORT, HOST = 5001, "127.0.0.1"
API_PORT, API_HOST = 5002, "127.0.0.1"
