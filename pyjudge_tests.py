import pytest
import server as app

def test_question(self):
    assert app.get('/question/1').status_code == 200

def test_download(self):
    assert app.get('/question/1/inputs.txt').status_code == 200

def test_file_upload(self):
        #assert app.post('/check/1').status_code == 200
    print(app.post('/check/1',  expect_errors=True).status_code)

