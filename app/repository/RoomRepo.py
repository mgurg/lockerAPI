from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.models import Room
from app.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class RoomRepo(GenericRepo[Room]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Room
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> Room | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
