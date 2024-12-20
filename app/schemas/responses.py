from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StandardResponse(BaseResponse):
    ok: bool


class CompanyIndexResponse(BaseResponse):
    uuid: UUID
    name: str


class RoomTranslation(BaseResponse):
    lang: LanguageAlpha2
    title: str
    lead: str
    description: str


class Location(BaseResponse):
    street_address: str
    city: str
    state_province: str | None = None
    postal_code: str | None = None
    country: CountryAlpha2
    located_in: str | None = None
    lat: float | None = None
    lon: float | None = None


class RoomIndexResponse(BaseResponse):
    uuid: UUID
    url_slug: str
    reservation_url: str
    players_min: int
    players_max: int
    price_from: float
    game_duration: int
    location: Location
    translation: RoomTranslation | None = None


class RoomsPaginated(BaseResponse):
    data: list[RoomIndexResponse]
    count: int
    limit: int
    offset: int


class CompaniesPaginated(BaseResponse):
    data: list[CompanyIndexResponse]
    count: int
    limit: int
    offset: int
