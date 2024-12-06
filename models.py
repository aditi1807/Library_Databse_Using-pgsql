from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, UniqueConstraint
from database import Base


class Questions(Base):
    __tablename__ = 'questions'

    question_id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, unique=True,index=True)


class Choices(Base):
    __tablename__ = 'choices'

    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(String, index=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    question_id = Column(Integer, ForeignKey("questions"))
