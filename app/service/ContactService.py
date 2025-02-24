from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.config import get_settings
from app.database.repository.CompanyRepo import CompanyRepo
from app.database.repository.ContactRepo import ContactRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.schemas.requests import ContactAdd

settings = get_settings()


class ContactService:
    def __init__(
            self,
            company_repo: Annotated[CompanyRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            contact_repo: Annotated[ContactRepo, Depends()],
    ) -> None:
        self.company_repo = company_repo
        self.department_repo = department_repo
        self.contact_repo = contact_repo

    async def create_contact(self, contact: ContactAdd):
        db_company = await self.company_repo.get_by_uuid(contact.company_uuid)
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{contact.company_uuid}` not found!")

        contact_data = {
                "uuid": str(uuid4()),
                # "company_id": db_company.id,
                "company": db_company,
                "type": contact.type,
                "value": contact.value,
                "country_code": contact.country_code,
                "description": contact.description,
            }

        if contact.department_uuid:
            db_departments = await self.department_repo.get_by_uuids([contact.department_uuid])
            if not db_departments:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                    detail=f"Department `{contact.department_uuid}` not found!")
            contact_data["departments"] = db_departments

        new_contact = await self.contact_repo.create(**contact_data)

        return new_contact

    async def get_company_contacts(self, company_uuid: UUID):
        db_company = await self.company_repo.get_by_uuid(company_uuid)
        if not db_company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Company `{company_uuid}` not found!")
        db_contacts = await self.contact_repo.get_by_company_id(db_company.id, ["departments"])

        return db_contacts
