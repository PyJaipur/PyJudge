from bottle import Bottle, run, template, static_file
import os
import sys
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)



app = Bottle()

@app.route('/hello/<something>')
def index(something):
    return template('<b>Hello My Name is {{something}}</b>', something = 'Shivank')

@app.get('/question/<number>')
def question1(number):
    return '''<b>Add given two numbers in given text file and upload your solution in a text file.</b>\n<a href="http://localhost:8080/question/1/download/">Download Test Case</a>:
'''



@app.route('/question/<number>/download/')
def download(number):
    return static_file('inputs1.txt', root=dir_path+'/'+'files/questions/')


run(app, host = 'localhost', port = 8080)


