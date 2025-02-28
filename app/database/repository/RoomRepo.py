from math import cos, radians
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic_extra_types.coordinate import Latitude, Longitude
from sqlalchemy import BinaryExpression, Sequence, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import get_db
from app.database.models.models import Location, Room, RoomTranslation
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]

EARTH_RADIUS_KM = 6371  # Earth's radius in kilometers
KM_PER_DEGREE_LAT = 111.32  # Approximate km per degree of latitude


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

    async def get_by_uuid(self, uuid: UUID, load_relations: list[str] | str = None) -> Room | None:
        query = select(self.Model).where(self.Model.uuid == uuid)
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_uuids(self, uuids: list[UUID], load_relations: list[str] | str = None) -> Sequence[Room]:
        query = select(self.Model).where(self.Model.uuid.in_(uuids))
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_count(self) -> int:
        query = select(func.count()).select_from(self.Model).where(self.Model.verified_at.isnot(None))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_by_url_slug(self, slug: str, load_relations: list[str] | str = None) -> Room | None:
        query = select(self.Model).where(self.Model.url_slug == slug)
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_location_and_language(
            self, slug: str, lang_code: str, load_relations: list[str | BinaryExpression] = None
    ) -> Room | None:
        ...

    async def get_by_bbox(
            self,
            min_lon: float,
            max_lon: float,
            min_lat: float,
            max_lat: float,
            load_relations: list[str | BinaryExpression],
            offset: int | None = None,
            limit: int | None = None,
            sort_column: str | None = None,
            sort_order: str | None = None,
    ) -> tuple[Sequence[Room], int]:
        # bbox = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude

        location_subquery = (
            select(Location.id)
            .where((Location.lon >= min_lon) & (Location.lon <= max_lon),
                   (Location.lat >= min_lat) & (Location.lat <= max_lat))
            .subquery()
        )

        # Join the rooms with the locations subquery
        query = (
            select(self.Model).join(location_subquery, self.Model.location_id == location_subquery.c.id)
            .where(self.Model.active.is_(True))
        )

        query = self._apply_relationship_loading(query, load_relations)
        result = await self.session.execute(query.offset(offset).limit(limit))

        total_records: int = 0

        count_statement = select(func.count(self.Model.id))
        count_result = await self.session.execute(count_statement)
        counter = count_result.scalar_one_or_none()
        if counter:
            total_records = counter

        return result.scalars().all(), total_records

    async def get_nearby_rooms(self, lat: Latitude, lon: Longitude, radius_km: int = 10,
                               load_relations: list[str | BinaryExpression] = None):
        # Approximate latitude and longitude bounds
        lat = float(lat)  # Convert lat to float
        lon = float(lon)  # Convert lon to float
        lat_diff = radius_km / KM_PER_DEGREE_LAT
        lon_diff = radius_km / (KM_PER_DEGREE_LAT * cos(radians(lat)))

        min_lat, max_lat = lat - lat_diff, lat + lat_diff  # Now both are floats
        min_lon, max_lon = lon - lon_diff, lon + lon_diff

        # Bounding Box SQL filter
        query = (
            select(self.Model)
            .join(Location, self.Model.location_id == Location.id)
            .where(Location.lat.between(min_lat, max_lat))
            .where(Location.lon.between(min_lon, max_lon))
            .where(
                func.acos(
                    func.sin(func.radians(lat)) * func.sin(func.radians(Location.lat))
                    + func.cos(func.radians(lat))
                    * func.cos(func.radians(Location.lat))
                    * func.cos(func.radians(Location.lon) - func.radians(lon))
                )
                * EARTH_RADIUS_KM
                <= radius_km  # Final precise distance filter
            )
            .limit(20)
        )

        query = self._apply_relationship_loading(query, load_relations)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_url_slug_and_lang(self, slug: str, lang_code: str,
                                       load_relations: list[str | BinaryExpression] = None) -> Room | None:

        # stmt = (
        #     select(Room)
        #     .join(RoomTranslation, Room.id == RoomTranslation.room_id)
        #     .filter(Room.url_slug == slug, RoomTranslation.lang == lang_code)
        #     .options(joinedload(Room.translations))  # Load translations
        # )
        # result = await self.session.execute(stmt)
        # return result.scalar_one_or_none()
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

    async def get_number_of_rooms(self) -> int:
        query = select(func.count()).select_from(self.Model)
        result = await self.session.execute(query)
        return result.scalar()
