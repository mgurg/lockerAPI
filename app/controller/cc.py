from typing import Annotated

from fastapi import APIRouter, Depends

from app.service.CommandService import CommandService

cc_router = APIRouter()

commandServiceDependency = Annotated[CommandService, Depends()]


@cc_router.get("/company")
async def get_first_unverified_company(command_service: commandServiceDependency):
    db_company = await command_service.get_first_unverified_company()
    return db_company
