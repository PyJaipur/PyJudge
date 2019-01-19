from bottle import Bottle, run, template, static_file, request, route
import os
import sys
import datetime
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = Bottle()

no_of_attempts = 0
user_attempt_history = []
with open('./files/expected_outputs/expected_output.txt', 'r') as fl:
   expected = fl.read()


@app.get('/question/<number>')
def question1(number):
    return static_file('index.html', root=dir_path)

@app.get('/question/<number>/download/')
def download(number):
    input_file_name = 'inputs.txt'
    return static_file(input_file_name, root=dir_path+'/'+'files/questions/'+str(number)+'/')

@app.route('/question/<number>/upload/', method = 'POST') # method = 'POST'
def file_upload(number):
    uploaded = request.files.get('upload').file.read() #uploaded outputs by user


    current_time = datetime.datetime.now()
    global expected
    global no_of_attempts
    global user_attempt_history
    global expected

    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = (uploaded==expected)
    
    if not ans:
        no_of_attempts += 1
        user_attempt_history.append(['name', number, no_of_attempts, current_time])
        return "Wrong Answer!!"
    else:
        user_attempt_history.append(['name', number, no_of_attempts, current_time])
        return "Solved! Great Job! "


run(app, host='localhost', port=8080)
