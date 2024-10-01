from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from starlette.status import HTTP_204_NO_CONTENT

from app.schemas.requests import PlaceAdd
from app.service.PlaceService import PlaceService

place_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
placeServiceDependency = Annotated[PlaceService, Depends()]


@place_router.get("/{location_name}")
async def place_by_uuid(place_service: placeServiceDependency, location_name: str,
                        language: LanguageAlpha2 | None = None):
    db_item = await place_service.get_rooms_by_location(location_name, language)

    return db_item


@place_router.get("")
async def places_with_rooms(place_service: placeServiceDependency, country: CountryAlpha2 | None = None):
    db_item = await place_service.get_places_with_rooms(country)

    return db_item


@place_router.post("", status_code=HTTP_204_NO_CONTENT)
async def add_room(place_service: placeServiceDependency, place: PlaceAdd):
    await place_service.create_place(place)

    return None
