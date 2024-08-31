from uuid import UUID

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from application.services.utils.filters import Pagination
from core import OrmEntityRepository
from core.base_repos import OrmEntityRepoInterface
from application import User
from application.schemas.order_schemas import (
    UpdatePartiallyOrderS
)
from application.models import Order, Book, BookOrderAssoc
from typing import Protocol, Union, TypeAlias
from core.exceptions import NotFoundError, DBError

__all__ = (
    "CombinedOrderRepositoryInterface",
    "OrderRepository",
)


class OrderRepositoryInterface(Protocol):
    async def get_all_orders(
            self,
            session: AsyncSession,
            page: int,
            limit: int,
    ) -> list[Order]:
        ...

    async def get_orders_by_user_id(
            self,
            session: AsyncSession,
            user_id: int
    ) -> list[BookOrderAssoc]:
        ...

    async def get_order_by_id(
            self,
            session: AsyncSession,
            order_id: int
    ) -> list[BookOrderAssoc]:
        ...

    async def get_order_with_order_details(
            self,
            session: AsyncSession,
            order_id: int,
    ) -> Order:
        ...

    async def delete_book_from_order_by_id(
            self,
            session:AsyncSession,
            book_id: UUID,
            order_id: int
    ):
        ...

    async def update_order(
            self,
            session: AsyncSession,
            order_id: int,
            data: UpdatePartiallyOrderS,
    ):
        ...


CombinedOrderRepositoryInterface = Union[OrderRepositoryInterface, OrmEntityRepoInterface]

OrderId: TypeAlias = str
books_data: TypeAlias = str


class OrderRepository(OrmEntityRepository):
    model: Order = Order

    async def get_all_orders(
            self,
            session: AsyncSession,
            pagination: Pagination
    ) -> list[Order]:
        stmt = select(Order).options(
            selectinload(Order.user).load_only(User.first_name, User.last_name, User.email)
        ).offset(pagination.page * pagination.limit).limit(pagination.limit)

        orders: list[Order] = list(await session.scalars(stmt))

        return orders

    async def get_orders_by_user_id(
            self,
            session: AsyncSession,
            user_id: int
    ) -> list[BookOrderAssoc]:
        stmt = select(BookOrderAssoc).join_from(
           BookOrderAssoc, Order,
           BookOrderAssoc.order_id == Order.id
        ).options(
            selectinload(BookOrderAssoc.book),
            selectinload(BookOrderAssoc.book).selectinload(Book.categories),
            selectinload(BookOrderAssoc.book).selectinload(Book.authors),
        ).where(Order.user_id == user_id)

        try:
            order_res = list(await session.scalars(stmt))
            if not order_res:
                raise NotFoundError(entity="Order")
            return order_res
        except SQLAlchemyError as e:
            raise DBError(traceback=str(e))

    async def get_by_id(
            self,
            session: AsyncSession,
            id: int
    ) -> list[BookOrderAssoc]:
        stmt = select(BookOrderAssoc).join_from(
            BookOrderAssoc, Order,
            BookOrderAssoc.order_id == Order.id
        ).options(
            selectinload(BookOrderAssoc.book),
            selectinload(BookOrderAssoc.order),
            selectinload(BookOrderAssoc.book).selectinload(Book.categories),
            selectinload(BookOrderAssoc.book).selectinload(Book.authors),
        ).where(BookOrderAssoc.order_id == id)

        try:
            order_res = list(await session.scalars(stmt))
            if not order_res:
                raise NotFoundError(entity="Order")
            return order_res
        except SQLAlchemyError as e:
            raise DBError(traceback=str(e))

    async def delete_book_from_order_by_id(
            self,
            session: AsyncSession,
            book_id: UUID,
            order_id: int
    ):
        stmt = delete(BookOrderAssoc).where(
            and_(
                BookOrderAssoc.book_id == str(book_id),
                BookOrderAssoc.order_id == order_id
            )
        )
        try:
            await session.execute(stmt)
            await session.commit()
        except SQLAlchemyError as e:
            raise DBError(traceback=str(e))

    async def get_order_with_order_details(
            self,
            session: AsyncSession,
            order_id: int,
    ) -> Order:
        stmt = select(Order, BookOrderAssoc).join_from(
            Order, BookOrderAssoc, Order.id == BookOrderAssoc.order_id
        ).where(
            and_(
                Order.id == order_id,
                order_id == BookOrderAssoc.order_id
            ),
        ).options(
            selectinload(BookOrderAssoc.order),
            selectinload(BookOrderAssoc.book)
        )
        try:
            order: Order = (await session.scalars(stmt)).one_or_none()
            return order
        except SQLAlchemyError as e:
            raise DBError(traceback=str(e))


