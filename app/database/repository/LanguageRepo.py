from typing import Annotated

from fastapi import Depends
from pydantic_extra_types.language_code import LanguageAlpha2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.database.models.models import Language
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class LanguageRepo(GenericRepo[Language]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Language
        super().__init__(session, self.Model)

    async def get_by_codes(self, codes: list[LanguageAlpha2]):
        query = select(self.Model).where(self.Model.code.in_(codes))

        result = await self.session.execute(query)

        return result.scalars().all()
