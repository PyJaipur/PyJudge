import unittest
import server
from webtest import TestApp

app = TestApp(server.app)
class TestPyJudge(unittest.TestCase):
    
    def test_question(self):
        assert app.get('/question/1').status_code == 200

    def test_download(self):
        assert app.get('/question/1/inputs.txt').status_code == 200

    def test_file_upload(self):
        #assert app.post('/check/1').status_code == 200
        print(app.post('/check/1',  expect_errors=True).status_code)




if __name__=='__main__':
  unittest.main()