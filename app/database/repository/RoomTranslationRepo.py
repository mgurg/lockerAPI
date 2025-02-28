from typing import Annotated

from fastapi import Depends
from sqlalchemy import Sequence, delete, select
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

    async def delete_by_room_id(self, room_id: int) -> None:
        query = delete(self.Model).where(self.Model.room_id == room_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_translation_by_room_id_and_lang(self, room_id: int, lang_code: str, default_lang: str = "pl") -> RoomTranslation | None:
        """
        Fetch the room translation for a given language.
        If not found, fetch the default language translation.
        """
        query = (
            select(self.Model)
            .where(self.Model.room_id == room_id)
            .where(self.Model.lang.in_([lang_code, default_lang]))  # Look for both languages
            # .order_by(self.Model.lang == lang_code.desc())  # Prefer the requested language first
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
