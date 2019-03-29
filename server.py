class User:
	def __init__(self):
		self.score = 0
		self.solvedQuestions = set()
		self.submissions = list()
	def getScore(self):
		return self.score
	def incrementScore(self):
		self.score += 1
	def addQuestion(self,number):
		self.solvedQuestions.add(int(number))

from bottle import Bottle, run, template, static_file, request, route, redirect
import os
import sys
import datetime
from collections import defaultdict, namedtuple

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = Bottle()

questions = {}
usernames = defaultdict(list)  # dictionary for storing the usernames
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
	for u_name in usernames.keys():
		people.append([u_name,usernames[u_name].getScore(),0])
	people.sort(key=lambda x: x[1],reverse=True)
	# rank
	for i in range(len(people)):
		people[i][2] = i+1
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
    if not u_name in usernames.keys():
    	usernames[u_name] = User()
    usernames[u_name].submissions.append(Submission(question=number, time=time,
                                        output=uploaded, result=ans))
    if not ans:
        return "Wrong Answer!!"
    else:
        if not (int(number) in usernames[u_name].solvedQuestions):
        	usernames[u_name].incrementScore()
        	usernames[u_name].addQuestion(number)
        return "Solved! Great Job! "

                                                            
run(app, host='localhost', port=8080)
