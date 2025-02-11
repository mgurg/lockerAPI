from typing import Annotated

from fastapi import APIRouter, Depends, Header
from pydantic import IPvAnyAddress
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT

from app.schemas.requests import PlaceAdd
from app.schemas.responses import CityDetailsResponse
from app.service.PlaceService import PlaceService
from app.shared.text_utils import sanitize_location_input

place_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
placeServiceDependency = Annotated[PlaceService, Depends()]


@place_router.get("")
async def get_places_with_rooms(place_service: placeServiceDependency, country: CountryAlpha2 | None = None):
    db_item = await place_service.get_places_with_rooms(country)

    return db_item


@place_router.get("/{city_ascii_name}")
async def get_city_details(
    place_service: placeServiceDependency, city_ascii_name: str, language: LanguageAlpha2, country: CountryAlpha2
) -> CityDetailsResponse:
    db_city = await place_service.get_city_details(sanitize_location_input(city_ascii_name), language, country)

    return db_city


@place_router.get("/nearby_city/{city_ascii_name}")
async def get_nearby_cities(
    place_service: placeServiceDependency, city_ascii_name: str
):
    db_city = await place_service.get_nearby_cities(sanitize_location_input(city_ascii_name))

    return db_city


@place_router.get("/rooms/{location_name}")
async def get_rooms_by_location(place_service: placeServiceDependency, location_name: str, language: LanguageAlpha2 | None = None):
    db_item = await place_service.get_rooms_by_location(location_name, language)

    return db_item


@place_router.get("/rooms/geoip")
async def get_rooms_by_geolocation(
    place_service: placeServiceDependency,
    request: Request,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    client_ip_str = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host
    client_ip = IPvAnyAddress(client_ip_str)
    db_item = await place_service.get_rooms_by_ip(client_ip)

    return db_item


@place_router.post("", status_code=HTTP_204_NO_CONTENT)
async def add_room(place_service: placeServiceDependency, place: PlaceAdd):
    await place_service.create_place(place)

    return None
