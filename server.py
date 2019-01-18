from bottle import Bottle, run, template, static_file, request, route
import os
import sys
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)



app = Bottle()


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
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)

    save_path = "./files/user_outputs/"
    upload.save(save_path)  # appends upload.filename automatically
    
    userpath = "./files/user_outputs/" + name + '.' + ext

    with open('./files/expected_outputs/expected_output.txt','r') as f2 , open(userpath,'r') as f1:
        ans = True
        for line1,line2 in zip(f1,f2):
            if ans!=True:
                break
            elif line1!=line2:
                ans = False
            else:
                continue

    if ans==False:
        return "Wrong Answer!!"
    else: 
        return "Solved! Great Job!"


run(app, host='localhost', port=8080)
