from bottle import Bottle, run, template, static_file, request, route, redirect
import os
import sys
import datetime
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field

@dataclass
class User:
	submissions: list = field(default_factory = list)
	solvedQuestions: set = field(default_factory = set)

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = Bottle()

questions = {}
usernames = defaultdict(User)  # dictionary for storing the usernames
question_dir = 'files/questions'

Question = namedtuple('Question', 'output statement')
Submission = namedtuple('Submission', 'question time result output')

for i in os.listdir(question_dir):
    if not i.isdigit():
        continue
    # read the correct output as bytes object
    with open(os.path.join(question_dir, i, 'output.txt'), 'rb') as fl:
        output = fl.read()
    with open(os.path.join(question_dir, i, 'statement.txt'), 'r') as fl:
        statement = fl.read()
    questions[i] = Question(output=output, statement=statement)

@app.route('/')
def changePath():
	redirect("/question/1")

@app.get('/question/<number>')
def question(number):
    statement = questions[number].statement
    return template('index.html', question_number=number, question=statement)


@app.get('/question/<path:path>')
def download(path):
    return static_file(path, root=question_dir)


@app.get('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=os.path.join(dir_path, 'static'))

@app.get('/ranking')
def rankings():
	people=[]
	for u_name in usernames:
		people.append([u_name,len(usernames[u_name].solvedQuestions)])
	people.sort(key=lambda x: x[1],reverse=True)
	people = [(user, score, rank) for rank, (user, score) in enumerate(people, start=1)]
	return template('Rankings.html', people=people)

@app.post('/check/<number>')
def file_upload(number):
    u_name = request.forms.get('username')  # accepting username
    time = datetime.datetime.now()
    # type(uploaded) == <class 'bytes'>
    # uploaded outputs by user
    uploaded = request.files.get('upload').file.read()
    expected = questions[number].output
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = (uploaded == expected)
    usernames[u_name].submissions.append(Submission(question=number, time=time,
                                        output=uploaded, result=ans))
    if not ans:
        return "Wrong Answer!!"
    else:
        if not (int(number) in usernames[u_name].solvedQuestions):
        	usernames[u_name].solvedQuestions.add(int(number))
        return "Solved! Great Job! "

                                                            
run(app, host='localhost', port=8080)
