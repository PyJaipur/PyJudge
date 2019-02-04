import requests as R


def api(x):
    return "http://localhost:8080" + x


def test_sanity():
    assert 1 == 1, "This should never fail"


def test_question_statement_can_be_obtained():
    r = R.get(api("/question/1"))
    assert r.status_code == 200
    assert "Find The Sum" in r.text


def test_question_input_file_is_available():
    r = R.get(api("/question/1/inputs.txt"))
    assert r.status_code == 200


def test_question_submission_fails_for_wrong_answer():
    r = R.post(
        api("/check/1"),
        json={"username": "chacha chaudhary"},
        files={"upload": ("myoutput.txt", b"something wrong")},
    )
    assert r.status_code == 200
    assert "wrong" in r.text.lower()


def test_question_submission_passes_for_correct_answer():
    path = "files/questions/1/output.txt"
    with open(path, "rb") as output_file:
        r = R.post(
            api("/check/1"),
            json={"username": "chacha chaudhary"},
            files={"upload": output_file},
        )
    assert r.status_code == 200
    assert "solved" in r.text.lower()
