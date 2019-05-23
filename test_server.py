import unittest
import pytest
#import server as app
import requests

def test_demo():
    assert 1==1
"""
url = 'http://localhost:8080'

def test_question():
    r = requests.get(url+'/question/1')
    assert r.status_code == 200

def test_download():
    #time = datetime.datetime.now()

    # type(uploaded) == <class 'bytes'>
    # uploaded outputs by user
    assert requests.get(url+'/question/1/inputs.txt').status_code == 200

def test_file_upload():
    files= {'upload' : open('files/questions/1/output.txt', 'rb')}
    global url
    check_url = url + '/check/1'

    assert requests.post(check_url, files = files).status_code == 200
"""