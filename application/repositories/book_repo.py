from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Union

from application.services.utils.books_filter import BookFilter
from core import OrmEntityRepository
from core.base_repos import OrmEntityRepoInterface
from application.models import Book
from logger import logger


class BookRepoInterface(OrmEntityRepository):
    async def get_all_books(
            self,
            session: AsyncSession,
            filters: BookFilter,
            page: int = 0,
            limit: int = 10,
    ) -> list[Book]:
        ...

    async def get_by_id(
            self,
            session: AsyncSession,
            id: UUID4
    ) -> Book:
        pass


CombinedBookRepoInterface = Union[OrmEntityRepoInterface, BookRepoInterface]


class BookRepository(OrmEntityRepository):
    model: Book = Book

    async def get_all_books(
            self,
            session: AsyncSession,
            filters: BookFilter,
            page: int = 0,
            limit: int = 10,
    ) -> list[Book]:
        stmt = select(self.model).options(
            selectinload(Book.categories),
            selectinload(Book.authors)
        )

        if limit > 1000:
            session = session.bind.execution_options(yield_per=100)

            stmt = select(self.model).options(
                selectinload(Book.categories),
                selectinload(Book.authors)
            )
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt).offset(page * limit).limit(limit)

            result = await session.execute(stmt)

            books: list[Book] = []

            for chunk in result.yield_per(2):
                books.append(chunk[0])

            logger.debug("books: ", books)
            return books

        stmt = select(self.model).options(
            selectinload(Book.categories),
            selectinload(Book.authors)
        )

        stmt = filters.filter(stmt)
        stmt = filters.sort(stmt).offset(page * limit).limit(limit)

        books = list((await session.scalars(stmt)).all())
        logger.debug("books: ", books)
        return books

    async def get_by_id(
            self,
            session: AsyncSession,
            id: UUID4
    ) -> Book:
        stmt = select(self.model).options(
            selectinload(Book.categories),
            selectinload(Book.authors)
        ).where(Book.id == str(id))

        return (await session.execute(stmt)).scalar_one_or_none()
