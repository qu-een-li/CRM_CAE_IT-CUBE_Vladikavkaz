from app import app
from flask import render_template


@app.errorhandler(404)
def not_found_page(e):
    parameters = {
        "up_message": "Упс! Страница не найдена.",
        "down_message": "Кажется, вы забрели не туда.",
        "error_code": "404",
    }
    return render_template("error.html", **parameters)


@app.errorhandler(500)
def internal_server_error(e):
    parameters = {
        "up_message": "Произошло что-то не предвиденое.",
        "down_message": "Кажется, у нас ошибка.",
        "error_code": "500",
    }
    return render_template("error.html", **parameters)


@app.route('/under_construction')
def under_construction():
    return render_template('under_construction.html')
