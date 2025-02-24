from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import get_db
from app.database.models.models import Company, Contact
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class ContactRepo(GenericRepo[Contact]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Contact
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

    async def get_by_uuid(self, uuid: UUID) -> Contact | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_company_id(self, company_id: int, load_relations: list[str] | str = None) -> Sequence[Company]:
        query = select(self.Model).where(self.Model.company_id == company_id)
        query = self._apply_relationship_loading(query, load_relations)

        result = await self.session.execute(query)
        return result.scalars().all()
