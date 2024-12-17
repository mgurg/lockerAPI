from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StandardResponse(BaseResponse):
    ok: bool


class CompanyIndexResponse(BaseResponse):
    uuid: UUID
    name: str


class CompaniesPaginated(BaseResponse):
    data: list[CompanyIndexResponse]
    count: int
    limit: int
    offset: int
