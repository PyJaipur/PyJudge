import datetime
from peewee import *

DATABASE_NAME = "data.db"
db = SqliteDatabase(DATABASE_NAME)


class User(Model):
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        database = db


class Contest(Model):
    code = CharField(unique=True)
    description = CharField()
    start_time = DateTimeField()
    end_time = DateTimeField()

    class Meta:
        database = db


class Question(Model):
    test_case_input = TextField()
    test_case_output = TextField()
    question_statement = CharField()
    author = ForeignKeyField(User)
    created_date_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class ContestProblems(Model):
    contest = ForeignKeyField(Contest, backref="questions")
    question = ForeignKeyField(Question)

    class Meta:
        database = db
        indexes = ((("contest", "question"), True),)


db.connect()

# dummy contest data
practiceContest = Contest.get_or_create(
    code="PRACTICE",
    description="practice questions",
    start_time=datetime.datetime(day=1, month=1, year=1),
    end_time=datetime.datetime(day=1, month=1, year=9999),
)
pastContest = Contest.get_or_create(
    code="PASTCONTEST",
    description="somewhere in the past",
    start_time=datetime.datetime(day=1, month=11, year=2018),
    end_time=datetime.datetime(day=1, month=12, year=2018),
)
ongoingContest = Contest.get_or_create(
    code="ONGOINGCONTEST",
    description="somewhere in the present",
    start_time=datetime.datetime(day=1, month=4, year=2019),
    end_time=datetime.datetime(day=1, month=6, year=2019),
)
futureContest = Contest.get_or_create(
    code="FUTURECONTEST",
    description="somewhere in the future",
    start_time=datetime.datetime(day=1, month=1, year=2020),
    end_time=datetime.datetime(day=1, month=10, year=2020),
)

test = User.get_or_create(username="test", password="test")

q1 = Question.get_or_create(
    test_case_input="1",
    test_case_output="1",
    question_statement="1",
    author=test[0],
    created_date_time=datetime.datetime.now(),
)
q2 = Question.get_or_create(
    test_case_input="2",
    test_case_output="2",
    question_statement="1",
    author=test[0],
    created_date_time=datetime.datetime.now(),
)
q3 = Question.get_or_create(
    test_case_input="3",
    test_case_output="3",
    question_statement="1",
    author=test[0],
    created_date_time=datetime.datetime.now(),
)
q4 = Question.get_or_create(
    test_case_input="4",
    test_case_output="4",
    question_statement="1",
    author=test[0],
    created_date_time=datetime.datetime.now(),
)
q5 = Question.get_or_create(
    test_case_input="5",
    test_case_output="5",
    question_statement="1",
    author=test[0],
    created_date_time=datetime.datetime.now(),
)
q6 = Question.get_or_create(
    test_case_input="6",
    test_case_output="6",
    question_statement="1",
    author=test[0],
    created_date_time=datetime.datetime.now(),
)

ContestProblems.get_or_create(contest=practiceContest[0], question=q1[0])
ContestProblems.get_or_create(contest=practiceContest[0], question=q2[0])
ContestProblems.get_or_create(contest=pastContest[0], question=q1[0])
ContestProblems.get_or_create(contest=pastContest[0], question=q2[0])
ContestProblems.get_or_create(contest=ongoingContest[0], question=q3[0])
ContestProblems.get_or_create(contest=ongoingContest[0], question=q4[0])
ContestProblems.get_or_create(contest=futureContest[0], question=q5[0])
ContestProblems.get_or_create(contest=futureContest[0], question=q6[0])
