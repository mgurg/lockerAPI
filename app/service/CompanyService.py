from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException
from sqlalchemy import Sequence
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.config import get_settings
from app.datbase.models.models import Company
from app.datbase.repository.CompanyRepo import CompanyRepo
from app.datbase.repository.LocationRepo import LocationRepo
from app.schemas.requests import CompanyAdd, DepartmentAdd

settings = get_settings()


class CompanyService:
    def __init__(
            self,
            company_repo: Annotated[CompanyRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
    ) -> None:
        self.company_repo = company_repo
        self.location_repo = location_repo

    async def get_all(self,
                      offset: int,
                      limit: int,
                      sort_column: str,
                      sort_order: str,
                      search: str | None = None
                      ) -> tuple[Sequence[Company], int]:

        db_companies, count = await self.company_repo.get_companies(offset, limit, sort_column, sort_order, search)
        return db_companies, count

    async def create_company(self, company: CompanyAdd):
        location_data = {
            "street_address": company.location.street_address,
            "city": company.location.city,
            "state_province": company.location.state_province,
            "postal_code": company.location.postal_code,
            "country": company.location.country,
            "located_in": company.location.located_in,
            "type": "room",
            "lat": company.location.lat,
            "lon": company.location.lon,
        }
        db_location = await self.location_repo.create(**location_data)

        company_data = {
            "uuid": str(uuid4()),
            "name": company.name,
            "brand": company.name,
            "location_id": db_location.id,
            "place_id": company.place_id,
            "gov_id": company.gov_id,
            "gov_id_type": company.gov_id_type,
            "website": company.website,
            "phone": company.phone,
            "verified_at": None
        }

        try:
            new_db_room = await self.company_repo.create(**company_data)
        except IntegrityError as e:
            raise HTTPException(status_code=HTTP_409_CONFLICT,
                                detail=f"Company with {company.gov_id_type} `{company.gov_id}` already exists") from e

        return new_db_room

    async def create_department(self, department: DepartmentAdd):
        db_company = await self.company_repo.get_by_uuid(department.company_uuid)
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{department.company_uuid}` not found!")
        location_data = {
            "street_address": department.location.street_address,
            "city": department.location.city,
            "state_province": department.location.state_province,
            "postal_code": department.location.postal_code,
            "country": department.location.country,
            "located_in": department.location.located_in,
            "type": "department",
            "lat": department.location.lat,
            "lon": department.location.lon,
        }
        db_location = await self.location_repo.create(**location_data)

        department_data = {
            "name": department.name,
            "company": db_company,
            "location": db_location,
        }
        new_db_department = await self.location_repo.create(**department_data)
        return new_db_department
