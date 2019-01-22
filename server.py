from bottle import Bottle, run, template, static_file, request, route
import os
import sys
import datetime
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
app = Bottle()


#with open('./files/expected_outputs/expected_output.txt', 'r') as fl:
   # expected = fl.read()

@app.get('/question/<number>')
def question1(number):
    file_path = './files/questions/'+ str(number) + '/statement.txt'
    with open(file_path, 'r') as inputs:
        ques = inputs.read()
    download_link = '/question/' + str(number)+ '/download/'
    return template('question_template.tpl', question = ques, link_to_download = download_link, number = number) # root=dir_path+'/'+'views'


@app.get('/question/<number>/download/')
def download(number):
    input_file_name = 'inputs.txt'
    return static_file(input_file_name, root=dir_path+'/'+'files/questions/'+str(number)+'/')


@app.route('/question/<number>/upload', method = 'POST')
def file_upload(number):
    file_path = './files/questions/'+ str(number) + '/output.txt'
    with open(file_path, 'r') as fl:
        expected = fl.read()
    uploaded = request.files.get('upload').file.read() #uploaded outputs by user

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
