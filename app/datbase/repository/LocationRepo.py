from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from app.datbase.db import get_db
from app.datbase.models.models import Location
from app.datbase.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class LocationRepo(GenericRepo[Location]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Location
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> Location | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_bbox(self, min_lng: float, max_lng: float, min_lat: float, max_lat: float,
                          load_relations: list[str | BinaryExpression] = None) -> Sequence[Location]:
        # bbox = left,bottom,right,top
        # bbox = min Longitude , min Latitude , max Longitude , max Latitude

        query = (
            select(self.Model)
            .where(
                (self.Model.lng >= min_lng) & (self.Model.lng <= max_lng),
                (self.Model.lat >= min_lat) & (self.Model.lat <= max_lat)
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()
