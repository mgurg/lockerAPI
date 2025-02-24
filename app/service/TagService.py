from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.database.models.models import Room, Tag
from app.database.repository.CityRepo import CityRepo
from app.database.repository.CompanyRepo import CompanyRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.database.repository.LanguageRepo import LanguageRepo
from app.database.repository.LocationRepo import LocationRepo
from app.database.repository.RoomRepo import RoomRepo
from app.database.repository.RoomTranslationRepo import RoomTranslationRepo
from app.database.repository.TagRepo import TagRepo
from app.schemas.requests import TagAdd


class TagService:
    def __init__(
            self,
            room_repo: Annotated[RoomRepo, Depends()],
            city_repo: Annotated[CityRepo, Depends()],
            location_repo: Annotated[LocationRepo, Depends()],
            company_repo: Annotated[CompanyRepo, Depends()],
            department_repo: Annotated[DepartmentRepo, Depends()],
            room_translation_repo: Annotated[RoomTranslationRepo, Depends()],
            language_repo: Annotated[LanguageRepo, Depends()],
            tag_repo: Annotated[TagRepo, Depends()]
    ) -> None:
        self.room_repo = room_repo
        self.city_repo = city_repo
        self.location_repo = location_repo
        self.company_repo = company_repo
        self.department_repo = department_repo
        self.room_translation_repo = room_translation_repo
        self.language_repo = language_repo
        self.tag_repo = tag_repo

    async def get_tag_by_uuid(self, tag_uuid: UUID) -> Room | None:
        db_room = await self.tag_repo.get_by_uuid(tag_uuid)

        if not db_room:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Room `{tag_uuid}` not found!")

        return db_room

    async def create_tag(self, tag: TagAdd) -> Tag | None:
        db_room = await self.room_repo.get_by_uuid(tag.room_uuid)
        if not db_room:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail=f"Room `{tag.room_uuid}` not found!")

        db_tag = await self.tag_repo.get_by_name(tag.name)
        if not db_tag:
            tag_data = {
                    "name": tag.name,
                }

            if tag.room_uuid:
                db_rooms = await self.room_repo.get_by_uuids([tag.room_uuid])
                tag_data["rooms"] = db_rooms

            db_tag = await self.tag_repo.create(**tag_data)
        else:
            ...
            # db_rooms = await self.room_repo.get_by_uuids([tag.room_uuid])
            # await self.tag_repo.update(db_tag.id, **{"rooms": db_rooms})
        return db_tag
