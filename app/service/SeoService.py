from datetime import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from app.config import get_settings
from app.database.models.models import City, Room
from app.database.repository.CityRepo import CityRepo
from app.database.repository.GeoNameRepo import GeoNameRepo
from app.database.repository.RoomRepo import RoomRepo


class SitemapEntry(BaseModel):
    """Represents a single sitemap URL entry."""
    loc: str
    lastmod: str
    changefreq: str
    priority: float


class SeoService:
    """Service responsible for generating sitemaps."""

    def __init__(
            self,
            city_repo: Annotated[CityRepo, Depends()],
            geo_name_repo: Annotated[GeoNameRepo, Depends()],
            room_repo: Annotated[RoomRepo, Depends()],
    ) -> None:
        """
        Initialize the SEO service with required repositories.

        :param city_repo: Repository for city-related operations
        :param geo_name_repo: Repository for geolocation-related operations
        :param room_repo: Repository for room-related operations
        """
        self.city_repo = city_repo
        self.geo_name_repo = geo_name_repo
        self.room_repo = room_repo
        self.settings = get_settings()

    def _format_sitemap_entry(self, url: str, lastmod: datetime | None, changefreq: str,
                              priority: float) -> SitemapEntry:
        """
        Create a formatted sitemap entry with default fallback values.

        :param url: URL of the page
        :param lastmod: Last modification date
        :param changefreq: Frequency of page updates
        :param priority: Page priority
        :return: Formatted SitemapEntry
        """
        formatted_lastmod = lastmod.strftime("%Y-%m-%d") if lastmod else datetime.now().strftime("%Y-%m-%d")

        return SitemapEntry(loc=url, lastmod=formatted_lastmod, changefreq=changefreq, priority=priority)

    def _generate_sitemap_xml(self, entries: list[SitemapEntry]) -> str:
        """
        Generate XML sitemap from a list of sitemap entries.

        :param entries: List of sitemap entries
        :return: Complete XML sitemap as a string
        """
        sitemap_header = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        sitemap_footer = "</urlset>"

        sitemap_entries = "\n".join([
            f"""    <url>
        <loc>{entry.loc}</loc>
        <lastmod>{entry.lastmod}</lastmod>
        <changefreq>{entry.changefreq}</changefreq>
        <priority>{entry.priority}</priority>
    </url>""" for entry in entries
        ])

        return f"{sitemap_header}\n{sitemap_entries}\n{sitemap_footer}"

    async def generate_city_sitemap(self) -> str:
        """
        Generate sitemap for cities in Poland.

        :return: XML sitemap for city pages
        """
        cities: list[City] = await self.geo_name_repo.get_by_country_and_lang("PL", "pl")
        base_url = f"https://{self.settings.APP_DOMAIN}"

        sitemap_entries = [
            self._format_sitemap_entry(
                url=f"{base_url}/pl/escape-rooms/{city.name_ascii}",
                lastmod=city.created_at,
                changefreq="daily",
                priority=0.7
            ) for city in cities
        ]

        return self._generate_sitemap_xml(sitemap_entries)

    async def generate_rooms_sitemap(self) -> str:
        """
        Generate sitemap for active escape rooms.

        :return: XML sitemap for room pages
        """
        rooms: list[Room] = await self.room_repo.get_all_active()
        base_url = f"https://{self.settings.APP_DOMAIN}"

        sitemap_entries = [
            self._format_sitemap_entry(
                url=f"{base_url}/pl/escape-room/{room.url_slug}",
                lastmod=room.updated_at,
                changefreq="weekly",
                priority=0.8
            ) for room in rooms
        ]

        return self._generate_sitemap_xml(sitemap_entries)
