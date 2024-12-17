from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import BinaryExpression, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.datbase.db import get_db
from app.datbase.models.models import Location, Room, RoomTranslation
from app.datbase.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class RoomRepo(GenericRepo[Room]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Room
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

    async def get_by_uuid(self, uuid: UUID) -> Room | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_url_slug(self, slug: str, load_relations: list[str] | str = None) -> Room | None:
        query = select(self.Model).where(self.Model.url_slug == slug)
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_location_and_language(self, slug: str, lang_code: str,
                                       load_relations: list[str | BinaryExpression] = None) -> Room | None:

        ...

    async def get_by_bbox(self, min_lon: float, max_lon: float, min_lat: float, max_lat: float,
                          load_relations: list[str | BinaryExpression] = None) -> Sequence[Room]:
        # bbox = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude

        location_subquery = (
            select(Location.id)
            .where(
                (Location.lon >= min_lon) & (Location.lon <= max_lon),
                (Location.lat >= min_lat) & (Location.lat <= max_lat)
            ).subquery()
        )

        # Join the rooms with the locations subquery
        query = (
            select(self.Model)
            .join(location_subquery, self.Model.location_id == location_subquery.c.id)
        )

        query = self._apply_relationship_loading(query, load_relations)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_nearby_rooms(self, lat: float, lon: float, load_relations: list[str | BinaryExpression] = None) -> \
    Sequence[Room]:
        # Haversine formula to calculate distance
        query = (
            select(self.Model)
            .join(Location, self.Model.location_id == Location.id)
            .where(
                func.acos(
                    func.sin(func.radians(lat)) * func.sin(func.radians(Location.lat)) +
                    func.cos(func.radians(lat)) * func.cos(func.radians(Location.lat)) *
                    func.cos(func.radians(Location.lon) - func.radians(lon))
                ) * 6371 <= 400  # Distance in kilometers (10 km radius)
            )
            .limit(20)
        )

        query = self._apply_relationship_loading(query, load_relations)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_url_slug_and_lang(self, slug: str, lang_code: str,
                                       load_relations: list[str | BinaryExpression] = None) -> Room | None:
        # Solution 1
        query = (
            select(self.Model)
            .join(Room.translations)  # Join the RoomTranslation table
            .where(self.Model.url_slug == slug, RoomTranslation.lang == lang_code.lower())
        )

        # Solution 2
        # subquery = (
        #     select(RoomTranslation)
        #     .where(RoomTranslation.lang == lang_code)
        #     .filter(RoomTranslation.room_id == Room.id)
        # )
        #
        # query = (
        #     select(self.Model)
        #     .where(self.Model.url_slug == slug)
        #     .where(exists(subquery))  # Explicit EXISTS check
        # )

        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
