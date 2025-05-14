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
from app.database.repository.ContactRepo import ContactRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.database.repository.LocationRepo import LocationRepo
from app.database.repository.RoomRepo import RoomRepo
from app.database.repository.RoomTranslationRepo import RoomTranslationRepo
from app.schemas.requests import CompanyAdd, CompanyEdit, DepartmentAdd, DepartmentEdit

settings = get_settings()


class CompanyService:
    def __init__(
            self,
            company_repo: Annotated[CompanyRepo, Depends()],
            contact_repo: Annotated[ContactRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            room_repo: Annotated[RoomRepo, Depends()],
            room_translation_repo: Annotated[RoomTranslationRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
    ) -> None:
        self.company_repo = company_repo
        self.contact_repo = contact_repo
        self.department_repo = department_repo
        self.room_repo = room_repo
        self.room_translation_repo = room_translation_repo
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
            "type": "company",
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
        # Fetch company with related departments and location
        db_company = await self.company_repo.get_by_uuid(company_uuid, ["location", "departments"])
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{company_uuid}` not found!")

        for dept in db_company.departments:
            # 1. Delete rooms linked to the department
            dept_rooms = await self.room_repo.get_by_department_id(dept.id)
            for room in dept_rooms:
                # First delete room translations
                await self.room_translation_repo.delete_by_room_id(room.id)

                # Get room with languages loaded to properly clear M2M relationships
                room_with_languages = await self.room_repo.get_by_id(room.id, ["languages"])
                if room_with_languages and room_with_languages.languages:
                    logger.info(f"Clearing language associations for room: {room.name}")
                    room_with_languages.languages = []

                logger.info(f"Removing room: {room.name}")
                await self.room_repo.delete(room.id)

            # 2. Store department location_id before deleting the department
            dept_location_id = dept.location_id

            # 3. Delete the department itself
            logger.info(f"Removing department: {dept.name}")
            await self.department_repo.delete(dept.id)

            # 4. Now delete the department location
            if dept_location_id:
                logger.info(f"Removing department location for department: {dept.name}")
                await self.location_repo.delete(dept_location_id)

        # Finally delete the company
        logger.info(f"Removing company: {db_company.name}")
        await self.company_repo.delete(db_company.id)

        # Delete location if no other companies are using it
        location = db_company.location
        if location:
            other_companies_using_location = await self.company_repo.count_by_location_id(location.id)
            if other_companies_using_location == 0:
                logger.info(f"Removing company location for company: {db_company.name}")
                await self.location_repo.delete(location.id)

        return {"message": f"Company {company_uuid} and all associated data deleted successfully"}

    async def create_department(self, department: DepartmentAdd):
        db_company = await self.company_repo.get_by_uuid(department.company_uuid, ["departments", "location"])
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

        if department.location is not None:
            location_data = department.location.model_dump(exclude_unset=True)
            location_data["uuid"] = str(uuid4())
            location_data["type"] = "department"
            new_location = await self.location_repo.create(**location_data)
            department_data["location"] = new_location
        else:
            location_data = {
                "uuid": str(uuid4()),
                "street_name": db_company.location.street_name,
                "street_number": db_company.location.street_number,
                "city": db_company.location.city,
                "state_province": db_company.location.state_province,
                "postal_code": db_company.location.postal_code,
                "country": db_company.location.country,
                "type": "department",
                "located_in": db_company.location.located_in,
                "lat": db_company.location.lat,
                "lon": db_company.location.lon,
            }
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