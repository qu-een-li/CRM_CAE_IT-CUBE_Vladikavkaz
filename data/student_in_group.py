import sqlalchemy
from .db_session import SqlAlchemyBase

student_in_group = sqlalchemy.Table(
    "students_in_groups",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('group_id',
                      sqlalchemy.Integer,
                      sqlalchemy.ForeignKey("groups.id"),
                      nullable=False),
    sqlalchemy.Column('student_id',
                      sqlalchemy.Integer,
                      sqlalchemy.ForeignKey("students.id"),
                      nullable=False),
    sqlalchemy.Column('is_order',
                      sqlalchemy.Boolean,
                      default=False,
                      nullable=False)
)
