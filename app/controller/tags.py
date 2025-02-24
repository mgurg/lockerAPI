from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.requests import TagAdd
from app.service.TagService import TagService

tag_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
tagServiceDependency = Annotated[TagService, Depends()]


@tag_router.post("")
async def get_rooms_count(tag_service: tagServiceDependency, tag: TagAdd):
    db_rooms_count = await tag_service.create_tag(tag)

    return db_rooms_count
