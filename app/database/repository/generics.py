from typing import Any, TypeVar
from contextlib import asynccontextmanager

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert  # For PostgreSQL bulk insert optimization

from app.database.models.models import BaseModel

T = TypeVar("T", bound=BaseModel)


class GenericRepo[T]:
    def __init__(self, session: AsyncSession, model: type[T]):
        """
        Initializes the repository with the given session and model.

        :param session: The SQLAlchemy session to use.
        :param model: The SQLAlchemy model to use.
        """
        self.session = session
        self.model = model

    @asynccontextmanager
    async def session_scope(self):
        """Provide a transactional scope."""
        try:
            yield self.session
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        finally:
            await self.session.close()

    async def get_all(self) -> list[T]:
        """
        Retrieves all objects from the database.

        :return: A list of all objects of the model type.
        """
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> T | None:
        """
        Retrieves an object by its ID.

        :param id: The ID of the object to retrieve.
        :return: The object if found, None otherwise.
        """
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs: dict[str, Any]) -> T:
        """
        Creates a new object with the given keyword arguments.

        :param kwargs: The keyword arguments to use for creating the object.
        :return: The newly created object.
        """
        obj = self.model(**kwargs)
        async with self.session_scope():
            self.session.add(obj)
            await self.session.flush()  # Flush before refresh
            await self.session.refresh(obj)

        return obj

    async def create_all(self, data_list: list[dict[str, Any]]) -> None:
        """
        Inserts multiple records efficiently using bulk insert.
        """
        async with self.session_scope():
            stmt = insert(self.model).values(data_list)
            await self.session.execute(stmt)

    async def update(self, id: int, **kwargs: dict[str, Any]) -> T | None:
        """
        Updates an object with the given ID and keyword arguments.

        :param id: The ID of the object to update.
        :param kwargs: The fields to update.
        :return: The updated object if found, None otherwise.
        """
        async with self.session_scope():
            query = update(self.model).where(self.model.id == id).values(**kwargs).returning(self.model)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        """
        Deletes an object by its ID.

        :param id: The ID of the object to delete.
        :return: True if deleted, False if not found.
        """
        obj = await self.get_by_id(id)
        if obj:
            async with self.session_scope():
                await self.session.delete(obj)
            return True
        return False

    async def filter(self, page: int = 1, per_page: int = 10, case_insensitive: bool = False, **kwargs: Any) -> list[T]:
        """
        Filters objects based on the given keyword arguments and paginates the result.

        :param page: The page number for pagination.
        :param per_page: Number of records per page.
        :param case_insensitive: Whether to apply case-insensitive filtering.
        :param kwargs: The filtering conditions.
        :return: A paginated list of filtered objects.
        """
        offset = (page - 1) * per_page  # Fix off-by-one error
        filters = [
            getattr(self.model, k).ilike(f"%{v}%") if case_insensitive else getattr(self.model, k) == v
            for k, v in kwargs.items()
        ]
        query = select(self.model).where(and_(*filters)).limit(per_page).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()
