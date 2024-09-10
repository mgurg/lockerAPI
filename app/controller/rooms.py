from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.service.RoomService import RoomService

room_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
roomServiceDependency = Annotated[RoomService, Depends()]


@room_router.get("/{room_uuid}")
async def item_get_one(room_service: roomServiceDependency, room_uuid: UUID):
    db_item = await room_service.get_room_by_uuid(room_uuid)

    return db_item
