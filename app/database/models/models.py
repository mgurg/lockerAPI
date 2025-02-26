from typing import Optional
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, configure_mappers, mapped_column, relationship

from app.database.db import Base
from app.database.models.enums import ContactType, GameDifficulty, FearLevel

configure_mappers()


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

contacts_departments_link = Table(
    "contacts_departments_link",
    BaseModel.metadata,
    Column("department_id", ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
    Column("contact_id", ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True),
)

room_tag_link = Table(
    "room_tag_link",
    BaseModel.metadata,
    Column("room_id", ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Location(BaseModel):
    __tablename__ = "locations"
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    street_name: Mapped[str | None]
    street_number: Mapped[str | None]
    city: Mapped[str]
    state_province: Mapped[str | None]
    postal_code: Mapped[str | None]
    country: Mapped[str]
    located_in: Mapped[str | None]
    type: Mapped[str]
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lon: Mapped[float | None] = mapped_column(Numeric(10, 7))

    rooms: Mapped[list["Room"]] = relationship(back_populates="location")

    companies: Mapped[list["Company"]] = relationship(back_populates="location")
    departments: Mapped[list["Department"]] = relationship(back_populates="location")


class Contact(BaseModel):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid4)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[ContactType] = mapped_column(Enum(ContactType), nullable=False)
    value: Mapped[str] = mapped_column(String())
    country_code: Mapped[str | None] = mapped_column(String(), nullable=True)
    description: Mapped[str | None] = mapped_column(String(), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean(), default=False)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now(), onupdate=func.now())
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="contacts")
    departments: Mapped[list["Department"]] = relationship(secondary="contacts_departments_link",
                                                           back_populates="contacts")


class City(BaseModel):
    __tablename__ = "cities"
    name: Mapped[str]
    name_ascii: Mapped[str]
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
    language: Mapped[str | None] = mapped_column(String(2))
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
    name: Mapped[str]
    active: Mapped[bool]
    players_min: Mapped[int | None]
    players_max: Mapped[int | None]
    price_from: Mapped[float | None]
    currency: Mapped[str | None]
    duration: Mapped[int | None]
    difficulty: Mapped[GameDifficulty | None] = mapped_column(Enum(GameDifficulty), nullable=True)
    fear_level: Mapped[FearLevel | None] = mapped_column(Enum(FearLevel), nullable=True)
    rating: Mapped[str | None]
    category: Mapped[str | None]
    booking_url: Mapped[str | None]
    url_yt: Mapped[str | None]
    lm_id: Mapped[str | None]
    mt_id: Mapped[str | None]
    sort_order: Mapped[str | None]
    hero_img: Mapped[str | None]
    icon_img: Mapped[str | None]
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime())
    opened_at: Mapped[DateTime | None] = mapped_column(DateTime())
    suspended_at: Mapped[DateTime | None] = mapped_column(DateTime())
    closed_at: Mapped[DateTime | None] = mapped_column(DateTime())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now(), onupdate=func.now())
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())

    location: Mapped[Optional["Location"]] = relationship(back_populates="rooms")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="rooms")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="rooms")
    translations: Mapped[list["RoomTranslation"]] = relationship(back_populates="room")

    # Many-to-Many Relationship
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=room_tag_link, back_populates="rooms")
    languages: Mapped[list["Language"]] = relationship("Language", secondary=room_language_link, back_populates="rooms")

    # contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="room")


class Tag(BaseModel):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Many-to-Many Relationship
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        secondary=room_tag_link,
        back_populates="tags"
    )


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
    website: Mapped[str | None] = mapped_column(String())
    phone: Mapped[str | None] = mapped_column(String())
    email: Mapped[str | None] = mapped_column(String())
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now(), onupdate=func.now())
    created_at: Mapped[DateTime | None] = mapped_column(DateTime(), default=func.now())

    location: Mapped[Optional["Location"]] = relationship(back_populates="companies")
    departments: Mapped[list["Department"]] = relationship(back_populates="company")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="company")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")


class Department(BaseModel):
    __tablename__ = "departments"

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String())
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))

    company: Mapped["Company"] = relationship(back_populates="departments")
    location: Mapped["Location"] = relationship(back_populates="departments")

    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="department")
    # contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="department")

    contacts: Mapped[list[Contact]] = relationship(
        secondary=contacts_departments_link, back_populates="departments"
    )


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
