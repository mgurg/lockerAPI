from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2


class LocationAdd(BaseModel):
    street_address: str
    city: str
    state_province: str | None = None
    postal_code: str | None = None
    country: CountryAlpha2
    lat: float | None = None
    lng: float | None = None


class TranslationAdd(BaseModel):
    lang: LanguageAlpha2
    title: str
    lead: str | None = None
    description: str | None = None


class RoomAdd(BaseModel):
    name: str
    # city_id: int
    price_from: float | None = None
    game_duration: int | None = None
    players_min: int | None = None
    players_max: int | None = None
    reservation_url: str | None = None
    lm_id: str | None = None
    mt_id: str | None = None
    location: LocationAdd
    translation: TranslationAdd


class GeoNameAdd(BaseModel):
    name: str
    lang: str


class PlaceAdd(BaseModel):
    lat: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]
    lng: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]
    lat_min: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # South Latitude
    lat_max: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # North Latitude
    lng_min: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # West Longitude
    lng_max: Annotated[Decimal | None, Field(max_digits=10, decimal_places=7)]  # East Longitude
    population: int | None
    importance: float | None
    category: str
    region: str | None
    country: CountryAlpha2 | None
    geo_names: list[GeoNameAdd]
