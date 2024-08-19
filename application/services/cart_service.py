import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
# from application import CreateBookS
from application.models import CartItem
from application.repositories import CartRepository
from application.repositories.cart_repo import CombinedOrderRepositoryInterface
from application.schemas import AddBookToCartS, ReturnCartS, ReturnBookS, ShoppingSessionIdS
from application.schemas.order_schemas import AssocBookS
from application.services import UserService
from application.services.utils import cart_assembler
from core import EntityBaseService
# from core.exceptions import DomainModelConversionError
from typing import Annotated
from application.schemas.domain_model_schemas import CartItemS, BookS
# from pydantic import ValidationError, PydanticSchemaGenerationError
# from logger import logger
from uuid import UUID

from core.exceptions import NotFoundError, EntityDoesNotExist, DBError, ServerError
from logger import logger


class CartService(EntityBaseService):
    model_name = "Cart"

    def __init__(
        self,
        cart_repo: Annotated[
            CombinedOrderRepositoryInterface, Depends(CartRepository)
        ],
        user_service: UserService = Depends()
    ):
        self.user_service = user_service
        self.cart_repo: CombinedOrderRepositoryInterface = cart_repo
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
                logger.error(f"{self.model_name} not found", exc_info=True)
                raise EntityDoesNotExist(self.model_name)
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
        return session_id

    async def delete_cart(
        self,
        session: AsyncSession,
        cart_session_id: UUID,
    ) -> None:
        cart = await self.get_cart_by_session_id(
            session=session,
            cart_session_id=cart_session_id
        )
        cart_session_id: str = str(cart_session_id)
        _ = await super().delete(
            repo=self.cart_repo, session=session, instance_id=cart_session_id
        )

    async def add_book_to_cart(
            self,
            session: AsyncSession,
            session_id: UUID,
            dto: AddBookToCartS,
    ):
        pass
        # session_id: str = str(session_id)
        # cart: CartItem = (await self.get_cart_by_session_id(
        #     session=session,
        #     cart_session_id=session_id
        # ))[0]
        # CartItem.book
        # pass

    async def delete_book_from_cart(
            self,
            session: AsyncSession,
            book_id: UUID,
            cart_session_id: UUID

    ):
    # ) -> ReturnCartS:
        pass
