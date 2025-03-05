from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2

from app.database.models.enums import GameDifficulty, FearLevel


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StandardResponse(BaseResponse):
    ok: bool


class Location(BaseResponse):
    street_name: str | None
    street_number: str | None
    city: str
    state_province: str | None = None
    postal_code: str | None = None
    country: CountryAlpha2
    located_in: str | None = None
    lat: float | None = None
    lon: float | None = None


class BasicLocation(BaseResponse):
    city: str | None


class BasicDepartment(BaseResponse):
    uuid: UUID
    name: str


class BasicRoom(BaseResponse):
    uuid: UUID
    name: str


class CompanyIndexResponse(BaseResponse):
    uuid: UUID
    name: str
    verified_at: datetime | None
    location: BasicLocation | None
    departments: list[BasicDepartment] | None
    rooms: list[BasicRoom] | None


class RoomTranslation(BaseResponse):
    lang: LanguageAlpha2
    title: str
    lead: str
    description: str


class RoomIndexResponse(BaseResponse):
    uuid: UUID
    url_slug: str
    booking_url: str | None
    players_min: int | None
    players_max: int | None
    price_from: float | None
    duration: int | None
    difficulty:  GameDifficulty | None = None
    category:  str | None = None
    fear_level:  FearLevel | None = None
    url_yt:  str | None = None
    location: Location
    translation: RoomTranslation | None = None
    department: BasicDepartment | None = None


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


class CityDetailsResponse(BaseResponse):
    city_name: str
    city_name_inflect: str
    lat: float
    lon: float
    lat_min: float
    lon_min: float
    lat_max: float
    lon_max: float
    population: int
    importance: float
    category: str | None = None
    region: str | None = None
    country: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None


class BaseUuid(BaseResponse):
    uuid: UUID

class PlaceRoomIndexResponse(BaseResponse):
    uuid: UUID
    url_slug: str
    players_min: int | None
    players_max: int | None
    price_from: float | None
    duration: int | None
    translation: RoomTranslation | None = None