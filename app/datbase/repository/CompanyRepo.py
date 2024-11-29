from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Sequence, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.datbase.db import get_db
from app.datbase.models.models import Company
from app.datbase.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class CompanyRepo(GenericRepo[Company]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Company
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> Company | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_companies(
        self, offset: int, limit: int, sort_column: str, sort_order: str, search: str | None = None
    ) -> tuple[Sequence[Company], int]:
        query = (
            select(self.Model)
            .order_by(text(f"{sort_column} {sort_order}"))
        )

        search_filters = []
        if search is not None:
            search_filters.append(self.Model.name.ilike(f"%{search}%"))
            query = query.filter(*search_filters)

        result = await self.session.execute(query.offset(offset).limit(limit))

        total_records: int = 0

        count_statement = (
            select(func.count(self.Model.id))
        )
        count_result = await self.session.execute(count_statement)
        counter = count_result.scalar_one_or_none()
        if counter:
            total_records = counter

        return result.scalars().all(), total_records
