from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.models.models import Room
from app.repository.RoomRepo import RoomRepo


class RoomService:
    def __init__(
            self,
            room_repo: Annotated[RoomRepo, Depends()]
    ) -> None:
        self.room_repo = room_repo

    async def get_room_by_uuid(self, room_uuid: UUID) -> Room | None:
        db_item = await self.room_repo.get_by_uuid(room_uuid)

        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_uuid}` not found!")

        return db_item