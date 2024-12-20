import re
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from loguru import logger
from pydantic_extra_types.country import CountryAlpha2
from sqlalchemy import BinaryExpression
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from unidecode import unidecode

from app.datbase.models.models import Room
from app.datbase.repository.CityRepo import CityRepo
from app.datbase.repository.CompanyRepo import CompanyRepo
from app.datbase.repository.DepartmentRepo import DepartmentRepo
from app.datbase.repository.LocationRepo import LocationRepo
from app.datbase.repository.RoomRepo import RoomRepo
from app.datbase.repository.RoomTranslationRepo import RoomTranslationRepo
from app.schemas.requests import RoomAdd


class RoomService:
    def __init__(
            self,
            room_repo: Annotated[RoomRepo, Depends()],
            city_repo: Annotated[CityRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
            company_repo: Annotated[CompanyRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            room_translation_repo: Annotated[RoomTranslationRepo, Depends()]
    ) -> None:
        self.room_repo = room_repo
        self.city_repo = city_repo
        self.location_repo = location_repo
        self.company_repo = company_repo
        self.department_repo = department_repo
        self.room_translation_repo = room_translation_repo

    async def get_room_by_uuid(self, room_uuid: UUID) -> Room | None:
        db_item = await self.room_repo.get_by_uuid(room_uuid)

        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_uuid}` not found!")

        return db_item

    async def get_room_by_url_slug(self, room_url_slug: str,
                                   load_relations: list[str | BinaryExpression] = None) -> Room | None:
        db_item = await self.room_repo.get_by_url_slug(room_url_slug, load_relations)

        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_url_slug}` not found!")

        return db_item

    async def get_room_by_url_slug_and_language(self, room_url_slug, lang_code: CountryAlpha2,
                                                load_relations: list[str | BinaryExpression] = None):
        db_item = await self.room_repo.get_by_url_slug_and_lang(room_url_slug, lang_code, load_relations)
        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_url_slug}` not found!")

        # Fetch the specific translation for the given language
        translation = next((t for t in db_item.translations if t.lang == lang_code.lower()), None)
        db_item.translation = translation if translation else None

        return db_item

    async def get_rooms_by_location_and_language(self, location: str, language: str,
                                                 load_relations: list[str | BinaryExpression],
                                                 offset: int,
                                                 limit: int,
                                                 sort_column: str,
                                                 sort_order: str):
        url_safe_place = RoomService.sanitize_input(location)
        city = await self.city_repo.get_place_by_name(url_safe_place)
        if city is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Place `{location}` as: `{url_safe_place}` not found!"
            )

        rooms, count = await self.room_repo.get_by_bbox(
            city.lon_min,
            city.lon_max,
            city.lat_min,
            city.lat_max,
            load_relations,
            offset, limit, sort_column, sort_order
        )

        lang_code = language
        for room in rooms:
            translation = next((t for t in room.translations if t.lang == lang_code.lower()), None)
            room.translation = translation if translation else None
        return rooms, count

    async def room_exists_by_url_slug(self, room_url_slug: str) -> bool:
        db_item = await self.room_repo.get_by_url_slug(room_url_slug)
        return db_item is not None

    async def create_room(self, room: RoomAdd) -> Room | None:
        db_company = await self.company_repo.get_by_uuid(room.company_uuid, ["location"])
        if not db_company:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Company `{room.company_uuid}` not found!")
        location = db_company.location

        db_department = await self.department_repo.get_by_uuid(room.department_uuid, ["location"])
        if not db_department:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail=f"Department `{room.department_uuid}` not found!")
        location = db_department.location

        location_data = {
            "street_address": room.location.street_address if room.location else location.street_address,
            "city": room.location.city if room.location else location.city,
            "state_province": room.location.state_province if room.location else location.state_province,
            "postal_code": room.location.postal_code if room.location else location.postal_code,
            "country": room.location.country if room.location else location.country,
            "lat": room.location.lat if room.location else location.lat,
            "lon": room.location.lon if room.location else location.lon,
            "type": "room"
        }

        db_location = await self.location_repo.create(**location_data)

        translation = ""
        if db_location.lat and db_location.lon:
            db_cities = await self.city_repo.get_places_by_bbox(db_location.lat, db_location.lon,
                                                                ["geo_names"])
            for city in db_cities:
                translation = next((t for t in city.geo_names if t.lang == "pl"), None)
                logger.info(f"Matching `{room.name}` with {city.id} as {translation.name}")
        else:
            logger.warning(
                f"No lat/long data for `{room.name}`: {location_data["street_address"]}, {location_data["city"]}")
        try:
            unique_slug = await self.generate_unique_slug(room.name, translation.name)

        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e

        room_data = {
            "uuid": str(uuid4()),
            "url_slug": unique_slug,
            "name": room.name,
            "active": True,
            "location": db_location,
            "price_from": room.price_from,
            "game_duration": room.game_duration,
            "players_min": room.players_min,
            "players_max": room.players_max,
            "reservation_url": room.reservation_url,
            "lm_id": room.lm_id,
            "mt_id": room.mt_id,
            # "company_id" : db_company.id,
            # "department_id" : db_department.id,
        }

        new_db_room = await self.room_repo.create(**room_data)

        for translation in room.translation:
            room_translation_data = {
                "room_id": new_db_room.id,
                "lang": translation.lang,
                "title": translation.title,
                "lead": translation.lead,
                "description": translation.description,
            }

            await self.room_translation_repo.create(**room_translation_data)

        return new_db_room

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize string to make it URL-safe.
        Remove non-alphanumeric characters, replace spaces with hyphens,
        and handle duplicate or leading/trailing hyphens.
        """
        # Transliterate Unicode characters to ASCII
        safe_name = unidecode(input_str)

        # Replace non-alphanumeric characters (except hyphens) with spaces
        cleaned_str = re.sub(r"[^a-zA-Z0-9\s-]", " ", safe_name)

        # Replace spaces with hyphens, collapse multiple spaces/hyphens into one
        hyphenated_str = re.sub(r"[\s-]+", "-", cleaned_str).lower()

        # Remove leading and trailing hyphens
        return hyphenated_str.strip("-")

    async def generate_unique_slug(self, name: str, street_address: str) -> str:
        """Generate a unique URL-friendly slug."""
        base_slug = self.sanitize_input(name)

        if not await self.room_exists_by_url_slug(base_slug):
            return base_slug

        slug_with_address = f"{base_slug}-{self.sanitize_input(street_address)}"
        if not await self.room_exists_by_url_slug(slug_with_address):
            return slug_with_address

        raise ValueError(f"Unable to generate a unique slug for room '{name}' at '{street_address}'")
