from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool


class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependencies = Annotated[Session, Depends(get_db)]


@app.get("/question/{question_id}")
def get_question(question_id: int, db: db_dependencies):
    res = db.query(models.Questions).filter(models.Questions.question_id == question_id).first()
    if res is not None:
        return JSONResponse(
            status_code=200,
            content={"message": f'Answer the following question {res.question_text}'}
        )

    raise HTTPException(
        status_code=400,
        detail="Kindly give correct question Id"
    )


@app.get("/check/{question_id}")
def check(question_id:int, answer: str, db:db_dependencies):
    choices = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    for choice in choices:
        if choice.choice_text == answer:
            return True
    return False


@app.get("/choice/{choice_id}")
def get_choice(question_id: int, db: db_dependencies):
    res = []
    for choice in db.query(models.Choices).filter(models.Choices.question_id == question_id).all():
        res.append(choice.choice_text)
    if len(res) != 0:
        return JSONResponse(
            status_code=200,
            content={"message": f'The choices of the question is {res}'}
        )
    raise HTTPException(
        status_code=400,
        detail="There is no choice for the question"
    )


@app.post("/create_questions")
def create_questions(question: QuestionBase, db: db_dependencies):
    db_response = db.query(models.Questions).filter(models.Questions.question_text == question.question_text).first()
    if db_response is not None:
        return JSONResponse(
            status_code=400,
            content={"message": "Question already exists"}
        )
    flag: bool = False
    for choice in question.choices:
        if choice.is_correct is True:
            flag = True
    if flag is False:
        return JSONResponse(
            status_code=400,
            content={"message": "Please give least one choice with True value"}
        )
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct,
                                   question_id=db_question.question_id)
        db.add(db_choice)
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"message": "successfully posted"}
    )


@app.delete("/delete_question/{question_id}")
def delete_question(question_id: int, db: db_dependencies):
    question = db.query(models.Questions).filter(models.Questions.question_id == question_id).first()
    if question is None:
        raise HTTPException(
            detail="question_id incorrect"
        )
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    db.query(models.Questions).filter(models.Questions.question_id == question_id).delete()

    db.commit()


@app.delete("/delete_all")
def delete(db: db_dependencies):
    db.query(models.Choices).delete()
    db.query(models.Questions).delete()
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"message": "Successfully deleted"}
    )
