import pytest
from server import app
from webtest import TestApp

# import requests

# url = 'http://localhost:8080'


def test_demo():
    assert 1 == 1


@pytest.fixture(scope="module")
def application():
    test_app = TestApp(app)
    return test_app


def test_handlers(application):
    handlers = ["/dashboard", "/home"]
    for handler in handlers:
        assert application.get(handler).status == "200 OK"


# def test_question():
#    r = requests.get(url+'/question/1')
#    assert r.status_code == 200

# def test_download():
# time = datetime.datetime.now()

# type(uploaded) == <class 'bytes'>
# uploaded outputs by user
#    assert requests.get(url+'/question/1/inputs.txt').status_code == 200

# def test_file_upload():
#    files= {'upload' : open('files/questions/1/output.txt', 'rb')}
#    global url
#    check_url = url + '/check/1'

#    assert requests.post(check_url, files = files).status_code == 200
