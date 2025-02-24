from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.schemas.requests import CompanyAdd, CompanyEdit, DepartmentAdd, DepartmentEdit, ContactAdd
from app.schemas.responses import BaseUuid, CompaniesPaginated
from app.service.CompanyService import CompanyService
from app.service.ContactService import ContactService

company_router = APIRouter()

companyServiceDependency = Annotated[CompanyService, Depends()]
contactServiceDependency = Annotated[ContactService, Depends()]


@company_router.get("", status_code=HTTP_200_OK)
async def get_companies(
        company_service: companyServiceDependency,
        search: Annotated[str | None, Query(max_length=50)] = None,
        limit: int = 10,
        offset: int = 0,
        field: Literal["name", "created_at"] = "name",
        order: Literal["asc", "desc"] = "asc",
) -> CompaniesPaginated:
    db_companies, count = await company_service.get_all(offset, limit, field, order, search)
    return CompaniesPaginated(data=db_companies, count=count, offset=offset, limit=limit)


@company_router.get("/{company_uuid}", status_code=HTTP_200_OK)
async def get_company_by_uuid(company_service: companyServiceDependency, company_uuid: UUID):
    db_company = await company_service.get_one(company_uuid)
    return db_company


@company_router.post("", status_code=HTTP_201_CREATED)
async def create_company(company_service: companyServiceDependency, company: CompanyAdd) -> BaseUuid:
    db_company = await company_service.create_company(company)
    return BaseUuid(uuid=db_company.uuid)


@company_router.patch("/{company_uuid}", status_code=HTTP_204_NO_CONTENT)
async def update_company(company_service: companyServiceDependency, company_uuid: UUID, company: CompanyEdit) -> None:
    await company_service.update_company(company_uuid, company)
    return None


@company_router.delete("/{company_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_company(company_service: companyServiceDependency, company_uuid: UUID) -> None:
    await company_service.delete_company(company_uuid)
    return None


@company_router.get("/{company_uuid}/departments")
async def get_company_departments(company_service: companyServiceDependency, company_uuid: UUID):
    db_department = await company_service.get_company_departments(company_uuid)
    return db_department


@company_router.get("/{company_uuid}/locations")
async def get_company_locations(company_service: companyServiceDependency, company_uuid: UUID):
    db_locations = await company_service.get_company_locations(company_uuid)
    return db_locations


@company_router.get("/departments/{department_uuid}")
async def get_department(company_service: companyServiceDependency, department_uuid: UUID):
    db_department = await company_service.get_department(department_uuid)
    return db_department


@company_router.post("/departments")
async def create_department(company_service: companyServiceDependency, department: DepartmentAdd) -> BaseUuid:
    db_department = await company_service.create_department(department)
    return BaseUuid(uuid=db_department.uuid)


@company_router.patch("/departments/{department_uuid}", status_code=HTTP_204_NO_CONTENT)
async def update_department(company_service: companyServiceDependency, department_uuid: UUID,
                            department: DepartmentEdit) -> None:
    await company_service.update_department(department_uuid, department)
    return None


@company_router.delete("/departments/{department_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_department(company_service: companyServiceDependency, department_uuid: UUID) -> None:
    await company_service.delete_department(department_uuid)
    return None


@company_router.get("/{company_uuid}/contacts")
async def get_company_contacts(contact_service: contactServiceDependency, company_uuid: UUID):
    db_locations = await contact_service.get_company_contacts(company_uuid)
    return db_locations

@company_router.post("/contacts")
async def create_contact(contact_service: contactServiceDependency, contact: ContactAdd) -> BaseUuid:
    db_department = await contact_service.create_contact(contact)
    return BaseUuid(uuid=db_department.uuid)