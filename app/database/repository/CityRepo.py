from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic_extra_types.country import CountryAlpha2
from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import get_db
from app.database.models.models import City, GeoName
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class CityRepo(GenericRepo[City]):
    def __init__(self, session: UserDB) -> None:
        self.Model = City
        super().__init__(session, self.Model)

    def _apply_relationship_loading(self, query, load_relations: list[str | BinaryExpression] = None):
        if not load_relations:
            return query

        for relation in load_relations:  # load_relations=["*"]
            if relation == "*":
                return query.options(selectinload("*"))
            elif isinstance(relation, str):  # load_relations=["city", "location"]
                query = query.options(selectinload(getattr(self.Model, relation)))
            elif isinstance(relation, BinaryExpression):  # load_relations=[Room.city, Room.location]
                query = query.options(selectinload(relation))

        return query

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

    async def get_places_by_bbox(self,
                                 latitude: float,
                                 longitude: float,
                                 load_relations: list[str | BinaryExpression] = None
                                 ) -> Sequence[City]:
        query = (
            select(self.Model)
            .where(
                (self.Model.lat_min <= latitude) &
                (self.Model.lat_max >= latitude) &
                (self.Model.lon_min <= longitude) &
                (self.Model.lon_max >= longitude)
            )
        )
        query = self._apply_relationship_loading(query, load_relations)
        result = await self.session.execute(query)
        return result.scalars().all()
