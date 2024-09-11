from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.datbase.db import get_db
from app.datbase.models.models import RoomTranslation
from app.datbase.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class RoomTranslationRepo(GenericRepo[RoomTranslation]):
    def __init__(self, session: UserDB) -> None:
        self.Model = RoomTranslation
        super().__init__(session, self.Model)
