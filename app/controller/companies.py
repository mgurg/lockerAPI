from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.schemas.requests import CompanyAdd, DepartmentAdd
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


@company_router.post("/department")
async def add_company_department(company_service: companyServiceDependency, department: DepartmentAdd) -> BaseUuid:
    db_department = await company_service.create_department(department)
    return BaseUuid(uuid=db_department.uuid)
