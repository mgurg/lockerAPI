from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import BinaryExpression, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import get_db
from app.database.models.models import Company
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class CompanyRepo(GenericRepo[Company]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Company
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

    async def get_by_uuid(self, uuid: UUID, load_relations: list[str] | str = None) -> Company | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_companies(
            self,
            offset: int,
            limit: int,
            sort_column: str,
            sort_order: str,
            search: str | None = None,
            load_relations: list[str] | str = None
    ) -> tuple[Sequence[Company], int]:
        query = (
            select(self.Model)
            .order_by(text(f"{sort_column} {sort_order}"))
        )
        query = self._apply_relationship_loading(query, load_relations)

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

    async def get_by_gov_id(self, gov_id: str) -> Company | None:
        query = select(self.Model).where(self.Model.gov_id == gov_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def gef_first_unverified(self, load_relations: list[str] | str = None) -> Company:
        query = (
            select(self.Model).where(self.Model.verified_at.is_(None))
        )
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_company_location(self, company_id: int):
        return None

    async def get_company_related_locations(
        self,
        company_uuid: UUID,
        entity_type: str | None = None,
        city: str | None = None,
        country: str | None = None
    ):
        ...
