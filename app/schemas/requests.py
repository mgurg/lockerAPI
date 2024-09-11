from pydantic import BaseModel
from pydantic_extra_types.country import CountryAlpha2


class LocationAdd(BaseModel):
    street_address: str
    city: str
    state_province: str | None = None
    postal_code: str | None = None
    country: str
    lat: float | None = None
    lng: float | None = None


class TranslationAdd(BaseModel):
    lang: CountryAlpha2
    title: str
    lead: str | None = None
    description: str | None = None


class RoomAdd(BaseModel):
    name: str
    url_slug: str | None = None
    city_id: int
    location: LocationAdd
    translation: TranslationAdd
