from data.teacher import Teacher


def get_full_teachers_initials_by_column(teacher: Teacher):
    return f'{teacher.name} {teacher.patronymic} {teacher.surename}'
