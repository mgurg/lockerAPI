from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT

from app.datbase.bearer_auth import is_app_owner
from app.schemas.ai_game import (
    AnswerRequest,
    AnswerResponse,
    CurrentPuzzleResponse,
    GameOutro,
    GameStart,
    GameStartResponse,
    IntroResponse,
    ReviewRequest,
)
from app.service.GameService import GameService

game_router = APIRouter()

gameServiceDependency = Annotated[GameService, Depends()]


@game_router.post("/start")
async def start_game(game_service: gameServiceDependency, setup: GameStart,
                     auth=Depends(is_app_owner)) -> GameStartResponse:
    return await game_service.start(setup)


@game_router.get("/intro/{game_uuid}")
async def get_intro(
    game_service: gameServiceDependency,
    game_uuid: UUID,
    request: Request,
    x_forwarded_for: Annotated[str | None, Header()] = None,
    auth=Depends(is_app_owner)
) -> IntroResponse:
    client_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    return await game_service.intro(game_uuid, client_ip)


@game_router.get("/puzzle/{game_uuid}")
async def get_puzzle(game_service: gameServiceDependency, game_uuid: UUID,
                     auth=Depends(is_app_owner)) -> CurrentPuzzleResponse:
    return await game_service.generate_puzzle(game_uuid)


@game_router.post("/answer/{game_uuid}")
async def submit_answer(
        game_service: gameServiceDependency, game_uuid: UUID, answer: AnswerRequest, auth=Depends(is_app_owner)
) -> AnswerResponse:
    return await game_service.answer(game_uuid, answer.choice)


@game_router.get("/ending/{game_uuid}")
async def get_ending(game_service: gameServiceDependency, game_uuid: UUID, auth=Depends(is_app_owner)) -> GameOutro:
    return await game_service.ending(game_uuid)


@game_router.post("/review/{game_uuid}", status_code=HTTP_204_NO_CONTENT)
async def add_review(game_service: gameServiceDependency, game_uuid: UUID, review: ReviewRequest,
                     auth=Depends(is_app_owner)) -> None:
    await game_service.review(game_uuid, review)
    return None
