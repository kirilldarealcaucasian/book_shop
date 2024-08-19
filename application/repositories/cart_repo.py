# from sqlalchemy import select, delete, and_
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
# from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from application import Book
from application.models import CartItem, ShoppingSession, BookCategoryAssoc
from core import OrmEntityRepository
from core.base_repos import OrmEntityRepoInterface
from typing import Protocol, Union
from application.schemas.domain_model_schemas import CartItemS, BookS
from core.exceptions import NotFoundError, DBError
from logger import logger


# from core.exceptions import DeletionError, DBError
# from logger import logger


class CartRepositoryInterface(Protocol):
    async def get_cart_by_session_id(
            self,
            session: AsyncSession,
            cart_session_id: UUID
    ) -> list[CartItem]:
        ...

    async def get_cart_by_user_id(
            self,
            session: AsyncSession,
            user_id: int | str,
    ) -> list[CartItem]:
        ...

    async def add_book_to_cart_by_session_id(
            self,
            session_id: str,
            domain_model: BookS
    ) -> None:
        ...

    async def delete_book_from_cart_by_session_id(
            self,
            session_id: str,
            domain_model: BookS
    ):
        ...


CombinedOrderRepositoryInterface = Union[CartRepositoryInterface, OrmEntityRepoInterface]


class CartRepository(OrmEntityRepository):
    model: CartItem = CartItem

    async def get_cart_by_session_id(
            self,
            session: AsyncSession,
            cart_session_id: UUID
    ) -> list[CartItem]:

        # load Cart with books
        stmt = select(CartItem).options(
            selectinload(CartItem.book).selectinload(Book.authors),
            selectinload(CartItem.shopping_session),
            selectinload(CartItem.book).selectinload(Book.categories),
        ).where(ShoppingSession.id == cart_session_id)

        try:
            cart = (await session.scalars(stmt)).all()
        except SQLAlchemyError as e:
            raise DBError(str(e))

        if not cart:
            raise NotFoundError()

        return list(cart)

    async def get_cart_by_user_id(
            self,
            session: AsyncSession,
            user_id: int
    ) -> list[CartItem]:
        stmt = select(CartItem).options(
            selectinload(CartItem.book).selectinload(Book.authors),
            selectinload(CartItem.shopping_session),
            selectinload(CartItem.book).selectinload(Book.categories),
        ).where(ShoppingSession.user_id == user_id)

        try:
            cart = (await session.scalars(stmt)).all()
        except SQLAlchemyError as e:
            logger.error("query error: failed to perform select query", exc_info=True)
            raise DBError(str(e))

        if not cart:
            raise NotFoundError()

        return list(cart)

    async def add_book_to_cart_by_session_id(
            self,
            session: AsyncSession,
            session_id: str,
            domain_model: BookS
    ) -> None:
        # stmt = insert(self.model)\
        #     .where(self.model.session_id == session_id)\
        #     .values(domain_model.model_dump())
        pass
        # _ = await session.execute(stmt)
        # await super().commit(session)

    async def delete_book_from_cart_by_session_id(
            self,
            session: AsyncSession,
            session_id: str,
            book_id: str,
    ) -> None:
        pass
        # cart = self.get_cart_by_session_id(session=session)
        # stmt = delete().where(
        #     and_(self.model.session_id == session_id, self.model.book_id == book_id))
        #
        # res = None
        #
        # try:
        #     res = await session.excute(stmt)
        # except IntegrityError:
        #     extra = {"session_id": session, "book_id": book_id}
        #     logger.error(
        #         f"Integrity deletion error: Error while deleting book from {self.model} due to Integrity error",
        #         extra,
        #         exc_info=True
        #     )
        #     raise DBError(f"Failed to delete a book from {self.model}")
        #
        # await super().commit(session)
        #
        # if res and res.rowcount == 0:
        #     extra = {"session_id": session, "book_id": book_id}
        #     logger.error(
        #         f"Deletion error: Error while deleting book from {self.model}",
        #         extra,
        #         exc_info=True
        #     )
        #     raise DeletionError(entity="Book", info="Book to delete wasn't found")
        
