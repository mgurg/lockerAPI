from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.service.SeoService import SeoService

seo_router = APIRouter()

# CurrentUser = Annotated[User, Depends(check_token)]
seoServiceDependency = Annotated[SeoService, Depends()]


@seo_router.get("/sitemap", response_class=Response)
async def room_by_uuid(seo_service: seoServiceDependency):
    sitemap_content = await seo_service.generate()
    return Response(content=sitemap_content, media_type="application/xml")
