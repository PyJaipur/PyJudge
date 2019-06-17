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
    """ 
    Defines username and password for individual user.
    """
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        """
        define the database in the main class
        """
        database = db


class Session(Model):
    """
    Generates randam token for every section
    new Token is assigned to every User for every new session
    """ 
    
    def random_token():
        return "".join([random.choice(string.ascii_letters) for _ in range(20)])

    token = CharField(unique=True, default=random_token)
    user = ForeignKeyField(User)

    class Meta:
        database = db


class Contest(Model):
    """
    Each Contest instance contains:-
        Code
        Description of contest
        Contest start time and End Time
    """
    code = CharField(unique=True)
    description = CharField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    creator = ForeignKeyField(User)
    created_date_time = DateTimeField(default=datetime.datetime.now)

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
    """
    All contest problems belong to a Contest and are itself a question.
        contest defines the instance of Contest Class it belongs
        question defines the questions that belongs to that contest.
    """
    contest = ForeignKeyField(Contest, backref="questions")
    question = ForeignKeyField(Question)

    class Meta:
        database = db
        indexes = ((("contest", "question"), True),)


class Submission(Model):
    """
    Submoission classdefines the submission of solution of a Question
    Stores the information about:
        User that submits the Solution
        Time of Submission
        Contest to whish The question belongs
        Whether the soolution is correct
    """
    user = ForeignKeyField(User)
    time = DateTimeField()
    contestProblem = ForeignKeyField(ContestProblems)
    is_correct = BooleanField()

    class Meta:
        database = db
        #define the database in the main class
        indexes = ((("user", "time"), True),)

#Establish a Connection with Database
db.connect()

"""Create Tables with specied fields in Databse"""
db.create_tables([User, Session, Submission, ContestProblems, Contest, Question])


def login_required(function):
    """
    Extends the functainality of a funcion by checking log in condition.
    Checks if the user is logged in.if not redirect the user to home page 
    with message 'Login Required'
    
    : param : Function
    : type : method
    """
    
    def login_redirect(*args, **kwargs):
        if not logggedIn():
            return bottle.template("home.html", message="Login required.")
        me = Session.get(Session.token == bottle.request.get_cookie("s_id"))
        bottle.request.session = me
        return function(*args, **kwargs)

    return login_redirect



@app.route("/")# Sets the url that trigger following function
def changePath():
    """ redirects to home page """
    return bottle.redirect("/home")


@app.get("/home")# Sets the base url as the argument.
def home():    
    """
    If Logged in ,redirects to Dashboard of the user
    """
    if logggedIn():
        return bottle.redirect("/dashboard")
    return bottle.template("home.html", message="")


@app.get("/dashboard")# Sets the base url as the argument.
@login_required# Checks if user is logged in or not
def dashboard():
    """
    Return the dashboard template to the user
    """
    contests = Contest.select().order_by(Contest.start_time)
    return bottle.template("dashboard.html", contests=contests)


@app.get("/stats")
@login_required
def statistics():
    sub_history = (
        Submission.select(
            Contest.code,
            ContestProblems.question,
            Submission.time,
            Submission.is_correct,
        )
        .where(Submission.user == bottle.request.session.user)
        .join(ContestProblems, on=(Submission.contestProblem == ContestProblems.id))
        .switch()
        .join(Contest, on=(ContestProblems.contest == Contest.id))
        .order_by(Submission.time.desc())
        .dicts()
    )
    sub_stats_total = len(sub_history)
    sub_stats_correct = len([sub_history for sub in sub_history if sub["is_correct"]])
    return bottle.template(
        "stats.html",
        sub_history=sub_history,
        sub_stats_correct=sub_stats_correct,
        sub_stats_total=sub_stats_total,
    )


@app.get("/addQuestion")
@login_required
def addQuestion():
    return bottle.template("addQuestion.html")


@app.post("/questionInput")
@login_required
def questionInput():
    userid = bottle.request.session.user
    uploaded_question = bottle.request.files.get("question").file.read()
    uploaded_answer = bottle.request.files.get("answer").file.read()
    uploaded_statement = bottle.request.forms.get("statement")
    try:
        Question.create(
            test_case_input=uploaded_question,
            test_case_output=uploaded_answer,
            question_statement=uploaded_statement,
            author=userid,
        )
    except Exception as e:
        bottle.abort(500, str(e))
    question_bank = (
        Question.select(
            Question.id,
            Question.test_case_input,
            Question.question_statement,
            User.username,
            Question.created_date_time,
        )
        .join(User, on=(Question.author == User.id))
        .order_by(Question.created_date_time.desc())
        .dicts()
    )
    return bottle.template("questionBank.html", question_bank=question_bank)


