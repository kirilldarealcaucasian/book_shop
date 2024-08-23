import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from application.models import CartItem
from application.repositories import CartRepository, ShoppingSessionRepository
from application.repositories.book_repo import CombinedBookRepoInterface, BookRepository
from application.repositories.cart_repo import CombinedCartRepositoryInterface
from application.repositories.shopping_session_repo import CombinedShoppingSessionRepositoryInterface
from application.schemas import AddBookToCartS, ReturnCartS, ShoppingSessionIdS
from application.services import UserService
from application.services.utils import cart_assembler
from core import EntityBaseService
from typing import Annotated
from application.schemas.domain_model_schemas import CartItemS

from uuid import UUID

from core.base_repos import OrmEntityRepoInterface
from core.exceptions import NotFoundError, EntityDoesNotExist, DBError, ServerError
from logger import logger


class CartService(EntityBaseService):

    def __init__(
        self,
        cart_repo: Annotated[
            CombinedCartRepositoryInterface, Depends(CartRepository)
        ],
        book_repo: Annotated[CombinedBookRepoInterface, Depends(BookRepository)],
        shopping_session_repo: Annotated[
                CombinedShoppingSessionRepositoryInterface, Depends(ShoppingSessionRepository)
        ],
        user_service: UserService = Depends()
    ):
        self.book_repo = book_repo
        self.shopping_session_repo = shopping_session_repo
        self.user_service = user_service
        self.cart_repo: CombinedCartRepositoryInterface = cart_repo
        super().__init__(cart_repo=cart_repo)

    async def get_cart_by_session_id(
        self,
        session: AsyncSession,
        cart_session_id: UUID
    ) -> ReturnCartS:
        """retrieves books in a cart and cart session_id"""
        cart: list[CartItem] = []

        try:
            cart: list[CartItem] = await self.cart_repo.get_cart_by_session_id(
                session=session,
                cart_session_id=cart_session_id,
            )
        except (NotFoundError, DBError) as e:
            if type(e) == NotFoundError:
                logger.info(f"{e.entity} not found", exc_info=True)
                raise EntityDoesNotExist(e.entity)
            elif type(e) == DBError:
                logger.error(f"DB error", exc_info=True)
                raise ServerError()

        assembled_cart: ReturnCartS = cart_assembler(cart)

        return assembled_cart

    async def get_cart_by_user_id(
        self,
        session: AsyncSession,
        user_id: int | str
    ) -> ReturnCartS:
        cart: list[CartItem] = []

        user = await self.user_service.get_user_by_id(session=session, id=user_id)

        try:
            cart: list[CartItem] = await self.cart_repo.get_cart_by_user_id(
                session=session,
                user_id=user_id
            )
        except (NotFoundError, DBError) as e:
            if type(e) == NotFoundError:
                raise EntityDoesNotExist("Cart")
            elif type(e) == DBError:
                raise ServerError()
        assembled_cart: ReturnCartS = cart_assembler(cart)

        return assembled_cart

    async def create_cart(
        self,
        session: AsyncSession,
    ) -> ShoppingSessionIdS:
        session_id: uuid.UUID = uuid.uuid4()
        domain_model = CartItemS(session_id=session_id)

        session_id: UUID = await super().create(repo=self.cart_repo, session=session, domain_model=domain_model)

        return ShoppingSessionIdS(
            session_id=session_id
        )

    async def delete_cart(
        self,
        session: AsyncSession,
        cart_session_id: UUID,
    ) -> None:
        _ = await super().delete(
            repo=self.cart_repo,
            session=session,
            instance_id=cart_session_id
        )

    async def add_book_to_cart(
            self,
            session: AsyncSession,
            session_id: UUID,
            dto: AddBookToCartS,
    ):
        domain_model = CartItemS(**dto.model_dump(exclude_none=True))

        _ = await super().get_by_id(
            session=session, repo=self.book_repo, id=dto.book_id
        )  # if not exists, exception will be raised

        _ = await super().get_by_id(
            session=session, repo=self.shopping_session_repo, id=dto.book_id
        )  # if not exists, exception will be raised

        await super().create(
            session=session,
            repo=self.cart_repo,
            domain_model=domain_model
        )

        return await self.get_cart_by_session_id(
            session=session,
            cart_session_id=session_id
        )

    async def delete_book_from_cart(
            self,
            session: AsyncSession,
            book_id: UUID,
            cart_session_id: UUID

    ):
        _ = await super().get_by_id(
            session=session, repo=self.book_repo, id=book_id
        )  # if not exists, exception will be raised

        _ = await super().get_by_id(
            session=session, repo=self.shopping_session_repo, id=cart_session_id
        )  # if not exists, exception will be raised

        try:
            _ = await self.cart_repo.delete_cart_by_shopping_session_id(
                session=session,
                shopping_session_id=cart_session_id
            )
        except SQLAlchemyError as e:
            extra = {"book_id": book_id, "cart_session_id": cart_session_id}
            logger.error(
                f"failed to delete book from cart",
                extra=extra,
                exc_info=True
            )
            raise DBError("Something went wrong")
