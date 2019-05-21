import bottle
import os, sys, datetime
import string, random
from peewee import *

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = bottle.Bottle()

DATABASE_NAME = "data.db"
question_dir = "files/questions"

db = SqliteDatabase(DATABASE_NAME)


class User(Model):
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        database = db


class Session(Model):
    id = CharField(unique=True)
    user = ForeignKeyField(User)

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
    q_no = IntegerField(unique=True)
    author = ForeignKeyField(User)

    class Meta:
        database = db


class ContestProblems(Model):
    contest = ForeignKeyField(Contest)
    question = ForeignKeyField(Question)

    class Meta:
        database = db
        indexes = ((("contest", "question"), True),)


class Submission(Model):
    user = ForeignKeyField(User)
    time = DateTimeField()
    question = ForeignKeyField(Question)
    contest = ForeignKeyField(Contest)
    is_correct = BooleanField()

    class Meta:
        database = db
        indexes = ((("user", "time"), True),)


db.connect()
db.create_tables([User, Session, Submission, ContestProblems, Contest, Question])


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

q1 = Question.get_or_create(q_no=1, author=test[0])
q2 = Question.get_or_create(q_no=2, author=test[0])
q3 = Question.get_or_create(q_no=3, author=test[0])
q4 = Question.get_or_create(q_no=4, author=test[0])
q5 = Question.get_or_create(q_no=5, author=test[0])
q6 = Question.get_or_create(q_no=6, author=test[0])


ContestProblems.get_or_create(contest=practiceContest[0], question=q1[0])
ContestProblems.get_or_create(contest=practiceContest[0], question=q2[0])
ContestProblems.get_or_create(contest=pastContest[0], question=q1[0])
ContestProblems.get_or_create(contest=pastContest[0], question=q2[0])
ContestProblems.get_or_create(contest=ongoingContest[0], question=q3[0])
ContestProblems.get_or_create(contest=ongoingContest[0], question=q4[0])
ContestProblems.get_or_create(contest=futureContest[0], question=q5[0])
ContestProblems.get_or_create(contest=futureContest[0], question=q6[0])


def login_required(function):
    def login_redirect(*args, **kwargs):
        if not logggedIn():
            return bottle.template("home.html", message="Login required.")
        return function(*args, **kwargs)

    return login_redirect


@app.route("/")
def changePath():
    return bottle.redirect("/home")


@app.get("/home")
def home():
    if logggedIn():
        return bottle.redirect("/dashboard")
    return bottle.template("home.html", message="")


@app.get("/dashboard")
@login_required
def dashboard():
    contests = Contest.select().order_by(Contest.start_time)
    return bottle.template("dashboard.html", contests=contests)


@app.get("/contest/<code>/<number>")
@login_required
def question(code, number):
    if (
        not ContestProblems.select()
        .where((Contest.code == code) & (Question.q_no == int(number)))
        .join(Contest, on=(ContestProblems.contest == Contest.id))
        .join(Question, on=(ContestProblems.question == Question.q_no))
        .exists()
    ):
        return bottle.abort(404, "no such contest problem")
    contest = Contest.get(Contest.code == code)
    if contest.start_time > datetime.datetime.now():
        return "The contest had not started yet."
    with open(os.path.join(question_dir, number, "statement.txt"), "rb") as fl:
        statement = fl.read()
    return bottle.template(
        "question.html", question_number=number, contest=code, question=statement
    )


@app.get("/contest/<code>")
@login_required
def contest(code):
    if not Contest.select().where(Contest.code == code).exists():
        return bottle.abort(404, "no such contest")
    contest = Contest.get(Contest.code == code)
    questions = (
        ContestProblems.select(Question.q_no)
        .where(ContestProblems.contest == contest)
        .join(Question, on=(ContestProblems.question == Question.q_no))
        .tuples()
    )
    return bottle.template("contest.html", contest=contest, questions=list(questions))


