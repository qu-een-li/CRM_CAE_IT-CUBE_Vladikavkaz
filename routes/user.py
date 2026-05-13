from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from data.user import User
from app import app
from data.db_session import create_session
from forms.loginform import LoginForm


@app.route("/login", methods=["GET", "POST"])
def login():
    """Форма входа в аккаунт"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        try:
            db_sess = create_session()
            user = db_sess.query(User).filter(User.user_name == username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                return redirect("/")
            else:
                flash("Неверные данные!")
        finally:
            db_sess.close()

    return render_template("login.html", title="Авторизация", form=form)


@app.route("/logout")
def logout():
    """Выход из аккаунта"""
    logout_user()
    return redirect(url_for("login"))
