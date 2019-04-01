import unittest
import pytest
#import server as app
import requests

url = 'http://localhost:8080'

def test_question():
    r = requests.get(url+'/question/1')
    assert r.status_code == 200

def test_download():
    assert requests.get(url+'/question/1/inputs.txt').status_code == 200

def test_file_upload():
    files= '/question/1/output.txt'
    global url
    url += '/check/1/output.txt'
    assert requests.post(url, files = files).status_code == 200   # givin a error