@app.get("/addContest")
@login_required
def addContest():
    question_bank = (
        Question.select(
            Question.id,
            Question.test_case_input,
            Question.question_statement,
            User.username,
            Question.created_date_time,
        )
        .join(User, on=(Question.author == User.id))
        .order_by(Question.created_date_time.desc())
        .dicts()
    )
    return bottle.template("addContest.html", question_bank=question_bank)


@app.post("/contestInput")
@login_required
def contestInput():
    userid = bottle.request.session.user
    code = bottle.request.forms.get("code")
    description = bottle.request.forms.get("description")
    start_time = bottle.request.forms.get("start_time")
    end_time = bottle.request.forms.get("end_time")
    selection = bottle.request.forms.getall("selection")
    try:
        contest = Contest.get_or_create(
            code=code,
            description=description,
            start_time=start_time,
            end_time=end_time,
            creator=userid,
        )
    except Exception as e:
        bottle.abort(500, str(e))
    for questions in selection:
        ContestProblems.create(contest=contest[0], question=questions)
    contests = Contest.select().order_by(Contest.start_time)
    return bottle.template("dashboard.html", contests=contests)


@app.get("/contest/<code>/<number>")
@login_required
def question(code, number):
    """
    Checks if the question and Contest it belongs does exists.
    If exists : it checks the current status of the contest
    And then returns the question state ment along with question numbers
    and contest code to the Template

    : paran code : Contest code 
    : type code: int
    : paran Question  : Question no 
    : type Question: int 
    : return : Html template for Individual Question  

    """
    
    if (
        not ContestProblems.select()
        .where((Contest.code == code) & (Question.id == int(number)))
        .join(Contest, on=(ContestProblems.contest == Contest.id))
        .join(Question, on=(ContestProblems.question == Question.id))
        .exists()
    ):
        return bottle.abort(404, "no such contest problem")
    contest = Contest.get(Contest.code == code)
    if contest.start_time > datetime.datetime.now():
        return "The contest had not started yet."
    statement = (
        Question.select(Question.question_statement)
        .where(Question.id == number)
        .dicts()
        .get()
    )
    return bottle.template(
        "question.html", question_number=number, contest=code, question=statement
    )



@app.get("/contest/<code>")
@login_required
def contest(code):
    """
    Checks if contest exists by validating the contest id.
    Checks the the current staus of code
    
    : param code : Contest code
    : return : Html template for Contest 
    
    """

    try:
        contest = Contest.get(Contest.code == code)
    except Contest.DoesNotExist:
        return bottle.abort(404, "no such contest")
    if contest.start_time > datetime.datetime.now():
        return "The contest had not started yet."
    return bottle.template("contest.html", contest=contest, questions=contest.questions)



@app.get("/question/<id>")
def download(id):
    try:
        question_result = (
            Question.select(Question.test_case_input)
            .where(Question.id == id)
            .dicts()
            .get()
        )
    except:
        bottle.abort(404, "No such question")
    return question_result["test_case_input"]



@app.get("/static/<filepath:path>")
def server_static(filepath):
    """
    Static files for server

    : param path : path to download from
    :return : Static Files
    """ 
    return bottle.static_file(filepath, root=os.path.join(dir_path, "static"))


@app.get("/ranking/<code>")
def contest_ranking(code):
    """
    Generates rankinks of users in a Contest i.e the Contest results
    Validates the Sumbission And Contest. 
    Checks the number of correct submissions for each user and Added to 
    list with tuples of Username Along with thier Scores . The tuples 
    are added to list in descending order of the score .Then rankings are 
    given to each Username in the list.


    :param code : Contest Code
    :return : Html Template For Displaying Rankings
    """
    order = (
        Submission.select(
            User.username, fn.count(Submission.contestProblem.distinct()).alias("score")
        )
        .where(
            (Submission.is_correct == True)
            & (ContestProblems.contest == Contest.get(Contest.code == code))
        )
        .join(User, on=(Submission.user == User.id))
        .switch()
        .join(ContestProblems, on=(Submission.contestProblem == ContestProblems.id))
        .group_by(Submission.user)
        .order_by(fn.count(Submission.contestProblem.distinct()).desc())# descending order on basis of no of solution
    )
    order = list(order.tuples())
    order = [
        (username, score, rank) for rank, (username, score) in enumerate(order, start=1)
    ]# associate  ranks to each user
    return bottle.template("rankings.html", people=order)



