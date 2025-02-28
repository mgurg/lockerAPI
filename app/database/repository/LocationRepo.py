from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic_extra_types.country import CountryAlpha2
from sqlalchemy import BinaryExpression, Sequence, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.database.models.models import Location, Room
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class LocationRepo(GenericRepo[Location]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Location
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> Location | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_places_with_rooms(self, country: CountryAlpha2, cut_off: int = 0) -> Sequence[Location]:
        query = (
            select(Location.city, Location.state_province, func.count(Room.id).label("room_count"))
            .join(Room, Room.location_id == Location.id)
            .where(Location.country == country)
            .where(Room.active.is_(True))
            .group_by(Location.city, Location.state_province)
            .having(func.count(Room.id) > cut_off)
            .order_by(func.count(Room.id).desc())
        )

        result = await self.session.execute(query)
        return result.all()

    async def get_by_bbox(self, min_lon: float, max_lon: float, min_lat: float, max_lat: float,
                          load_relations: list[str | BinaryExpression] = None) -> Sequence[Location]:
        # bbox = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude

        query = (
            select(self.Model)
            .where(
                (self.Model.lon >= min_lon) & (self.Model.lon <= max_lon),
                (self.Model.lat >= min_lat) & (self.Model.lat <= max_lat)
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()
