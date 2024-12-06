from fastapi.testclient import TestClient
from main import app, db_dependencies, get_question, get_choice, check, create_questions, delete_question, delete

client = TestClient(app)
db = db_dependencies()


def test_delete_all():
    response = client.delete("/delete_all")
    assert response.status_code == 200
    assert response.content == b'{"message":"Successfully deleted"}'


def test_create_question():
    question_data = {
        "question_text": "Which is the best Python framework?",
        "choices": [
            {"choice_text": "FastAPI", "is_correct": True},
            {"choice_text": "Starlette", "is_correct": False}
        ]
    }
    incorrect_question_data = {
        "question_text": "Which is the best Python framework?",
        "choices": [
            {"choice_text": "FastAPI", "is_correct": False},
            {"choice_text": "Starlette", "is_correct": False}
        ]
    }
    incorrect_response = client.post("/create_questions", json=incorrect_question_data)
    assert incorrect_response.status_code == 400
    assert incorrect_response.content == b'{"message":"Please give least one choice with True value"}'
    response = client.post("/create_questions", json=question_data)
    assert response.status_code == 200
    assert response.content == b'{"message":"successfully posted"}'
    response = client.post("/create_questions", json=incorrect_question_data)
    assert response.status_code == 400
    assert response.content == b'{"message":"Question already exists"}'
