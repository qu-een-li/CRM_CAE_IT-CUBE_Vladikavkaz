import calendar
from datetime import date, time
from datetime import datetime
from random import choice, randint, random, sample
from string import ascii_lowercase

from data import db_session
from data.contest import Contest
from data.db_session import create_session, global_init
from data.direction import Direction
from data.group import Group
from data.level_contest import Level_contest
from data.schedule import Schedule
from data.student import Student
from data.study_period import Study_period
from data.teacher import Teacher
from data.auditorium import Auditorium
from data.user import User, UserRole

global_init("db/reg_form.db")
ses = create_session()
Direction.init_data(ses)
