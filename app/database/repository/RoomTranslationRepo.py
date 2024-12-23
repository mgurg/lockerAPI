from typing import Annotated

from fastapi import Depends
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.database.models.models import RoomTranslation
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class RoomTranslationRepo(GenericRepo[RoomTranslation]):
    def __init__(self, session: UserDB) -> None:
        self.Model = RoomTranslation
        super().__init__(session, self.Model)

    async def get_translations_by_room_id(self, room_id: int) -> Sequence[RoomTranslation]:
        query = (
            select(self.Model)
            .where(self.Model.room_id == room_id)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
