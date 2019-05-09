from bottle import Bottle, run, template, static_file, request, route, redirect
import os
import sys
import datetime
from collections import defaultdict, namedtuple
import shelve

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = Bottle()

database_path = "submission_record.db"
questions = {}
contests = []
question_dir = "files/questions"

Question = namedtuple("Question", "output statement")
Submission = namedtuple("Submission", "question time output is_correct")
# questions, code, description, start_time, end_time
Contest = namedtuple("Contest","code description questions")

# dummy contests
contests.append(
    Contest(code="PRACTICE", description="practice questions", questions=[1,2])
)
contests.append(
    Contest(code="PASTCONTEST", description="somewhere in the past", questions=[1,2])
)
contests.append(
    Contest(code="ONGOINGCONTEST", description="somewhere in the present", questions=[3,4])
)
contests.append(
    Contest(code="FUTURECONTEST", description="somewhere in the future", questions=[5,6])
)

for i in os.listdir(question_dir):
    if not i.isdigit():
        continue
    # read the correct output as bytes object
    with open(os.path.join(question_dir, i, "output.txt"), "rb") as fl:
        output = fl.read()
    with open(os.path.join(question_dir, i, "statement.txt"), "r") as fl:
        statement = fl.read()
    questions[i] = Question(output=output, statement=statement)

@app.route("/")
def changePath():
    return redirect("/dashboard")

@app.get("/dashboard")
def dashboard():
    return template("dashboard.html", contests=contests)

@app.get("/contest/<code>/<number>")
def contest(code,number):
    statement = questions[number].statement
    return template("index.html", question_number=number, question=statement)

@app.get("/contest/<code>")
def contest(code):
    for contest in contests:
        if(contest.code == code):
            description = contest.description
            questions = contest.questions
    return template("contest.html", code=code, description=description, questions=questions)

@app.get("/question/<number>")
def question(number):
    statement = questions[number].statement
    return template("index.html", question_number=number, question=statement)


@app.get("/question/<path:path>")
def download(path):
    return static_file(path, root=question_dir)


@app.get("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root=os.path.join(dir_path, "static"))


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


@app.post("/check/<number>")
def file_upload(number):
    u_name = request.forms.get("username")  # accepting username
    time = datetime.datetime.now()
    uploaded = request.files.get("upload").file.read()
    expected = questions[number].output
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = uploaded == expected

    with shelve.open(database_path) as submission_record:
        submissions = (
            [] if u_name not in submission_record else submission_record[u_name]
        )
        # submissions = submission_record.get(u_name, list())
        submissions.append(
            Submission(question=number, time=time, output=uploaded, is_correct=ans)
        )
        submission_record[u_name] = submissions

    if not ans:
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job! "


run(app, host="localhost", port=8080)
