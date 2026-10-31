import enum
import sqlalchemy
from .db_session import SqlAlchemyBase


class StudentGroupStatus(enum.IntEnum):
    """Статус ученика в конкретной группе (у одного ученика в разных группах он может быть разным)"""

    STUDENT = 0    # начал учиться в группе — в столбце "Статус" ничего не пишется
    CANDIDATE = 1  # ещё не решил, остаётся в группе или нет

    @property
    def title(self):
        return {StudentGroupStatus.STUDENT: "Ученик", StudentGroupStatus.CANDIDATE: "Кандидат"}[self]


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
    # попал ли ученик в приказ о зачислении (будет позже)
    sqlalchemy.Column('is_order',
                      sqlalchemy.Boolean,
                      default=False,
                      nullable=False),
    sqlalchemy.Column('status',
                      sqlalchemy.Integer,
                      default=StudentGroupStatus.STUDENT,
                      server_default="0",
                      nullable=False),
    # один ученик может быть в разных группах, но в одной группе — один раз
    sqlalchemy.UniqueConstraint('group_id', 'student_id', name='ux_students_in_groups_group_student')
)
