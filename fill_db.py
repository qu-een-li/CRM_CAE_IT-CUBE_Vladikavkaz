from data.db_session import create_session, global_init
from data.teacher import Teacher
from data.group import Group
from data.schedule import Schedule
from data.direction import Direction
from data.student import Student
from data.direction import Direction
from data.study_period import Study_period
from datetime import datetime
from random import choice, randint, sample
from datetime import date, time
import calendar
from string import ascii_lowercase
from data.auditorium import Auditorium

global_init("db/reg_form.db")
N_OF_STUDENTS = 100
N_OF_GROUPS = 20
N_OF_TEACHER = 15
CITIES = ["Ардон", "Алагир", "Владикавказ", "Беслан", "Моздок", "Дигора"]
NAMES = [
    # Мужские имена
    "Михаил",
    "Александр",
    "Артем",
    "Тимофей",
    "Иван",
    "Лев",
    "Марк",
    "Дмитрий",
    "Максим",
    "Матвей",
    "Роман",
    "Кирилл",
    "Николай",
    "Константин",
    "Владимир",
    # Женские имена
    "София",
    "Анна",
    "Мария",
    "Ева",
    "Виктория",
    "Варвара",
    "Алиса",
    "Василиса",
    "Полина",
    "Мирослава",
    "Ксения",
    "Есения",
    "Елизавета",
    "Вера",
    "Таисия",
]
SURNAMES = [
    # Мужские формы
    "Иванов",
    "Смирнов",
    "Кузнецов",
    "Попов",
    "Васильев",
    "Петров",
    "Соколов",
    "Михайлов",
    "Новиков",
    "Федоров",
    "Морозов",
    "Волков",
    "Алексеев",
    "Лебедев",
    "Семенов",
    # Женские формы
    "Иванова",
    "Смирнова",
    "Кузнецова",
    "Попова",
    "Васильева",
    "Петрова",
    "Соколова",
    "Михайлова",
    "Новикова",
    "Федорова",
    "Морозова",
    "Волкова",
    "Алексеева",
    "Лебедева",
    "Семенова",
]
PATRONYMICS = [
    # Мужские отчества
    "Александрович",
    "Михайлович",
    "Артемович",
    "Иванович",
    "Дмитриевич",
    "Максимович",
    "Сергеевич",
    "Андреевич",
    "Алексеевич",
    "Николаевич",
    "Егорович",
    "Владимирович",
    "Ильевич",
    "Романович",
    "Кириллович",
    # Женские отчества
    "Александровна",
    "Михайловна",
    "Артемовна",
    "Ивановна",
    "Дмитриевна",
    "Максимовна",
    "Сергеевна",
    "Андреевна",
    "Алексеевна",
    "Николаевна",
    "Егоровна",
    "Владимировна",
    "Ильинична",
    "Романовна",
    "Кирилловна",
]
STREETS = [
    # Топ самых частых (статистика по РФ)
    "Центральная",
    "Молодежная",
    "Школьная",
    "Лесная",
    "Садовая",
    "Новая",
    "Советская",
    "Набережная",
    "Заречная",
    "Полевая",
    # Имена известных личностей
    "Ленина",
    "Гагарина",
    "Пушкина",
    "Кирова",
    "Мира",
    "Чехова",
    "Лермонтова",
    "Горького",
    "Маяковского",
    "Дзержинского",
    # Природные и городские ориентиры
    "Луговая",
    "Цветочная",
    "Солнечная",
    "Степная",
    "Зеленая",
    "Победы",
    "Октябрьская",
    "Комсомольская",
    "Первомайская",
    "Вокзальная",
]
MAIL_TEMPLATES = (
    ["yandex", "bestteacher", "justanothermailbox", "mouseman", "personalmineone", "hacker"],
    ["mail.ru", "gmail.ru", "it-cube.ru", "yandex.ru", "vladikavkaz.edu"],
)

db_sess = create_session()


def generate_school_name():
    """Генерация названия школы"""
    adjectives = [
        "Первая",
        "Золотая",
        "Новая",
        "Высшая",
        "Яркая",
        "Цифровая",
        "Глобальная",
        "Мудрая",
        "Светлая",
        "Творческая",
    ]

    subjects = [
        "Знаний",
        "Прогресса",
        "Успеха",
        "Лидеров",
        "Будущего",
        "Мастерства",
        "Развития",
        "Инноваций",
        "Искусств",
        "Науки",
    ]

    types = ["Академия", "Гимназия", "Лицей", "Школа", "Центр"]

    specializations = ["программирования", "дизайна", "языков", "бизнеса", "творчества"]

    # Шаблоны структур названий
    structures = [
        lambda: f"{choice(adjectives)} {choice(types)} {choice(subjects)}",
        lambda: f"{choice(types)} {choice(subjects)}",
        lambda: f"Школа {choice(specializations)} '{choice(adjectives)}'",
        lambda: f"{choice(adjectives)} путь к {choice(subjects)}",
    ]

    return choice(structures)()


