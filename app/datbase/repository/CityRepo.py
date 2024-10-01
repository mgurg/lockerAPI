from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic_extra_types.country import CountryAlpha2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.datbase.db import get_db
from app.datbase.models.models import City, GeoName
from app.datbase.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class CityRepo(GenericRepo[City]):
    def __init__(self, session: UserDB) -> None:
        self.Model = City
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> City | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_place_by_name(self, place_name: str, language: CountryAlpha2 | None = None):
        # Base query with join on the relationship
        query = select(City).join(City.geo_names).where(GeoName.name_ascii == place_name)

        # Add language filter if provided
        if language:
            query = query.where(GeoName.lang == language)

        query = query.options(selectinload(City.geo_names))

        # Execute the query
        result = await self.session.execute(query)

        # Return the first matching city
        # city = result.scalars().all()
        city = result.scalars().first()

        return city

    async def get_places_by_bbox(self, latitude: float, longitude: float) -> Sequence[City]:
        query = (
            select(self.Model)
            .where(
                (self.Model.lat_min <= latitude) &
                (self.Model.lat_max >= latitude) &
                (self.Model.lng_min <= longitude) &
                (self.Model.lng_max >= longitude)
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()
