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

"""
Class: User 
      Defines username and password for individual user.
"""
class User(Model):
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        """
        Class : Meta
            define the database in the main class
        """
        database = db
        
"""
Class: Session
        Generates randam token for every section
        new Token is assigned to every User for every new session
"""  
class Session(Model):
    def random_token():
        return "".join([random.choice(string.ascii_letters) for _ in range(20)])

    token = CharField(unique=True, default=random_token)
    user = ForeignKeyField(User)

    class Meta:
        database = db

"""
Class: Contest
        Each Contest instance contains:-
            Code
            Description of contest
            Contest start time and End Time
"""
class Contest(Model):
    code = CharField(unique=True)
    description = CharField()
    start_time = DateTimeField()
    end_time = DateTimeField()

    class Meta:
        database = db

"""
Class: Question
        Each Question has a Question no and a author 
        associated to it
"""
class Question(Model):
    q_no = IntegerField(unique=True)
    author = ForeignKeyField(User)

    class Meta:
        database = db

"""
Class: ContestProblems
    All contest problems belong to a Contest and are itself a question.
        contest defines the instance of Contest Class it belongs
        question defines the questions that belongs to that contest.

"""
class ContestProblems(Model):
    contest = ForeignKeyField(Contest, backref="questions")
    question = ForeignKeyField(Question)

    class Meta:
        database = db
        indexes = ((("contest", "question"), True),)

"""
Class: Submission
    Class defines the submission of solution of a Question
    Stores the information about:
        User that submits the Solution
        Time of Submission
        Contest to whish The question belongs
        Whether the soolution is correct
"""
class Submission(Model):
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

# Create a test User
test = User.get_or_create(username="test", password="test")

# Create test Questions
q1 = Question.get_or_create(q_no=1, author=test[0])
q2 = Question.get_or_create(q_no=2, author=test[0])
q3 = Question.get_or_create(q_no=3, author=test[0])
q4 = Question.get_or_create(q_no=4, author=test[0])
q5 = Question.get_or_create(q_no=5, author=test[0])
q6 = Question.get_or_create(q_no=6, author=test[0])

# Add Questions to contest 
"""Contest Problem Instance is created which is used to assign question to specific contests."""
ContestProblems.get_or_create(contest=practiceContest[0], question=q1[0])
ContestProblems.get_or_create(contest=practiceContest[0], question=q2[0])
ContestProblems.get_or_create(contest=pastContest[0], question=q1[0])
ContestProblems.get_or_create(contest=pastContest[0], question=q2[0])
ContestProblems.get_or_create(contest=ongoingContest[0], question=q3[0])
ContestProblems.get_or_create(contest=ongoingContest[0], question=q4[0])
ContestProblems.get_or_create(contest=futureContest[0], question=q5[0])
ContestProblems.get_or_create(contest=futureContest[0], question=q6[0])


"""
Function: login_required
        Extends the functainality of a funcion by checking log in condition.
        Checks if the user is logged in.if not redirect the user to home page 
        with message 'Login Required'
    parameters : Function on which decorator is applied  
"""
def login_required(function):
    def login_redirect(*args, **kwargs):
        if not logggedIn():
            return bottle.template("home.html", message="Login required.")
        return function(*args, **kwargs)

    return login_redirect


"""
Function: changePath
    redirects to home page
"""
@app.route("/")# Sets the url that trigger following function
def changePath():
    return bottle.redirect("/home")


"""
Function: home
    redirects to Dashboard of the user
"""
@app.get("/home")# Sets the base url as the argument.
def home():    
    if logggedIn():
        return bottle.redirect("/dashboard")
    return bottle.template("home.html", message="")

"""
Function: dashboard
    redirects to Dashboard of the user
"""
@app.get("/dashboard")# Sets the base url as the argument.
@login_required# Checks if user is logged in or not
def dashboard():
    contests = Contest.select().order_by(Contest.start_time)
    return bottle.template("dashboard.html", contests=contests)


"""
Function: question
        Checks if the question and Contest it belongs does exists.
        If exists : it checks the current status of the contest
        And then returns the question state ment along with question numbers
        and contest code to the Template
    Parameters:
        code: Contest Code
        number: Question Number
    Return: 
        Question Template
"""
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


"""
Function: contest: Function
        Checks if contest exists by validating the contest id.
        Checks the the current staus of code
    Parameters:
        code : contest code
    Return :
        Contest Template
"""
@app.get("/contest/<code>")
@login_required
def contest(code):
    try:
        contest = Contest.get(Contest.code == code)
    except Contest.DoesNotExist:
        return bottle.abort(404, "no such contest")
    if contest.start_time > datetime.datetime.now():
        return "The contest had not started yet."
    return bottle.template("contest.html", contest=contest, questions=contest.questions)


