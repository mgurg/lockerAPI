from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.status import HTTP_204_NO_CONTENT

from app.schemas.requests import RoomAdd, RoomEdit
from app.schemas.responses import RoomIndexResponse, RoomsPaginated
from app.service.RoomService import RoomService

room_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
roomServiceDependency = Annotated[RoomService, Depends()]


@room_router.get("/count")
async def get_rooms_count(room_service: roomServiceDependency) -> int:
    db_rooms_count = await room_service.get_room_count()

    return db_rooms_count


@room_router.get("/nearby/{city_name}")
async def get_rooms_nearby(room_service: roomServiceDependency, city_name: str):
    db_rooms_count = await room_service.get_rooms_nearby(city_name)

    return db_rooms_count


@room_router.get("/{room_uuid}")
async def get_room_by_uuid(room_service: roomServiceDependency, room_uuid: UUID):
    db_item = await room_service.get_room_by_uuid(room_uuid)

    return db_item


@room_router.get("/url/{language}/{room_url_slug}")
async def room_by_url_slug(room_service: roomServiceDependency, language: CountryAlpha2,
                           room_url_slug: str) -> RoomIndexResponse:
    db_item = await room_service.get_room_by_url_slug_and_language(
        room_url_slug, language, ["location", "translations", "department", "tags", "languages"]
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


@room_router.post("")
async def create_room(room_service: roomServiceDependency, room: RoomAdd):
    db_room = await room_service.create_room(room)

    return db_room


@room_router.patch("/{room_uuid}", status_code=HTTP_204_NO_CONTENT)
async def update_room(room_service: roomServiceDependency, room_uuid: UUID, room: RoomEdit) -> None:
    await room_service.update_room(room_uuid, room)
    return None


@room_router.delete("/{room_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_room(room_service: roomServiceDependency, room_uuid: UUID) -> None:
    await room_service.delete_room(room_uuid)

    return None
