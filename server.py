from bottle import Bottle, run, template, static_file, request, route
import os
import sys
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

app = Bottle()

with open('./files/expected_outputs/expected_output.txt', 'r') as fl:
    expected = fl.read()

@app.route('/hello/<something>')
def index(something):
    return template('<b>Hello My Name is {{something}}</b>', something='Shivank')


@app.get('/question/<number>')
def question1(number):
    return static_file('index.html', root=dir_path)
    #return '''<b>Add given two numbers in given text file and upload your solution in a text file.</b>\n<a href="http://localhost:8080/question/1/download/">Download Test Case</a>:
    # <a href="http://localhost:8080/question/1/submit">Submit Outputs</a>


#@app.route('/question/<number>/submit')
#def submit(number):
 #   return static_file('index.html' , root=dir_path)


@app.get('/question/<number>/download/')
def download(number):
    input_file_name = 'inputs'+number+'.txt'
    return static_file(input_file_name, root=dir_path+'/'+'files/questions/')

@app.route('/upload', method = 'POST')
def file_upload():
    uploaded = request.files.get('upload').file.read() #uploaded outputs by user
    expected.strip()
    uploaded.strip()
    ans = (uploaded==expected)

    if ans==False:
        return "Wrong Answer!!"
    else: 
        return "Solved! Great Job!"


run(app, host='localhost', port=8080)