@app.get("/ranking")
def rankings():
    """
    Overall Ranking of the user over all the Contest.

    :param None 
    :return : Ranking Template with Overall Ranking
    """
    order = (
        Submission.select(
            User.username, fn.count(Submission.contestProblem.distinct()).alias("score")
        )
        .where((Submission.is_correct == True))
        .join(User, on=(Submission.user == User.id))
        .switch()
        .join(ContestProblems, on=(Submission.contestProblem == ContestProblems.id))
        .group_by(Submission.user)
        .order_by(fn.count(Submission.contestProblem.distinct()).desc())
    )
    order = list(order.tuples())
    order = [
        (username, score, rank) for rank, (username, score) in enumerate(order, start=1)
    ]
    return bottle.template("rankings.html", people=order)


def logggedIn():
    """
    Downloads the question to local system

    :param None
    :return : True if Session exixsts for the user Logged In
    :return : False if Session not exixst for the user Logged In
                or if the s_id is not present or is wrong
    """
    if not bottle.request.get_cookie("s_id"):
        return False
    return (
        Session.select()
        .where(Session.token == bottle.request.get_cookie("s_id"))
        .exists()
    )



def createSession(username):
    """
    Create a session for the user.
    Set up cookie for The current session with seesion id ,token and expiry time.

    :param username: Username for which session is created
    :return : Resicts to dashboard of user
    """
    try:
        session = Session.create(user=User.get(User.username == username))
    except IntegrityError:
        return bottle.abort(500, "Error! Please try again.")
    bottle.response.set_cookie(
        "s_id",
        session.token,
        expires=datetime.datetime.now() + datetime.timedelta(days=30),
    )
    return bottle.redirect("/dashboard")


@app.post("/login")
def login():
    """
    This function is called whenever user log in to the app
    Checks if the user entered the Right credentials for log in

    :param None:
    :return : Redirects to home if invalid credenial Else Creates the session for the user  
    """
    
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
    """
    This function is called whenever new user registers
    New User is Created in the Data base and his credentials are stored
    Checks if the user with same username already exisxts

    :param None:
    :return : Create session function called for new username.
    """
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
    """
    Ends the session for the user  on logout
    Deletes the session cookie

    : param None:
    :return : Redirects to Home Page
    """
    Session.delete().where(Session.token == bottle.request.get_cookie("s_id")).execute()
    bottle.response.delete_cookie("s_id")
    return bottle.redirect("/home")



@app.post("/check/<code>/<number>")
@login_required 
def file_upload(code, number):
    """
    This Function is used to upload the submission to  Question to the Server.

    :param code: Contest Code 
    :param number : Question No of which solution is uploaded
    :return : "Wrong Answer!! : If solution is wrong
    :return : "Solved! Great Job! " : If solution is correct    
    """
    try:
        contestProblem = ContestProblems.get(
            ContestProblems.contest == Contest.get(Contest.code == code),
            ContestProblems.question == Question.get(Question.id == int(number)),
        )
    except:
        return bottle.abort(404, "no such contest problem")
    user = Session.get(Session.token == bottle.request.get_cookie("s_id")).user
    time = datetime.datetime.now()
    uploaded = bottle.request.files.get("upload").file.read()
    expected = (
        Question.select(Question.test_case_output)
        .where(Question.id == number)
        .dicts()
        .get()
    )
    expected = expected["test_case_output"]
    uploaded = uploaded.strip()
    ans = uploaded == expected
    
    try:
        Submission.create(
            user=user, contestProblem=contestProblem, time=time, is_correct=ans
<<<<<<< HEAD
        )# Add Submission For User
    except:
        bottle.abort(500, "Error in inserting submission to database.")
    
    if not ans: # if Answer is Wrong
=======
        )
    except Exception as e:
        bottle.abort(500, str(e))
    if not ans:
>>>>>>> 67730ed88a8c14fc1e4381f0bde6ee55f81aef12
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job! "



@app.error(404) # Checks if app returns an error with error code as argument
def error404(error):
    """
    Handles Error 

    :param error : Error rturned the App
    :return : Redirects to Template which Display Error
    """
    return template("error.html", errorcode=error.status_code, errorbody=error.body)


if __name__ == "__main__":
    bottle.run(app, host="localhost", port=8080)
