from typing import Optional

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.datbase.db import Base


class BaseModel(Base):
    __abstract__ = True
    """
    Base model for all tables

    Attributes:
        id (int): Primary key for all tables
        created_at (datetime): Date and time of creation
        updated_at (datetime): Date and time of last update
    """

    id: Mapped[int] = mapped_column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)


# class Room(BaseModel):
#     __tablename__ = "rooms"
#     uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)


class Location(BaseModel):
    __tablename__ = "locations"
    street_address: Mapped[str]
    city: Mapped[str]
    state_province: Mapped[str | None]
    postal_code: Mapped[str | None]
    country: Mapped[str]
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7))

    rooms: Mapped[list["Room"]] = relationship(back_populates="location")


class City(BaseModel):
    __tablename__ = "cities"
    local_id: Mapped[str]
    local_id_type: Mapped[str]
    population: Mapped[int | None]
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    category: Mapped[str] = mapped_column(String(16))
    region: Mapped[str | None] = mapped_column(String(64))
    country: Mapped[str | None] = mapped_column(String(2))

    rooms: Mapped[list["Room"]] = relationship(back_populates="city")
    normalized_geo_names: Mapped[list["GeoName"]] = relationship(back_populates="city")


class GeoName(BaseModel):
    __tablename__ = "geo_names"
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    name: Mapped[str] = mapped_column(String(128))
    name_ascii: Mapped[str] = mapped_column(String(128))
    country: Mapped[str] = mapped_column(String(2))
    lang: Mapped[str] = mapped_column(String(2))

    city: Mapped["City"] = relationship(back_populates="normalized_geo_names")


class Room(BaseModel):
    __tablename__ = "rooms"

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    url_slug: Mapped[str]
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    name: Mapped[str]

    city: Mapped["City"] = relationship(back_populates="rooms")
    location: Mapped[Optional["Location"]] = relationship(back_populates="rooms")
    translations: Mapped[list["RoomTranslation"]] = relationship(back_populates="room")
    # languages: Mapped[List["Language"]] = relationship(secondary="room_language", back_populates="rooms")
    # tags: Mapped[List["Tag"]] = relationship(secondary="room_tag", back_populates="rooms")


class RoomTranslation(BaseModel):
    __tablename__ = "room_translations"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    lang: Mapped[str] = mapped_column(String(2))
    title: Mapped[str] = mapped_column(String(128))
    lead: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(String(512))

    room: Mapped["Room"] = relationship(back_populates="translations")