@app.get("/question/<path:path>")
def download(path):
    return bottle.static_file(path, root=question_dir)


@app.get("/static/<filepath:path>")
def server_static(filepath):
    return bottle.static_file(filepath, root=os.path.join(dir_path, "static"))


@app.get("/ranking/<code>")
def contest_ranking(code):
    order = (
        Submission.select(User.username, fn.count(Question.q_no).alias("score"))
        .where((Submission.is_correct == True) & (Contest.code == code))
        .join(User, on=(Submission.user == User.id))
        .join(Question, on=(Submission.question == Question.q_no))
        .join(Contest, on=(Submission.contest == Contest.id))
        .group_by(Submission.user)
        .order_by(fn.count(Question.q_no).desc())
    )
    order = list(order.tuples())
    order = [
        (username, score, rank) for rank, (username, score) in enumerate(order, start=1)
    ]
    return bottle.template("rankings.html", people=order)


@app.get("/ranking")
def rankings():
    order = (
        Submission.select(User.username, fn.count(Question.q_no).alias("score"))
        .where(Submission.is_correct == True)
        .join(User, on=(Submission.user == User.id))
        .switch()
        .join(Question, on=(Submission.question == Question.q_no))
        .group_by(Submission.user)
        .order_by(fn.count(Question.q_no).desc())
    )
    order = list(order.tuples())
    order = [
        (username, score, rank) for rank, (username, score) in enumerate(order, start=1)
    ]
    return bottle.template("rankings.html", people=order)


def logggedIn():
    if not bottle.request.get_cookie("s_id"):
        return False
    return (
        Session.select().where(Session.id == bottle.request.get_cookie("s_id")).exists()
    )


def createSession(username):
    session_id = "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(20)
    )
    bottle.response.set_cookie(
        "s_id",
        session_id,
        expires=datetime.datetime.now() + datetime.timedelta(days=30),
    )
    try:
        Session.create(id=session_id, user=User.get(User.username == username))
    except IntegrityError:
        return abort("Error! Please try again.")
    return bottle.redirect("/dashboard")


@app.post("/login")
def login():
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    if (
        not User.select()
        .where((User.username == username) & (User.password == password))
        .exists()
    ):
        return bottle.template("home.html", message="Invalid credentials.")
    return createSession(username)


@app.post("/register")
def register():
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    try:
        User.create(username=username, password=password)
    except IntegrityError:
        return bottle.template(
            "home.html", message="Username already exists. Select a different username"
        )
    return createSession(username)


@app.get("/logout")
def logout():
    Session.delete().where(Session.id == bottle.request.get_cookie("s_id")).execute()
    bottle.response.delete_cookie("s_id")
    return bottle.redirect("/home")


@app.post("/check/<code>/<number>")
@login_required
def file_upload(code, number):
    if (
        not ContestProblems.select()
        .where((Contest.code == code) & (Question.q_no == int(number)))
        .join(Contest, on=(ContestProblems.contest == Contest.id))
        .join(Question, on=(ContestProblems.question == Question.q_no))
        .exists()
    ):
        return bottle.abort(404, "no such contest problem")
    username = Session.get(
        Session.id == bottle.request.get_cookie("s_id")
    ).user.username
    time = datetime.datetime.now()
    uploaded = bottle.request.files.get("upload").file.read()
    with open(os.path.join(question_dir, number, "output.txt"), "rb") as fl:
        expected = fl.read()
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = uploaded == expected
    try:
        Submission.create(
            user=User.get(User.username == username),
            question=Question.get(Question.q_no == number),
            time=time,
            contest=Contest.get(Contest.code == code),
            is_correct=ans,
        )
    except:
        abort("Error in inserting submission to database.")
    if not ans:
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job! "


@app.error(404)
def error404(error):
    return template("error.html", errorcode=error.status_code, errorbody=error.body)


bottle.run(app, host="localhost", port=8080)
