from bottle import Bottle, run, template, static_file, request, route
import os
import sys
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

app = Bottle()

question_dir = 'files/questions'
questions = {}
for qno in os.listdir(question_dir):
    questions[qno] = {}
    with open(os.path.join(question_dir, qno, 'expected.txt'), 'r') as fl:
        questions[qno]['expected'] = fl.read()
    with open(os.path.join(question_dir, qno, 'statement.txt'), 'r') as fl:
        questions[qno]['statement'] = fl.read()


@app.get('/question/<number>')
def question1(number):
    return static_file('index.html', root=dir_path)

@app.get('/question/<number>/download/')
def download(number):
    input_file_name = 'inputs'+number+'.txt'
    return static_file(input_file_name, root=dir_path+'/'+'files/questions/')

@app.post('/check/<number>')
def file_upload(qno):
    uploaded = request.files.get('upload').file.read() #uploaded outputs by user
    global questions
    expected = questions[qno]['expected'].strip()
    uploaded = uploaded.strip()
    ans = (uploaded==expected)

    if not ans:
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job!"


run(app, host='localhost', port=8080)
