from datetime import datetime
from typing import Annotated
from uuid import UUID

from annotated_types import Gt
from pydantic import BaseModel, EmailStr, StringConstraints


class Option(BaseModel):
    number: int
    text: str


class GameStart(BaseModel):
    theme: Annotated[str, StringConstraints(max_length=100)]
    description: Annotated[str, StringConstraints(max_length=140)]
    difficulty: Annotated[str, StringConstraints(max_length=100)]
    category: Annotated[str, StringConstraints(max_length=100)]
    occasion: Annotated[str, StringConstraints(max_length=100)]
    email: Annotated[EmailStr, StringConstraints(max_length=100)] | None = None


class WrongFeedback(BaseModel):
    number: int
    feedback: str


class PuzzleResponse(BaseModel):
    scenario: str
    base_hint: str
    options: list[Option]
    correct: Annotated[int, Gt(0)]
    result: str
    wrong_feedback: list[WrongFeedback]


class GenericList(BaseModel):
    value: str


class GameIntro(BaseModel):
    intro: str
    # puzzles: list[PuzzleResponse]


class GameOutro(BaseModel):
    outro: str


class GameState(BaseModel):
    theme: str
    details: str
    current_puzzle: int
    wrong_answers: int
    moves: int
    hints_remaining: int
    game_state: str
    story: str
    puzzle_descriptions: list[str]
    puzzle_history: list[str]


class GameStartResponse(BaseModel):
    uuid: UUID
    token: str
    intro: str
    created_at: datetime


class CurrentPuzzleResponse(BaseModel):
    scenario: str
    base_hint: str
    options: list[Option]
    correct: int
    result: str
    wrong_feedback: list[WrongFeedback]
    current_puzzle: int


class IntroResponse(BaseModel):
    theme: str
    intro: str


class AnswerRequest(BaseModel):
    choice: Annotated[int, Gt(0)]


class AnswerResponse(BaseModel):
    result: str
    correct: bool


class ReviewRequest(BaseModel):
    text: str
    score: int
