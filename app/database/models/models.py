from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


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


room_language_link = Table(
    "room_language_link",
    Base.metadata,
    Column("room_id", sa.Integer, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("language_id", sa.Integer, ForeignKey("languages.id", ondelete="CASCADE"), primary_key=True)
)


class Location(BaseModel):
    __tablename__ = "locations"
    street_address: Mapped[str]
    city: Mapped[str]
    state_province: Mapped[str | None]
    postal_code: Mapped[str | None]
    country: Mapped[str]
    located_in: Mapped[str | None]
    type: Mapped[str | None]
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lon: Mapped[float | None] = mapped_column(Numeric(10, 7))

    rooms: Mapped[list["Room"]] = relationship(back_populates="location")
    companies: Mapped[list["Company"]] = relationship(back_populates="location")
    departments: Mapped[list["Department"]] = relationship(back_populates="location")


class City(BaseModel):
    __tablename__ = "cities"
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lon: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lat_min: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lon_min: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lat_max: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lon_max: Mapped[float | None] = mapped_column(Numeric(10, 7))
    population: Mapped[int | None]
    importance: Mapped[float | None]
    category: Mapped[str] = mapped_column(String(16))
    region: Mapped[str | None] = mapped_column(String(64))
    country: Mapped[str | None] = mapped_column(String(2))
    seo_title: Mapped[str | None] = mapped_column(String())
    seo_description: Mapped[str | None] = mapped_column(String())

    geo_names: Mapped[list["GeoName"]] = relationship(back_populates="city")


class GeoName(BaseModel):
    __tablename__ = "geo_names"
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    name: Mapped[str] = mapped_column(String(128))
    name_ascii: Mapped[str] = mapped_column(String(128))
    country: Mapped[str] = mapped_column(String(2))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())

    city: Mapped["City"] = relationship(back_populates="geo_names")


class Room(BaseModel):
    __tablename__ = "rooms"

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    url_slug: Mapped[str]
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str]
    active: Mapped[bool]
    players_min: Mapped[int | None]
    players_max: Mapped[int | None]
    price_from: Mapped[float | None]
    game_duration: Mapped[int | None]
    game_difficulty: Mapped[str | None]
    game_fear_index: Mapped[str | None]
    reservation_url: Mapped[str | None]
    url_yt: Mapped[str | None]
    lm_id: Mapped[str | None]
    mt_id: Mapped[str | None]
    order: Mapped[str | None]
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime())
    opened_at: Mapped[DateTime | None] = mapped_column(DateTime())
    suspended_at: Mapped[DateTime | None] = mapped_column(DateTime())
    closed_at: Mapped[DateTime | None] = mapped_column(DateTime())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now(), onupdate=func.now())
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())

    location: Mapped[Optional["Location"]] = relationship(back_populates="rooms")
    translations: Mapped[list["RoomTranslation"]] = relationship(back_populates="room")
    languages: Mapped[list["Language"]] = relationship(secondary="room_language_link", back_populates="rooms")
    # tags: Mapped[List["Tag"]] = relationship(secondary="room_tag", back_populates="rooms")


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)

    # Many-to-many relationship with Room
    rooms: Mapped[list[Room]] = relationship(
        secondary=room_language_link, back_populates="languages"
    )


class RoomTranslation(BaseModel):
    __tablename__ = "room_translations"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    lang: Mapped[str] = mapped_column(String(2))
    title: Mapped[str] = mapped_column(String(128))
    lead: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(String(512))
    is_ai: Mapped[bool | None] = mapped_column(Boolean)

    room: Mapped["Room"] = relationship(back_populates="translations")


class Company(BaseModel):
    __tablename__ = "companies"

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    brand: Mapped[str | None] = mapped_column(String())
    name: Mapped[str] = mapped_column(String())
    gov_id: Mapped[str | None] = mapped_column(String())
    gov_id_type: Mapped[str | None] = mapped_column(String())
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    place_id: Mapped[str | None] = mapped_column(String())
    website: Mapped[str | None] = mapped_column(String())
    phone: Mapped[str | None] = mapped_column(String())
    email: Mapped[str | None] = mapped_column(String())
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now(), onupdate=func.now())
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())

    location: Mapped[Optional["Location"]] = relationship(back_populates="companies")
    departments: Mapped[list["Department"]] = relationship(back_populates="company")


class Department(BaseModel):
    __tablename__ = "departments"

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))

    company: Mapped["Company"] = relationship(back_populates="departments")
    location: Mapped["Location"] = relationship(back_populates="departments")


class AiGame(BaseModel):
    __tablename__ = "ai_games"

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    theme: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[str] = mapped_column(String(), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(), nullable=False)
    category: Mapped[str] = mapped_column(String(), nullable=False)
    occasion: Mapped[str] = mapped_column(String(), nullable=False)
    email: Mapped[str] = mapped_column(String())
    ip: Mapped[str] = mapped_column(String())
    location: Mapped[str] = mapped_column(String())
    is_valid: Mapped[bool] = mapped_column(Boolean())
    token: Mapped[str] = mapped_column(String(), nullable=False)
    intro: Mapped[str] = mapped_column(String(), nullable=False)
    ending: Mapped[str] = mapped_column(String(), nullable=False)
    puzzle_1: Mapped[str | None] = mapped_column(String())
    puzzle_2: Mapped[str | None] = mapped_column(String())
    puzzle_3: Mapped[str | None] = mapped_column(String())
    puzzle_4: Mapped[str | None] = mapped_column(String())
    state: Mapped[str] = mapped_column(String())
    current_puzzle: Mapped[int] = mapped_column(Integer())
    hints_remaining: Mapped[int] = mapped_column(Integer())
    wrong_answers: Mapped[int] = mapped_column(Integer())
    rating: Mapped[int | None] = mapped_column(Integer())
    remarks: Mapped[str | None] = mapped_column(String())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now(), onupdate=func.now())
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())
