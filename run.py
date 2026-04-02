
from api.api_schools import schools_api
from api.api_cities import cities_api
from api.api_regions import regions_api
from data import db_session
from application import app, login_manager
from data.student import Student
import views.main
import views.students
import views.schedule
db_session.global_init("db/reg_form.db")


app.register_blueprint(regions_api)
app.register_blueprint(cities_api)
app.register_blueprint(schools_api)


login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(user_id)


if __name__ == '__main__':
    db_session.global_init("db/reg_form.db")
    app.run(port=8080, host='127.0.0.1')
