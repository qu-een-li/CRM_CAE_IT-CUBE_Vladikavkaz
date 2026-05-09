from functools import wraps
from flask import request, jsonify
from config import KEY_API, API_HOST, API_PORT
import requests
import time
from datetime import datetime

API_URL = f"http://{API_HOST}:{API_PORT}/api"
_api_session = requests.Session()


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        if request.headers.get("X-API-Key") != KEY_API:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


def api_request(endpoint, method="GET", data=None, params=None, retries=3, delay=2):
    """
    Универсальная обертка для запросов к вашему API.
    Позволяет сокращать запросы с внутреннему API, используя относительные пути со вставленным API-KEY и сразу возвращая json.
    """
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    headers = {"X-API-Key": KEY_API, "Content-Type": "application/json"}
    for attempt in range(retries):
        try:
            response = _api_session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=(15, 15),  # Для GET параметров
            )
            response.raise_for_status()  # Вызовет ошибку, если код не 2xx
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Попытка {attempt + 1} из {retries} не удалась: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Ждем перед следующей попыткой
            else:
                print("Все попытки исчерпаны.")
                return None, 504
