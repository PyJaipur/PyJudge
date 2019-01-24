from bottle import Bottle, run, template, static_file, request, route
import os
import sys
import datetime
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = Bottle()

usernames = {}  #dictionary for storing the usernames

question_dir = 'files/questions'
questions = {}
for i in os.listdir(question_dir):
    questions[i] = {}
    with open(os.path.join(question_dir, i, 'output.txt'), 'r') as fl:
        questions[i]['output'] = fl.read()
    with open(os.path.join(question_dir, i, 'statement.txt'), 'r') as fl:
        questions[i]['question'] = fl.read()


@app.get('/question/<number>')
def question(number):
    global questions
    statement = questions[number]['question']
    return(template('index.html', question_number = number, question = statement))

@app.get('/question/<path:path>') 
def download(path):
  return static_file(path, root=question_dir)


@app.post('/check/<number>')
def file_upload(number):
    u_name = request.forms.get('username') #accepting username
    # storing usernames' submission along with the timestamp at which they submit it
    global usernames
    time = datetime.datetime.now()
    if u_name not in usernames:
        usernames[u_name] = [(uploaded, time)]
    else:
        usernames[u_name].append((uploaded,time))
    uploaded = request.files.get('upload').file.read() #uploaded outputs by user
    expected = questions[number]['output']
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = (uploaded==expected)
    
    if not ans:   
        return "Wrong Answer!!"
    else:       
        return "Solved! Great Job! "


run(app, host='localhost', port=8080)
