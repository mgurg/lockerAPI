from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2

from app.database.db import get_db
from app.database.models.models import GeoName
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class GeoNameRepo(GenericRepo[GeoName]):
    def __init__(self, session: UserDB) -> None:
        self.Model = GeoName
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> GeoName | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ascii_name(self, name: str) -> Sequence[GeoName]:
        query = select(self.Model).where(self.Model.name_ascii == name)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_country_and_lang(self, country: CountryAlpha2, lang:LanguageAlpha2) -> Sequence[GeoName]:
        query = select(self.Model).where(self.Model.country == country).where(self.Model.lang == lang)

        result = await self.session.execute(query)
        return result.scalars().all()
    