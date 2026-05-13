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


from sqlalchemy.orm import Session, scoped_session  # Добавили scoped_session
import sqlalchemy.orm as orm
import sqlalchemy as sa


def create_session() -> Session:
    global __factory
    return __factory()


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
    # SQLite по умолчанию использует StaticPool, но лучше настроить явно
    engine = sa.create_engine(conn_str, echo=False)

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
