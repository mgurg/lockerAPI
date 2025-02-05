from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.status import HTTP_204_NO_CONTENT

from app.schemas.requests import CompanyAdd, DepartmentAdd, DepartmentEdit
from app.schemas.responses import BaseUuid, CompaniesPaginated
from app.service.CompanyService import CompanyService

company_router = APIRouter()

companyServiceDependency = Annotated[CompanyService, Depends()]


@company_router.get("")
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


@company_router.post("")
async def add_company(company_service: companyServiceDependency, company: CompanyAdd) -> BaseUuid:
    db_company = await company_service.create_company(company)
    return BaseUuid(uuid=db_company.uuid)


@company_router.get("/{company_uuid}/departments")
async def get_company_departments(company_service: companyServiceDependency, company_uuid: UUID):
    db_department = await company_service.get_comapny_departments(company_uuid)
    return db_department


@company_router.get("/departments/{department_uuid}")
async def get_department(company_service: companyServiceDependency, department_uuid: UUID):
    db_department = await company_service.get_department(department_uuid)
    return db_department


@company_router.post("/departments")
async def create_department(company_service: companyServiceDependency, department: DepartmentAdd) -> BaseUuid:
    db_department = await company_service.create_department(department)
    return BaseUuid(uuid=db_department.uuid)


@company_router.patch("/departments/{department_uuid}")
async def update_department(company_service: companyServiceDependency, department_uuid: UUID, department: DepartmentEdit) -> None:
    db_department = await company_service.update_department(department_uuid, department)
    return None


@company_router.delete("/departments/{department_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_department(company_service: companyServiceDependency, department_uuid: UUID):
    db_department = await company_service.delete_department(department_uuid)
    return None
