import requests
from bottle import Bottle, run, template, static_file, request, route
import os
import sys
import datetime
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

app = Bottle()

usernames = {}  #dictionary for storing the usernames

with open('./files/expected_outputs/expected_output.txt', 'r') as fl:
    expected = fl.read()

@app.get('/question/<number>')
def question1(number):
    return static_file('index.html', root=dir_path)

@app.get('/question/<number>/download/')
def download(number):
    input_file_name = 'inputs'+number+'.txt'
    return static_file(input_file_name, root=dir_path+'/'+'files/questions/')

@app.route('/upload', method = 'POST')
def file_upload():
    uploaded = request.files.get('upload').file.read() #uploaded outputs by user
    u_name = request.forms.get('username') #accepting username

    # storing usernames' submission along with the timestamp at which they submit it
    global usernames
    time = datetime.datetime.now()
    t = time.strftime("%x") + ' ' + time.strftime("%I") + ":" + time.strftime("%M") + ":" + \
        time.strftime("%S") + " " + time.strftime("%p")
    if u_name not in usernames.keys():
        usernames[u_name] = [(uploaded, t)]
    else:
        usernames[u_name].append((uploaded,t))

    global expected
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = (uploaded==expected)

    if not ans:
        return "Wrong Answer!!"
    else: 
        return "Solved! Great Job!"


run(app, host='localhost', port=8080)
