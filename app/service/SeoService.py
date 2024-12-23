from datetime import datetime
from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.database.repository.CityRepo import CityRepo
from app.database.repository.CompanyRepo import CompanyRepo
from app.database.repository.DepartmentRepo import DepartmentRepo
from app.database.repository.GeoNameRepo import GeoNameRepo
from app.database.repository.LocationRepo import LocationRepo

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
        cities = await self.geo_name_repo.get_by_country("pl")
        base_url = "https://your-nuxt-app.com"

        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        """
        for city in cities:
            url = f"{base_url}/l/{city.name_ascii}"
            sitemap_content += f"""    <url>
                <loc>{url}</loc>
                <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
                <changefreq>daily</changefreq>
                <priority>0.8</priority>
            </url>
        """
        sitemap_content += "</urlset>"

        return sitemap_content
