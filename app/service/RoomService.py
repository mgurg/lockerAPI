import re
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from sqlalchemy import BinaryExpression
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from unidecode import unidecode

from app.datbase.models.models import Room
from app.datbase.repository.CityRepo import CityRepo
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
            room_translation_repo: Annotated[RoomTranslationRepo, Depends()]
    ) -> None:
        self.room_repo = room_repo
        self.city_repo = city_repo
        self.location_repo = location_repo
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

    async def get_room_by_url_slug_and_language(self, room_url_slug, lang_code,
                                                load_relations: list[str | BinaryExpression] = None):
        db_item = await self.room_repo.get_by_url_slug_and_lang(room_url_slug, lang_code, load_relations)
        if not db_item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_url_slug}` not found!")

        # Fetch the specific translation for the given language
        translation = next((t for t in db_item.translations if t.lang == lang_code), None)
        db_item.translations = [translation] if translation else []

        return db_item

    async def room_exists_by_url_slug(self, room_url_slug: str) -> bool:
        db_item = await self.room_repo.get_by_url_slug(room_url_slug)
        return db_item is not None

    async def create_room(self, room: RoomAdd) -> Room | None:
        db_city = await self.city_repo.get_by_id(3)

        try:
            unique_slug = await self.generate_unique_slug(room.name, room.location.city)
        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e

        if room.location:
            print(room.location.street_address)
            print(room.location.city)
            location_data = {
                "street_address": room.location.street_address,
                "city": room.location.city,
                "state_province": room.location.state_province,
                "postal_code": room.location.postal_code,
                "country": room.location.country,
                "lat": room.location.lat,
                "lng": room.location.lng,
            }
            db_location = await self.location_repo.create(**location_data)

            room_data = {
                "uuid": str(uuid4()),
                "url_slug": unique_slug,
                "name": room.name,
                # "city_id": 3,
                "city": db_city,
                "location": db_location
            }

            new_db_room = await self.room_repo.create(**room_data)

            room_translation_data = {
                "room_id": new_db_room.id,
                "lang": room.translation.lang,
                "title": room.translation.title,
                "lead": room.translation.lead,
                "description": room.translation.description,
            }

            await self.room_translation_repo.create(**room_translation_data)

            return new_db_room

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize string to make it URL-friendly.
        Remove non-alphanumeric characters, replace spaces with hyphens,
        and remove duplicate hyphens.
        """
        # Transliterate Unicode characters to ASCII
        ascii_str = unidecode(input_str)

        # Replace non-alphanumeric characters (except hyphens) with spaces
        cleaned_str = re.sub(r"[^a-zA-Z0-9\s-]", " ", ascii_str)

        # Replace spaces with hyphens and convert to lowercase
        hyphenated_str = re.sub(r"\s+", "-", cleaned_str).lower()

        # Remove duplicate hyphens
        single_hyphen_str = re.sub(r"-+", "-", hyphenated_str)

        # Remove leading and trailing hyphens
        return single_hyphen_str.strip("-")

    async def generate_unique_slug(self, name: str, street_address: str) -> str:
        """Generate a unique URL-friendly slug."""
        base_slug = self.sanitize_input(name)

        if not await self.room_exists_by_url_slug(base_slug):
            return base_slug

        slug_with_address = f"{base_slug}-{self.sanitize_input(street_address)}"
        if not await self.room_exists_by_url_slug(slug_with_address):
            return slug_with_address

        raise ValueError(f"Unable to generate a unique slug for room '{name}' at '{street_address}'")
