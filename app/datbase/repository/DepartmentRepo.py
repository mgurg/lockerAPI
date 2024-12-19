from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.datbase.db import get_db
from app.datbase.models.models import Department
from app.datbase.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class DepartmentRepo(GenericRepo[Department]):
    def __init__(self, session: UserDB) -> None:
        self.Model = Department
        super().__init__(session, self.Model)

    async def get_by_uuid(self, uuid: UUID) -> Department | None:
        query = select(self.Model).where(self.Model.uuid == str(uuid))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
