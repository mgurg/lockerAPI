from datetime import datetime
from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.database.repository.CityRepo import CityRepo
from app.database.repository.GeoNameRepo import GeoNameRepo

settings = get_settings()


class SeoService:
    def __init__(
            self,
            city_repo: Annotated[CityRepo, Depends()],
            geo_name_repo: Annotated[GeoNameRepo, Depends()],
    ) -> None:
        self.city_repo = city_repo
        self.geo_name_repo = geo_name_repo

    async def generate(self):
        cities = await self.geo_name_repo.get_by_country_and_lang("PL", "pl")
        base_url = f"https://{settings.APP_DOMAIN}"

        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        """
        for city in cities:
            # Use the city's created_at field for the lastmod
            lastmod = city.created_at.strftime("%Y-%m-%d") if city.created_at else datetime.now().strftime("%Y-%m-%d")
            url = f"{base_url}/l/{city.name_ascii}"
            sitemap_content += f"""    <url>
        <loc>{url}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
"""
        # Close the sitemap content
        sitemap_content += "</urlset>"

        return sitemap_content
