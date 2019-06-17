import requests
import datetime
import os


path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
question_dir = "files/questions"

with requests.Session() as session:
    register = session.post(
        "http://localhost:8080/register", data={"username": "test", "password": "test"}
    )

    login = session.post(
        "http://localhost:8080/login", data={"username": "test", "password": "test"}
    )

    for i in range(1, 7, 1):
        Question1 = session.post(
            "http://localhost:8080/questionInput",
            files={
                "question": open(
                    os.path.join(question_dir, str(i), "inputs.txt"), "rb"
                ),
                "answer": open(os.path.join(question_dir, str(i), "output.txt"), "rb"),
            },
            data={"statement": str(i)},
        )

    Contest1 = session.post(
        "http://localhost:8080/contestInput",
        data={
            "code": "PRACTICE",
            "description": "practice questions",
            "start_time": datetime.datetime(day=1, month=1, year=1),
            "end_time": datetime.datetime(day=1, month=1, year=9999),
            "selection": [1, 2],
        },
    )
    Contest2 = session.post(
        "http://localhost:8080/contestInput",
        data={
            "code": "PASTCONTEST",
            "description": "somewhere in the past",
            "start_time": datetime.datetime(day=1, month=11, year=2018),
            "end_time": datetime.datetime(day=1, month=12, year=2018),
            "selection": [1, 2],
        },
    )
    Contest3 = session.post(
        "http://localhost:8080/contestInput",
        data={
            "code": "ONGOINGCONTEST",
            "description": "somewhere in the present",
            "start_time": datetime.datetime(day=1, month=4, year=2019),
            "end_time": datetime.datetime(day=1, month=6, year=2019),
            "selection": [3, 4],
        },
    )
    Contest4 = session.post(
        "http://localhost:8080/contestInput",
        data={
            "code": "FUTURECONTEST",
            "description": "somewhere in the future",
            "start_time": datetime.datetime(day=1, month=1, year=2020),
            "end_time": datetime.datetime(day=1, month=10, year=2020),
            "selection": [5, 6],
        },
    )
