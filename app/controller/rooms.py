from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic_extra_types.country import CountryAlpha2

from app.schemas.requests import RoomAdd
from app.service.RoomService import RoomService

room_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
roomServiceDependency = Annotated[RoomService, Depends()]


@room_router.get("/{room_uuid}")
async def room_by_uuid(room_service: roomServiceDependency, room_uuid: UUID):
    db_item = await room_service.get_room_by_uuid(room_uuid)

    return db_item


@room_router.get("/url/{language}/{room_url_slug}")
async def room_by_url_slug(room_service: roomServiceDependency, language: CountryAlpha2, room_url_slug: str):
    db_item = await room_service.get_room_by_url_slug_and_language(room_url_slug, language,
                                                                   ["location", "translations"])

    return db_item


@room_router.get("/url/{language}/place/{location}")
async def rooms_by_location(room_service: roomServiceDependency, language: CountryAlpha2, location: str):
    db_items = await room_service.get_room_by_location_and_language(location, language,
                                                                   ["city", "location", "translations"])

    return db_items


@room_router.post("/department")
async def add_room(room_service: roomServiceDependency, room: RoomAdd):
    db_item = await room_service.create_room(room)

    return db_item


@room_router.post("")
async def add_room(room_service: roomServiceDependency, room: RoomAdd):
    db_item = await room_service.create_room(room)

    return db_item