study_period1 = Study_period()
study_period1.date_end = datetime.now()
study_period1.date_start = datetime.now()
study_period1.reporting_period = "year"
db_sess.add(study_period1)

Direction.init_data(db_sess)
Auditorium.init_data(db_sess)
# генерация учителей
generated_teachers = []
for i in range(N_OF_TEACHER):
    teacher = Teacher()
    teacher.name = choice(NAMES)
    teacher.surename = choice(SURNAMES)
    teacher.patronymic = choice(PATRONYMICS)
    if choice([False, True]):
        teacher.email = f"{choice(MAIL_TEMPLATES[0])}{randint(1, 100)}@{choice(MAIL_TEMPLATES[1])}"
    else:
        teacher.email = f"{choice(MAIL_TEMPLATES[0])}@{choice(MAIL_TEMPLATES[1])}"
    syms = ascii_lowercase + "0123456789/" + ascii_lowercase.upper()
    teacher.personal_photos = "data:image/jpeg;base64,/"
    for _ in range(15):
        teacher.personal_photos += choice(syms)
    teacher.status = ""
    teacher.phone = randint(11111111111, 99999999999)
    teacher.phone = int("7" + str(teacher.phone))
    birth_month = randint(1, 12)
    birth_year = randint(1946, 2006)
    first_weekday, last_day = calendar.monthrange(birth_year, birth_month)
    teacher.birthday = date(year=birth_year, month=birth_month, day=randint(1, last_day))
    generated_teachers.append(teacher)
    db_sess.add(teacher)
# крэш тест для групп и проверки отображения их таблицы
# генерация групп
auditoriums_n = len(db_sess.query(Auditorium).all())
generated_groups = []
for i in range(N_OF_GROUPS):
    group = Group()
    group.auditorium_id = randint(1, auditoriums_n)
    direction = db_sess.get(Direction, randint(1, 6))
    group.teacher = choice(generated_teachers)
    group.description = f"Обучаем {direction.name}"
    group.level_of_education = choice(["вводный", "базовый", "углубленный"])
    group.group_type = choice(["семестровый", "интенсив", "мастер-класс"])
    group.study_period_id = 1
    group.duration = time(hour=choice([1, 2]), minute=choice([0, 30]))
    week_names = ["Пн", "Вт", "Ср", "Чт", "Пт"]
    group.direction = direction
    db_sess.add(group)
    group.name_of_group = f"{group.direction.name}; {', '.join(sample(week_names, k=randint(1, 3)))}; {choice(['09:30-11:30', '11:00-12:30', '13:00-15:00', '17:00-18:30', '12:00:13:00'])}; {choice(['6-9', '9-12', '12-18'])}"

    generated_groups.append(group)

# генерация студентов
for i in range(N_OF_STUDENTS):
    student = Student()
    student.school_class = randint(6, 11)
    birth_month = randint(1, 12)
    birth_year = 2026 - student.school_class - 12
    first_weekday, last_day = calendar.monthrange(birth_year, birth_month)
    student.birthday = date(year=birth_year, month=birth_month, day=randint(1, last_day))
    student.adres_of_living = f"{choice(STREETS)} {randint(1, 60)}"
    student.city = choice(CITIES)
    student.document = 1
    for _ in range(randint(1, 3)):
        student.groups.append(choice(generated_groups))

    student.name_parent = f"{choice(NAMES)} {choice(SURNAMES)} {choice(PATRONYMICS)}"
    student.parent_phone = randint(11111111111, 99999999999)
    student.parent_phone = int("7" + str(student.parent_phone))

    student.name_student = f"{choice(NAMES)} {choice(SURNAMES)} {choice(PATRONYMICS)}"
    student.school = generate_school_name()
    student.PFDO = randint(1111111111, 9999999999)
    student.student_phone = randint(11111111111, 99999999999)
    student.student_phone = int("7" + str(student.student_phone))
    db_sess.add(student)

sc = Schedule()
sc.date = datetime.now().date()
sc.group_id = 1
sc.start_time = datetime.now().time()
sc.end_time = datetime.now().time()
db_sess.add(sc)

db_sess.commit()
