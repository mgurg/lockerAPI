from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy import Sequence
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.config import get_settings
from app.database.models.models import Company
from app.database.repository.CompanyRepo import CompanyRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.database.repository.LocationRepo import LocationRepo
from app.schemas.requests import CompanyAdd, CompanyEdit, DepartmentAdd, DepartmentEdit

settings = get_settings()


class CompanyService:
    def __init__(
            self,
            company_repo: Annotated[CompanyRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
    ) -> None:
        self.company_repo = company_repo
        self.department_repo = department_repo
        self.location_repo = location_repo

    async def get_all(self,
                      offset: int,
                      limit: int,
                      sort_column: str,
                      sort_order: str,
                      search: str | None = None
                      ) -> tuple[Sequence[Company], int]:

        db_companies, count = await self.company_repo.get_companies(offset, limit, sort_column, sort_order, search,
                                                                    ["location", "departments", "rooms"])
        return db_companies, count

    async def get_one(self, company_uuid: UUID):
        db_company = await self.company_repo.get_by_uuid(company_uuid, ["location", "departments", "rooms"])
        if not db_company:
            raise HTTPException(status_code=HTTP_409_CONFLICT,
                                detail=f"Company`{company_uuid}` not found")
        return db_company

    async def create_company(self, company: CompanyAdd):
        db_company = await self.company_repo.get_by_gov_id(company.gov_id)
        if db_company:
            raise HTTPException(status_code=HTTP_409_CONFLICT,
                                detail=f"Company with {company.gov_id_type} `{company.gov_id}` already exists")

        location_data = {
            "uuid": str(uuid4()),
            "street_name": company.location.street_name,
            "street_number": company.location.street_number,
            "city": company.location.city,
            "state_province": company.location.state_province,
            "postal_code": company.location.postal_code,
            "country": company.location.country,
            "type": "city",
            "located_in": company.location.located_in,
            "lat": company.location.lat,
            "lon": company.location.lon,
        }
        db_location = await self.location_repo.create(**location_data)

        company_data = {
            "uuid": str(uuid4()),
            "name": company.name,
            "brand": company.brand or company.name,
            "location_id": db_location.id,
            # "place_id": company.place_id,
            "gov_id": company.gov_id,
            "gov_id_type": company.gov_id_type,
            "website": company.website,
            "phone": company.phone,
            "verified_at": None,
            "created_at": datetime.now(UTC),
        }

        new_db_company = await self.company_repo.create(**company_data)

        return new_db_company

    async def update_company(self, company_uuid: UUID, company: CompanyEdit):
        db_company = await self.company_repo.get_by_uuid(company_uuid, ["location"])
        if not db_company:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Company with `{company_uuid}` not found"
            )

        update_data = company.model_dump(exclude_unset=True)

        if "location" in update_data and update_data["location"] is not None:
            location_data = update_data.pop("location")  # Extract location data
            if db_company.location:  # If company already has a location
                for key, value in location_data.items():
                    setattr(db_company.location, key, value)

        # Update the company with remaining data
        await self.company_repo.update(db_company.id, **update_data)

        # Return updated company
        # return await self.company_repo.get_by_uuid(company_uuid, ["location"])
        return None

    async def delete_company(self, company_uuid: UUID):
        db_company = await self.company_repo.get_by_uuid(company_uuid, ["location", "departments"])
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{company_uuid}` not found!")

        # Finally delete the company
        await self.company_repo.delete(db_company.id)

        # Get all department IDs for deletion
        department_ids = [dept.id for dept in db_company.departments]

        # Delete all departments associated with this company
        for dept_id in department_ids:
            await self.department_repo.delete(dept_id)

        # Check if this location is only used by this company
        location = db_company.location
        if location:
            # Location is only associated with this company, so delete it
            await self.location_repo.delete(location.id)

        return {"message": f"Company {company_uuid} and all associated data deleted successfully"}

    async def create_department(self, department: DepartmentAdd):
        db_company = await self.company_repo.get_by_uuid(department.company_uuid, ["departments"])
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{department.company_uuid}` not found!")

        departments_names = [department.name for department in db_company.departments]
        if department.name in departments_names:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail=f"Name `{department.name}` already in use for company `{department.company_uuid}`")

        department_data = {
                "uuid": str(uuid4()),
                "name": department.name,
                "company": db_company,
            }

        if department.location:
            location_data = department.location.model_dump(exclude_unset=True)
            location_data["uuid"] = str(uuid4())
            location_data["type"] = "department"
            new_location = await self.location_repo.create(**location_data)
            department_data["location"] = new_location

            # Create the new department
        new_department = await self.department_repo.create(**department_data)

        return new_department

    async def delete_department(self, department_uuid: UUID):
        db_department = await self.department_repo.get_by_uuid(department_uuid, ["location"])
        if not db_department:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{department_uuid}` not found!")

        # Delete the department
        await self.department_repo.delete(db_department.id)

        if db_department.location:
            await self.location_repo.delete(db_department.location.id)

        logger.info(f"Department `{department_uuid}` and its related location have been deleted.")

        return None

    async def update_department(self, department_uuid: UUID, department_data: DepartmentEdit):
        db_department = await self.department_repo.get_by_uuid(department_uuid, ["location"])
        if not db_department:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Department with UUID {department_uuid} not found"
            )

        update_data = department_data.model_dump(exclude_unset=True)

        # Handle location updates separately
        if "location" in update_data and update_data["location"] is not None:
            location_data = update_data.pop("location")  # Extract location data
            if db_department.location:  # If the department already has a location
                for key, value in location_data.items():
                    setattr(db_department.location, key, value)  # Update existing location object

        await self.department_repo.update(db_department.id, **update_data)

    async def get_department(self, department_uuid: UUID):
        db_department = await self.department_repo.get_by_uuid(department_uuid, ["location", "contacts"])
        if not db_department:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Department `{department_uuid}` not found!")

        return db_department

    async def get_company_departments(self, company_uuid: UUID):
        db_company = await self.company_repo.get_by_uuid(company_uuid, ["departments"])
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Department `{company_uuid}` not found!")

        departments_uuids = [department.uuid for department in db_company.departments]

        db_departments = await self.department_repo.get_by_uuids(departments_uuids, ["location"])

        return db_departments
