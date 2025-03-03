from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2

from app.database.models.enums import ContactType, FearLevel, GameDifficulty


class LocationAdd(BaseModel):
    street_name: str | None = None
    street_number: str | None = None
    city: str
    state_province: str | None = None
    postal_code: str | None = None
    country: CountryAlpha2
    located_in: str | None = None
    lat: Latitude | None = None
    lon: Longitude | None = None


class LocationEdit(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    uuid: UUID | None = None
    street_name: str | None = None
    street_number: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: CountryAlpha2
    located_in: str | None = None
    lat: Latitude | None = None
    lon: Longitude | None = None


class TranslationAdd(BaseModel):
    lang: LanguageAlpha2
    title: str
    lead: str | None = None
    description: str | None = None


class RoomAdd(BaseModel):
    name: str
    company_uuid: UUID
    department_uuid: UUID | None = None
    price_from: float | None = None
    duration: int | None = None
    players_min: int | None = None
    players_max: int | None = None
    booking_url: str | None = None
    difficulty:  GameDifficulty | None = None
    category:  str | None = None
    fear_level:  FearLevel | None = None
    url_yt:  str | None = None
    lm_id: str | None = None
    mt_id: str | None = None
    translation: list[TranslationAdd]
    supported_languages: list[LanguageAlpha2]


class RoomEdit(BaseModel):
    name: str | None
    department_uuid: UUID | None = None
    price_from: float | None = None
    game_duration: int | None = None
    players_min: int | None = None
    players_max: int | None = None
    booking_url: str | None = None
    lm_id: str | None = None
    mt_id: str | None = None
    translation: list[TranslationAdd] | None = None
    supported_languages: list[LanguageAlpha2] | None = None


class GeoNameAdd(BaseModel):
    name: str
    lang: str


class PlaceAdd(BaseModel):
    name: str
    lat: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]
    lon: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]
    lat_min: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # South Latitude
    lat_max: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # North Latitude
    lon_min: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # West Longitude
    lon_max: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # East Longitude
    population: int | None
    importance: float | None
    category: str
    region: str | None
    country: CountryAlpha2 | None
    language: LanguageAlpha2 | None
    geo_names: list[GeoNameAdd]


class CompanyAdd(BaseModel):
    name: str
    brand: str | None = None
    gov_id: str
    gov_id_type: str | None = "NIP"
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    location: LocationAdd


class CompanyEdit(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    brand: str | None = None
    gov_id: str | None = None
    gov_id_type: str | None = None
    place_id: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    verified_at: str | None = None
    location: LocationEdit | None = None


class DepartmentAdd(BaseModel):
    company_uuid: UUID
    name: str
    location: LocationAdd | None = None


class DepartmentEdit(BaseModel):
    name: str | None = None
    location: LocationEdit | None = None


class ContactAdd(BaseModel):
    company_uuid: UUID
    department_uuid: UUID | None = None
    type:  ContactType
    value: str
    country_code: str | None = None
    is_primary: bool = False
    description: str | None = None


class TagAdd(BaseModel):
    room_uuid: UUID
    name: str
