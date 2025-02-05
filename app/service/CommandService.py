from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.database.repository.CompanyRepo import CompanyRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.database.repository.LocationRepo import LocationRepo

settings = get_settings()


class CommandService:
    def __init__(
            self,
            company_repo: Annotated[CompanyRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
    ) -> None:
        self.company_repo = company_repo
        self.department_repo = department_repo
        self.location_repo = location_repo

    async def get_first_unverified_company(self):
        db_company = await self.company_repo.gef_first_unverified(["location", "departments", "rooms"])
        return db_company