"""
Function: download 
        Downloads the question to local system
    Parameters:
        path :path to download from
    Return :
        Static Files: Downloadable Files
"""
@app.get("/question/<path:path>")
def download(path):
    return bottle.static_file(path, root=question_dir)


"""
Function: server_static
         Static files for server
    Parameters:
        path :path of file 
    Return :
        Static Files
"""
@app.get("/static/<filepath:path>")
def server_static(filepath):
    return bottle.static_file(filepath, root=os.path.join(dir_path, "static"))


"""
Function: contest_ranking
        Generates rankinks of users in a Contest i.e the Contest results
        Validates the Sumbission And Contest 
        Checks the number of correct submissions for each user and Added to 
        list with tuples of Username Along with thier Scores . The tuples 
        are added to list in descending order of the score .Then rankings are 
        given to each Username in the list.
        
    Parameters:
        code : contest code
    Return :
        Ranking Template with ranks of different user in  a contest.
"""
@app.get("/ranking/<code>")
def contest_ranking(code):
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


"""
Function: rankings 
        Overall Ranking of the user over all the Contest.
    Parameters:
        None
    Return :
        Ranking Template with Overall Ranking
"""
@app.get("/ranking")
def rankings():
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


"""
Function: loggedIn
        Downloads the question to local system
    Parameters:
        None
    Return :
        True: if Session exixsts for the user Logged In
        False: if Session not exixst for the user Logged In
            or if the s_id is not present or is wrong
"""
def logggedIn():
    if not bottle.request.get_cookie("s_id"):
        return False
    return (
        Session.select()
        .where(Session.token == bottle.request.get_cookie("s_id"))
        .exists()
    )


"""
Function: createSession
        Create a session for the user
        Set up cookie for The current session with seesion id ,token and expiry 
        time
    Parameters:
        username: Username of user For whom session is Created.
    Return :
        Redirects to user Dashoard
"""
def createSession(username):
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


"""
Function: login
        This function is called whenever user log in to the app
        Checks if the user entered the Right credentials for log in
    Parameters:
        None
    Return :
        Redirects to home if invalid credenial
        Else Creates the session for the user  
"""
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


"""
Function: resgiter 
        This function is called whenever new user registers
        New User is Created in the Data base and his credentials are stored
        Checks if the user with same username already exisxts
    Parameters:
        None
    Return :
        Creates session for new user.
"""
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


"""
Function: logout
        Ends the session for the user 
        Deletes the session cookie
        
    Parameters:
        None
    Return :
        Redirects to Home Page
"""
@app.get("/logout")
def logout():
    Session.delete().where(Session.token == bottle.request.get_cookie("s_id")).execute()
    bottle.response.delete_cookie("s_id")
    return bottle.redirect("/home")


"""
Function: file_upload 
       This Function is used to upload the submission to  Question to the Server.
    Parameters:
        code: Contest Code 
        number : Question No of ehich solution is uploaded
    Return :
        "Wrong Answer!! : If solution is wrong
        "Solved! Great Job! " : If solution is correct    
"""
@app.post("/check/<code>/<number>")
@login_required 
def file_upload(code, number):
    try:
        contestProblem = ContestProblems.get(
            ContestProblems.contest == Contest.get(Contest.code == code),
            ContestProblems.question == Question.get(Question.q_no == int(number)),
        )
    except:
        return bottle.abort(404, "no such contest problem")
    user = Session.get(Session.token == bottle.request.get_cookie("s_id")).user
    time = datetime.datetime.now()
    uploaded = bottle.request.files.get("upload").file.read() # read the uploaded File
    with open(os.path.join(question_dir, number, "output.txt"), "rb") as fl:
        expected = fl.read()
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = uploaded == expected
    
    try:
        Submission.create(
            user=user, contestProblem=contestProblem, time=time, is_correct=ans
        )# Add Submission For User
    except:
        bottle.abort(500, "Error in inserting submission to database.")
    
    if not ans: # if Answer is Wrong
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job! "


"""
Function: error404 
        Handles Error  
    Parameter:
        error : Error rturned the App
    Return :
        Redirects to 
        
"""
@app.error(404) # Checks if app returns an error with error code as argument
def error404(error):
    return template("error.html", errorcode=error.status_code, errorbody=error.body)


bottle.run(app, host="localhost", port=8080)
