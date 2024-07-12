from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core import OrmEntityRepository
from core.base_repos import OrmEntityRepoInterface
from main import User
from main.schemas.order_schemas import (
    ReturnOrderS,
    ShortenedReturnOrderS, UpdatePartiallyOrderS
)
from main.models import Order, Book, BookOrderAssoc
from typing import Protocol, Union, TypeAlias
from core.exceptions import EntityDoesNotExist

__all__ = (
    "CombinedOrderRepositoryInterface",
)


class OrderRepositoryInterface(Protocol):
    async def get_all_orders(self, session: AsyncSession, page: int, limit: int ) -> list[ShortenedReturnOrderS]:
        ...

    async def get_orders_by_user_id(self, session: AsyncSession, user_id: int):
        ...

    async def get_order_by_id(
            self,
            session: AsyncSession,
            order_id: int
    ) -> Order:
        ...

    async def get_order_with_books_by_id_with_order_details(
            self,
            session: AsyncSession,
            order_id: int,
            book_id: str
    ) -> Order:
        ...

    async def get_order_with_order_details(
            self,
            session: AsyncSession,
            order_id: int,
    ) -> Order:
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

    async def get_all_orders(self, session: AsyncSession, page: int, limit: int):
        stmt = select(Order).options(
            selectinload(Order.user).load_only(User.first_name, User.last_name, User.email)
        ).offset(page * limit).limit(limit)
        orders = await session.scalars(stmt)

        res: list[ShortenedReturnOrderS] = []
        for order in orders:
            res.append(
                ShortenedReturnOrderS(
                    owner_name=" ".join([order.user.first_name, order.user.last_name]),
                    owner_email=order.user.email,
                    order_id=order.id,
                    order_status=order.order_status,
                    total_sum=order.total_sum,
                    order_date=order.order_date
                )
            )
        return res

    async def get_orders_by_user_id(
            self,
            session: AsyncSession,
            user_id: int
    ) -> list[BookOrderAssoc]:
        stmt = select(BookOrderAssoc).join(BookOrderAssoc.order).options(
            selectinload(BookOrderAssoc.book).selectinload(Book.authors)) \
            .options(selectinload(BookOrderAssoc.order)).where(Order.user_id == user_id)

        books_and_orders = (await session.scalars(stmt)).all()
        return list(books_and_orders)

    async def get_order_by_id(
            self,
            session: AsyncSession,
            order_id: int
    ) -> ReturnOrderS:
        stmt = select(Order) \
            .options(
            selectinload(Order.order_details)
            .joinedload(BookOrderAssoc.book)
            .joinedload(Book.authors)).where(
            and_(Order.id == order_id, BookOrderAssoc.order_id == order_id)
        )

        order_res = (await session.scalars(stmt)).one_or_none()
        return order_res


    async def get_order_with_books_by_id_with_order_details(
            self,
            session: AsyncSession,
            order_id: int,
            book_id: str
    ) -> Order:
        stmt = select(Order).options(
            selectinload(Order.order_details)
        ).options(selectinload(Order.order_details).joinedload(BookOrderAssoc.book)
                  ).where(
            or_(and_(BookOrderAssoc.order_id == order_id, BookOrderAssoc.book_id == book_id), Order.id == order_id))

        try:
            order: Order | [] = (await session.scalars(stmt)).all()[0]
        except IndexError:
            raise EntityDoesNotExist(entity="Order")
        return order

    async def get_order_with_order_details(
            self,
            session: AsyncSession,
            order_id: int,
    ) -> Order:
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.order_details))
        order: Order = (await session.scalars(stmt)).one_or_none()
        return order

    async def update(
            self,
            data: dict,
            instance_id: str | int,
            session: AsyncSession
    ) -> None:
        return await super().update(
            session=session,
            data=data,
            instance_id=int(instance_id),
        )