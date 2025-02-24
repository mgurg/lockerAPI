from datetime import UTC, datetime
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

from app.database.models.models import Room
from app.database.repository.CityRepo import CityRepo
from app.database.repository.CompanyRepo import CompanyRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.database.repository.LanguageRepo import LanguageRepo
from app.database.repository.LocationRepo import LocationRepo
from app.database.repository.RoomRepo import RoomRepo
from app.database.repository.RoomTranslationRepo import RoomTranslationRepo
from app.schemas.requests import RoomAdd, RoomEdit
from app.shared.text_utils import sanitize_location_input


class RoomService:
    def __init__(
            self,
            room_repo: Annotated[RoomRepo, Depends()],
            city_repo: Annotated[CityRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
            company_repo: Annotated[CompanyRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            room_translation_repo: Annotated[RoomTranslationRepo, Depends()],
            language_repo: Annotated[LanguageRepo, Depends()]
    ) -> None:
        self.room_repo = room_repo
        self.city_repo = city_repo
        self.location_repo = location_repo
        self.company_repo = company_repo
        self.department_repo = department_repo
        self.room_translation_repo = room_translation_repo
        self.language_repo = language_repo

    async def get_room_by_uuid(self, room_uuid: UUID) -> Room | None:
        db_room = await self.room_repo.get_by_uuid(room_uuid,
                                                   ["location", "tags", "languages", "translations", "company", "department"])

        if not db_room:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_uuid}` not found!")

        return db_room

    async def get_room_count(self) -> int:
        return await self.room_repo.get_count()

    async def get_rooms_nearby(self, city_ascii_name: str):
        city = await self.city_repo.get_place_by_name(city_ascii_name)
        if city is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"City `{city_ascii_name}` not found!")

        db_rooms = await self.room_repo.get_nearby_rooms(city.lat, city.lon, 50,
                                                         ["location", "languages", "translations"])
        return db_rooms

    async def get_room_by_url_slug(self, room_url_slug: str,
                                   load_relations: list[str | BinaryExpression] = None) -> Room | None:
        db_room = await self.room_repo.get_by_url_slug(room_url_slug, load_relations)

        if not db_room:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_url_slug}` not found!")

        return db_room

    async def get_room_by_url_slug_and_language(self, room_url_slug, lang_code: CountryAlpha2,
                                                load_relations: list[str | BinaryExpression] = None):
        db_room = await self.room_repo.get_by_url_slug_and_lang(room_url_slug, lang_code, load_relations)
        if not db_room:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_url_slug}` not found!")

        # Fetch the specific translation for the given language
        translation = next((t for t in db_room.translations if t.lang == lang_code.lower()), None)
        db_room.translation = translation if translation else None

        return db_room

    async def get_rooms_by_location_and_language(self, location: str, language: str,
                                                 load_relations: list[str | BinaryExpression],
                                                 offset: int,
                                                 limit: int,
                                                 sort_column: str,
                                                 sort_order: str):
        url_safe_place = sanitize_location_input(location)
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
        location = None
        if not db_company:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Company `{room.company_uuid}` not found!")
        else:
            location = db_company.location

        db_department = await self.department_repo.get_by_uuid(room.department_uuid, ["location"])
        if not db_department:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail=f"Department `{room.department_uuid}` not found!")
        else:
            location = db_department.location

        db_languages = await self.language_repo.get_by_codes(room.supported_languages)

        translation = ""
        if location.lat and location.lon:
            db_cities = await self.city_repo.get_places_by_bbox(location.lat, location.lon,
                                                                ["geo_names"])
            for city in db_cities:
                translation = next((t for t in city.geo_names if t.lang == "pl"), None)
                logger.info(f"Matching `{room.name}` with {city.id} as {translation.name}")
        else:
            logger.warning(
                f"No lat/long data for `{room.name}`: {location.street_name}, {location.city}")
        try:
            unique_slug = await self.generate_unique_slug(room.name, "XXXX")

        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e

        room_data = {
            "uuid": str(uuid4()),
            "url_slug": unique_slug,
            "name": room.name,
            "active": True,
            "location": location,
            "price_from": room.price_from,
            "duration": room.game_duration,
            "players_min": room.players_min,
            "players_max": room.players_max,
            "reservation_url": room.reservation_url,
            "lm_id": room.lm_id,
            "mt_id": room.mt_id,
            "company_id": db_company.id,
            "department_id": db_department.id,
            "languages": db_languages
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

    async def update_room(self, room_uuid: UUID, room: RoomEdit) -> None:
        db_room = await self.room_repo.get_by_uuid(room_uuid, ["location", "company", "department", "languages"])
        if not db_room:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Room with UUID {room_uuid} not found"
            )

        update_data = room.model_dump(exclude_unset=True)

        # Handle department and location updates
        if "department_uuid" in update_data:
            db_department = await self.department_repo.get_by_uuid(update_data["department_uuid"], ["location"])
            if not db_department:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Department `{update_data['department_uuid']}` not found!"
                )
            update_data["department_id"] = db_department.id
            update_data["location_id"] = db_department.location.id if db_department.location else db_room.location_id
            del update_data["department_uuid"]  # Remove UUID, as we store only the ID

        # Handle supported languages update
        if "supported_languages" in update_data:
            # db_languages = await self.language_repo.get_by_codes(update_data["supported_languages"])
            # update_data["languages"] = db_languages
            del update_data["supported_languages"]  # Remove from update_data since it's not a direct column

        update_data["updated_at"] = datetime.now(UTC)  # Ensure timestamp update

        # Handle translations update
        del update_data["translation"]

        await self.room_repo.update(db_room.id, **update_data)

        # if "translation" in update_data:
        #     await self.room_translation_repo.delete_by_room_id(db_room.id)
        #     for translation in update_data["translation"]:
        #         await self.room_translation_repo.create(
        #             room_id=db_room.id,
        #             lang=translation.lang,
        #             title=translation.title,
        #             lead=translation.lead,
        #             description=translation.description
        #
        #         )

        return None

    async def delete_room(self, room_uuid: UUID) -> None:
        db_room = await self.room_repo.get_by_uuid(room_uuid)
        if not db_room:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{room_uuid}` not found!")

        db_translations = await self.room_translation_repo.get_translations_by_room_id(db_room.id)

        for translation in db_translations:
            await self.room_translation_repo.delete(translation.id)

        await self.location_repo.delete(db_room.location_id)
        await self.room_repo.delete(db_room.id)

        return None

    async def generate_unique_slug(self, name: str, city: str) -> str:
        """Generate a unique URL-friendly slug."""
        base_slug = sanitize_location_input(name)

        if not await self.room_exists_by_url_slug(base_slug):
            return base_slug

        slug_with_address = f"{base_slug}-{sanitize_location_input(city)}"
        if not await self.room_exists_by_url_slug(slug_with_address):
            return slug_with_address

        raise ValueError(f"Unable to generate a unique slug for room '{name}' at '{city}'")
