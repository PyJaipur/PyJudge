from bottle import Bottle, run, template, static_file, request, route
import os
import sys
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

app = Bottle()

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
    with open('./files/expected_outputs/expected_output.txt', 'r') as fl:
        expected = fl.read()
    expected = expected.strip()
    uploaded = uploaded.strip()
    ans = (uploaded==expected)

    if not ans:
        return "Wrong Answer!!"
    else:
        return "Solved! Great Job!"


run(app, host='localhost', port=8080)
