# import sqlalchemy as sa
# import sqlalchemy.orm as orm
# from sqlalchemy.orm import Session

# SqlAlchemyBase = orm.declarative_base()

# __factory = None


# def global_init(db_file):
#     global __factory

#     if __factory:
#         return

#     if not db_file or not db_file.strip():
#         raise Exception("Необходимо указать файл базы данных.")

#     conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
#     print(f"Подключение к базе данных по адресу {conn_str}")

#     engine = sa.create_engine(conn_str, echo=False)
#     __factory = orm.sessionmaker(bind=engine)

#     from . import __all_models

#     SqlAlchemyBase.metadata.create_all(engine)


import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, scoped_session

# Добавили импорт event для перехвата событий подключения
from sqlalchemy import event

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)

    # --- НАЧАЛО ИЗМЕНЕНИЙ: Обучаем SQLite кириллице ---
    @event.listens_for(engine, "connect")
    def setup_sqlite_custom_functions(dbapi_connection, connection_record):
        # Проверяем наличие метода create_function (актуально только для встроенного драйвера SQLite)
        if hasattr(dbapi_connection, 'create_function'):
            # Переопределяем стандартную функцию LOWER внутри SQLite на Python-функцию .lower()
            # Она принимает 1 аргумент (текст) и безопасно приводит его к нижнему регистру
            dbapi_connection.create_function(
                "lower", 1, lambda val: val.lower() if val is not None else "")
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    # Оборачиваем sessionmaker в scoped_session
    __factory = scoped_session(orm.sessionmaker(bind=engine))

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def remove_session():
    global __factory
    if __factory:
        __factory.remove()
