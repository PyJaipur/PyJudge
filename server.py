import bottle
import os, sys, datetime
import string, random

from collections import defaultdict, namedtuple
import shelve

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = bottle.Bottle()

database_path = "submission_record.db"
user_db = "user_record.db"
sessions_db = "session_record.db"
questions = {}
contests = {}
question_dir = "files/questions"

Question = namedtuple("Question", "output statement")
Submission = namedtuple("Submission", "question time output is_correct contest")
Contest = namedtuple("Contest", "description questions start_time end_time")
User = namedtuple("User", "password")

# dummy contests
contests["PRACTICE"] = Contest(
    description="practice questions",
    questions=[1, 2],
    start_time=datetime.datetime(day=1, month=1, year=1),
    end_time=datetime.datetime(day=1, month=1, year=9999),
)
contests["PASTCONTEST"] = Contest(
    description="somewhere in the past",
    questions=[1, 2],
    start_time=datetime.datetime(day=1, month=11, year=2018),
    end_time=datetime.datetime(day=1, month=12, year=2018),
)
contests["ONGOINGCONTEST"] = Contest(
    description="somewhere in the present",
    questions=[3, 4],
    start_time=datetime.datetime(day=1, month=4, year=2019),
    end_time=datetime.datetime(day=1, month=6, year=2019),
)
contests["FUTURECONTEST"] = Contest(
    description="somewhere in the future",
    questions=[5, 6],
    start_time=datetime.datetime(day=1, month=1, year=2020),
    end_time=datetime.datetime(day=1, month=10, year=2020),
)

for i in os.listdir(question_dir):
    if not i.isdigit():
        continue
    with open(os.path.join(question_dir, i, "output.txt"), "rb") as fl:
        output = fl.read()
    with open(os.path.join(question_dir, i, "statement.txt"), "r") as fl:
        statement = fl.read()
    questions[i] = Question(output=output, statement=statement)


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
    return bottle.template("dashboard.html", contests=contests)

@app.get("/stats")
@login_required
def statistics():
    with shelve.open(database_path) as submission_record:
        sub_history = [
            (
                user,
                [
                    attempt
                    for attempt in submissions
                ]
            )
            for user, submissions in submission_record.items()
        ]
        sub_stats = [
            (
                user,
                len(
                        [
                            attempt.question
                            for attempt in submissions
                            if not(attempt.is_correct)
                        ]
                ),
				len(
                        [
                            attempt.question
                            for attempt in submissions
                            if attempt.is_correct
                        ]
                ),
				len(
                        [
                            attempt.question
                            for attempt in submissions
                        ]
                )
            )
            for user, submissions in submission_record.items()
        ]
    return bottle.template("stats.html", sub_history=sub_history, sub_stats=sub_stats)


@app.get("/contest/<code>/<number>")
@login_required
def contest(code, number):
    if not code in contests:
        return "Contest does not exist"
    if contests[code].start_time > datetime.datetime.now():
        return "The contest had not started yet."
    statement = questions[number].statement
    return bottle.template(
        "question.html", question_number=number, contest=code, question=statement
    )


@app.get("/contest/<code>")
@login_required
def contest(code):
    if not code in contests:
        return "Contest does not exist"
    if contests[code].start_time > datetime.datetime.now():
        return "The contest had not started yet."
    return bottle.template("contest.html", code=code, contest=contests[code])


@app.get("/question/<path:path>")
def download(path):
    return bottle.static_file(path, root=question_dir)


@app.get("/static/<filepath:path>")
def server_static(filepath):
    return bottle.static_file(filepath, root=os.path.join(dir_path, "static"))


@app.get("/ranking/<code>")
def contest_ranking(code):
    with shelve.open(database_path) as submission_record:
        order = [
            (
                user,
                len(
                    set(
                        [
                            attempt.question
                            for attempt in submissions
                            if (
                                attempt.is_correct
                                and (int(attempt.question) in contests[code].questions)
                                and attempt.contest == code
                                and attempt.time <= contests[code].end_time
                                and attempt.time >= contests[code].start_time
                            )
                        ]
                    )
                ),
            )
            for user, submissions in submission_record.items()
        ]
    order.sort(key=lambda x: x[1], reverse=True)
    order = [entry for entry in order if entry[1] > 0]
    order = [(user, score, rank) for rank, (user, score) in enumerate(order, start=1)]
    return bottle.template("rankings.html", people=order)


@app.get("/ranking")
def rankings():
    with shelve.open(database_path) as submission_record:
        order = [
            (
                user,
                len(
                    set(
                        [
                            attempt.question
                            for attempt in submissions
                            if attempt.is_correct
                        ]
                    )
                ),
            )
            for user, submissions in submission_record.items()
        ]
    order.sort(key=lambda x: x[1], reverse=True)
    order = [(user, score, rank) for rank, (user, score) in enumerate(order, start=1)]
    return template("rankings.html", people=order)

def logggedIn():
    if not bottle.request.get_cookie("s_id"):
        return False
    with shelve.open(sessions_db) as sessions:
        return bottle.request.get_cookie("s_id") in sessions


def createSession(username):
    session_id = "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(20)
    )
    bottle.response.set_cookie(
        "s_id",
        session_id,
        expires=datetime.datetime.now() + datetime.timedelta(days=30),
    )
    with shelve.open(sessions_db) as sessions:
        sessions[session_id] = username
    return bottle.redirect("/dashboard")


@app.post("/login")
def login():
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    with shelve.open(user_db) as users:
        if not username in users:
            return bottle.template("home.html", message="User does not exist.")
        if users[username].password != password:
            return bottle.template("home.html", message="Incorrect password.")
    return createSession(username)


@app.post("/register")
def register():
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    with shelve.open(user_db) as users:
        if username in users:
            return bottle.template(
                "home.html",
                message="Username already exists. Select a different username",
            )
        users[username] = User(password=password)
    return createSession(username)


@app.get("/logout")
def logout():
    with shelve.open(sessions_db) as sessions:
        del sessions[bottle.request.get_cookie("s_id")]
    bottle.response.delete_cookie("s_id")
    return bottle.redirect("/home")


@app.post("/check/<code>/<number>")
@login_required
def file_upload(code, number):
    with shelve.open(sessions_db) as sessions:
        u_name = sessions[bottle.request.get_cookie("s_id")]
    time = datetime.datetime.now()
    uploaded = bottle.request.files.get("upload").file.read()
    expected = questions[number].output
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = uploaded == expected

    with shelve.open(database_path) as submission_record:
        submissions = (
            [] if u_name not in submission_record else submission_record[u_name]
        )
        submissions.append(
            Submission(
                question=number,
                time=time,
                output=uploaded,
                is_correct=ans,
                contest=code,
            )
        )
        submission_record[u_name] = submissions

    if not ans:
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job! "


@app.error(404)
def error404(error):
    return template("error.html" ,errorcode=error.status_code , errorbody = error.body)

bottle.run(app, host="localhost", port=8080)