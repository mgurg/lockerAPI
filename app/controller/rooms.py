from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.status import HTTP_204_NO_CONTENT

from app.schemas.requests import RoomAdd
from app.schemas.responses import RoomIndexResponse, RoomsPaginated
from app.service.RoomService import RoomService

room_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
roomServiceDependency = Annotated[RoomService, Depends()]


@room_router.get("/{room_uuid}")
async def room_by_uuid(room_service: roomServiceDependency, room_uuid: UUID):
    db_item = await room_service.get_room_by_uuid(room_uuid)

    return db_item


@room_router.get("/url/{language}/{room_url_slug}")
async def room_by_url_slug(room_service: roomServiceDependency, language: CountryAlpha2,
                           room_url_slug: str) -> RoomIndexResponse:
    db_item = await room_service.get_room_by_url_slug_and_language(
        room_url_slug, language, ["location", "translations"]
    )

    return db_item


@room_router.get("/url/{language}/place/{location}")
async def rooms_by_location(
        room_service: roomServiceDependency,
        language: LanguageAlpha2, location: str,
        limit: int = 10,
        offset: int = 0,
        field: Literal["name", "created_at"] = "name",
        order: Literal["asc", "desc"] = "asc",
):
    relations = ["location", "translations"]
    db_rooms, count = await room_service.get_rooms_by_location_and_language(
        location,
        language,
        relations,
        offset, limit, field, order,
    )

    return RoomsPaginated(data=db_rooms, count=count, offset=offset, limit=limit)


@room_router.post("/department")
async def add_department(room_service: roomServiceDependency, room: RoomAdd):
    db_item = await room_service.create_room(room)

    return db_item


@room_router.post("")
async def add_room(room_service: roomServiceDependency, room: RoomAdd):
    db_item = await room_service.create_room(room)

    return db_item


@room_router.delete("/{room_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_room(room_service: roomServiceDependency, room_uuid: UUID):
    await room_service.delete_room(room_uuid)

    return None


@room_router.delete("/department/{department_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_department(room_service: roomServiceDependency, department_uuid: UUID):
    return None
