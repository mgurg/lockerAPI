import math
from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.language_code import LanguageAlpha2
from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import get_db
from app.database.models.models import City, GeoName
from app.database.repository.generics import GenericRepo

UserDB = Annotated[AsyncSession, Depends(get_db)]


class CityRepo(GenericRepo[City]):
    def __init__(self, session: UserDB) -> None:
        self.Model = City
        super().__init__(session, self.Model)

    def _apply_relationship_loading(self, query, load_relations: list[str | BinaryExpression] = None):
        if not load_relations:
            return query

        for relation in load_relations:  # load_relations=["*"]
            if relation == "*":
                return query.options(selectinload("*"))
            elif isinstance(relation, str):  # load_relations=["city", "location"]
                query = query.options(selectinload(getattr(self.Model, relation)))
            elif isinstance(relation, BinaryExpression):  # load_relations=[Room.city, Room.location]
                query = query.options(selectinload(relation))

        return query

    async def get_by_uuid(self, uuid: UUID) -> City | None:
        query = select(self.Model).where(self.Model.uuid == uuid)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_place_by_name(self, place_name: str, language: LanguageAlpha2 | None = None):
        # Base query with join on the relationship
        query = select(City).join(City.geo_names).where(GeoName.name_ascii == place_name)

        # Add language filter if provided
        if language:
            query = query.where(GeoName.lang == language)

        query = query.options(selectinload(City.geo_names))

        # Execute the query
        result = await self.session.execute(query)

        # Return the first matching city
        # city = result.scalars().all()
        city = result.scalars().first()

        return city

    async def get_places_by_bbox(
        self, latitude: float, longitude: float, load_relations: list[str | BinaryExpression] = None
    ) -> Sequence[City]:
        query = select(self.Model).where(
            (self.Model.lat_min <= latitude)
            & (self.Model.lat_max >= latitude)
            & (self.Model.lon_min <= longitude)
            & (self.Model.lon_max >= longitude)
        )
        query = self._apply_relationship_loading(query, load_relations)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_details_by_ascii_name(self, name_ascii: str, language: LanguageAlpha2, country: CountryAlpha2):
        query = (
            select(City, GeoName)
            .join(GeoName, GeoName.city_id == City.id)
            .where(
                GeoName.country == country,
                GeoName.name_ascii == name_ascii,
                GeoName.lang == language
            )
        )

        result = await self.session.execute(query)
        city_and_name = result.first()

        return city_and_name

    import math
    from math import cos, radians

    # Constants

    async def get_closest_cities(self, lat: Latitude, lon: Longitude, language: LanguageAlpha2 | None = None):
        """
        Finds all cities within a 20 km bounding box around the given latitude and longitude.
        Results are sorted by distance and include the city name and importance.

        :param lat: Latitude of the reference point
        :param lon: Longitude of the reference point
        :return: List of tuples containing city name and importance
        """

        KM_PER_DEGREE_LAT = 111  # Approximate number of kilometers per degree of latitude
        radius_km = 20  # Radius in kilometers

        # Convert lat and lon to floats
        lat = float(lat)
        lon = float(lon)

        # Calculate the difference in lat/lon for the bounding box
        lat_diff = radius_km / KM_PER_DEGREE_LAT  # Lat diff is straightforward
        lon_diff = radius_km / (KM_PER_DEGREE_LAT * math.cos(math.radians(lat)))  # Lon diff varies with latitude

        # Calculate the bounding box
        min_lat, max_lat = lat - lat_diff, lat + lat_diff
        min_lon, max_lon = lon - lon_diff, lon + lon_diff

        # Fetch all cities with their latitude, longitude, and importance
        query = (
            select(GeoName.name, City.lat, City.lon, City.importance)
            .join(GeoName, GeoName.city_id == City.id)
            .where(
                GeoName.lang == language
            )
            .distinct(City.id)
            .filter(
                City.lat >= min_lat, City.lat <= max_lat,
                City.lon >= min_lon, City.lon <= max_lon
            )
        )

        # Execute the query
        result = await self.session.execute(query)
        cities = result.fetchall()

        return cities
