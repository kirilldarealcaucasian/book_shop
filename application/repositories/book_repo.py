import logging
from collections import defaultdict
from uuid import UUID

from sqlalchemy import select, desc, func
from sqlalchemy.exc import StatementError, InvalidRequestError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from typing_extensions import Literal
from typing import Union

from application.services.utils.books_filter import BookFilter
from core import OrmEntityRepository
from core.base_repos import OrmEntityRepoInterface
from core.exceptions import FilterAttributeError, ServerError, DBError
from application.models import Book, Category, BookCategoryAssoc
from logger import logger


class BookRepoInterface(OrmEntityRepository):
    async def get_all_books(
            self,
            session: AsyncSession,
            filters: BookFilter,
            page: int = 0,
            limit: int = 10,
    ):
        ...


CombinedBookRepoInterface = Union[OrmEntityRepoInterface, BookRepoInterface]


class BookRepository(OrmEntityRepository):
    model: Book = Book

    # async def get_all(
    #         self,
    #         session: AsyncSession,
    #         page: int = 0,
    #         limit: int = 10,
    #         **filters
    # ) -> list[Book]:
    #     key_value_filters: dict[str, str] | None = filters.get("key_value_filters", None)
    #     order_by_filters: defaultdict[Literal["desc", "asc"], list[str]] = filters.get("order_by_filters", None)
    #
    #     if key_value_filters is None and order_by_filters is None:
    #         stmt = select(self.model).options(
    #             selectinload(self.model.categories)
    #         ).offset(page * limit).limit(limit)
    #         res = await session.execute(stmt)
    #         return list(res)
    #
    #     model_attributes = {a for a in dir(self.model) if not a.startswith('_')}  # get model attributes(fields) to
    #     # perform checking against client filters
    #     logger.debug("model_attributes:", model_attributes)
    #
    #     if key_value_filters:
    #         for filter in list(key_value_filters.keys()):
    #             """
    #             if there is no attribute(field) in the model that client wants to filter by,
    #             then we just won't filter by this field instead of raising an Exception
    #             """
    #             if filter not in model_attributes:
    #                 # remove invalid filter from the key_value_filters
    #                 del key_value_filters[filter]
    #
    #     if order_by_filters:
    #         for filter in list(order_by_filters.keys()):
    #             # remove invalid filters from order_by_filters
    #             if filter not in model_attributes:
    #                 del order_by_filters[filter]
    #
    #     stmt = None
    #
    #     if "name" in key_value_filters.keys():
    #         # special case when we want to use LIKE
    #
    #         stmt = select(self.model).options(
    #             joinedload(self.model.categories)
    #         ).filter(
    #             self.model.name.ilike(f"%{key_value_filters['name']}%")
    #         ).filter(
    #             *[
    #                 func.lower(getattr(self.model, filter_name)) == func.lower(filter_value) for
    #                 filter_name, filter_value in
    #                 key_value_filters.items() if filter_name != "name"
    #             ]  # apply key_value_filter (example of filter: name="some name")
    #         ).order_by(
    #             *[desc(value) for value in order_by_filters["desc"]],  # apply order_by for "descending" fields
    #             *[value for value in order_by_filters["asc"]]  # apply order_by for "ascending" fields
    #         ).offset(page * limit).limit(limit)  # pagination
    #
    #     elif key_value_filters and order_by_filters and "name" not in key_value_filters:
    #         try:
    #             stmt = select(self.model).options(
    #                 joinedload(self.model.categories)
    #             ).filter(
    #                 *[
    #                     getattr(self.model, filter_name) == filter_value for filter_name, filter_value in
    #                     key_value_filters.items()
    #                 ]  # apply key_value_filters
    #             ).order_by(
    #                 *[desc(value) for value in order_by_filters["desc"]],
    #                 *[value for value in order_by_filters["asc"]]
    #             ).offset(page * limit).limit(limit)
    #         except AttributeError:
    #             extra = {"key_value_filters": key_value_filters}
    #             logging.error("Error while applying filters to the statement", extra, exc_info=True)
    #             raise FilterAttributeError
    #
    #     elif key_value_filters and not order_by_filters and "name" not in key_value_filters:
    #         try:
    #             stmt = select(self.model).options(
    #                 self.model.categories
    #             ).filter(
    #                 *[
    #                     getattr(self.model, filter_name) == filter_value for filter_name, filter_value in
    #                     key_value_filters.items()
    #                 ]  # apply key_value_filters
    #             ).offset(page * limit).limit(limit)
    #         except AttributeError:
    #             extra = {"key_value_filters": key_value_filters}
    #             logging.error("Error while applying filters to the statement", extra, exc_info=True)
    #             raise FilterAttributeError
    #
    #     elif order_by_filters and not key_value_filters and "name" not in key_value_filters:
    #         try:
    #             stmt = select(self.model).options(
    #                 joinedload(self.model.categories)
    #             ).order_by(
    #                 *[desc(value) for value in order_by_filters["desc"]],
    #                 *[value for value in order_by_filters["asc"]]
    #             ).offset(page * limit).limit(limit)
    #         except AttributeError:
    #             raise FilterAttributeError
    #
    #     else:
    #         stmt = select(self.model).options(
    #             joinedload(self.model.categories)
    #         ).offset(page * limit).limit(limit)
    #
    #     try:
    #         books = (await session.scalars(stmt)).all()
    #         return list(books)
    #     except (StatementError, InvalidRequestError) as e:
    #         logging.error("Error while trying to perform request to db:", exc_info=True)
    #         raise ServerError("Unexpected server error")

    async def get_all_books(
            self,
            session: AsyncSession,
            filters: BookFilter,
            page: int = 0,
            limit: int = 10,
    ):
        stmt = select(Book).select_from(Book).join(BookCategoryAssoc).join(Category)
        stmt = filters.filter(stmt)
        print("STATEMENT: ", stmt)
        books = (await session.scalars(stmt)).all()
        print("BOOKS", books)
