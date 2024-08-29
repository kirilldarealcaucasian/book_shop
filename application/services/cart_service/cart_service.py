from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from application import Book
from application.models import CartItem
from application.repositories import CartRepository, ShoppingSessionRepository
from application.repositories.book_repo import CombinedBookRepoInterface, BookRepository
from application.repositories.cart_repo import CombinedCartRepositoryInterface
from application.repositories.shopping_session_repo import CombinedShoppingSessionRepositoryInterface
from application.schemas import AddBookToCartS, ReturnCartS, ShoppingSessionIdS, CreateShoppingSessionS
from application.services import UserService, ShoppingSessionService, BookService
from application.services.cart_service import store_cart_to_cache
from application.services.cart_service.utils import \
    (
    cart_assembler,
)

from auth.helpers import get_token_payload
from core import EntityBaseService
from typing import Annotated, Union
from application.schemas.domain_model_schemas import CartItemS

from uuid import UUID as uuid_UUID

from core.config import settings
from core.exceptions import NotFoundError, EntityDoesNotExist, DBError, ServerError, AlreadyExistsError, \
    OutOfStockQuantity
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
            shopping_session_service: ShoppingSessionService = Depends(),
            user_service: UserService = Depends(),
            book_service: BookService = Depends(),

    ):
        self.book_repo = book_repo
        self.shopping_session_repo = shopping_session_repo
        self.cart_repo: CombinedCartRepositoryInterface = cart_repo
        super().__init__(cart_repo=cart_repo)
        self.shopping_session_service = shopping_session_service
        self.user_service = user_service
        self.book_service = book_service

    @store_cart_to_cache(cache_time_seconds=10)
    async def get_cart_by_session_id(
            self,
            session: AsyncSession,
            shopping_session_id: uuid_UUID | None,
    ) -> ReturnCartS:
        """retrieves books in a cart and cart session_id"""
        cart: list[CartItem] = []
        try:
            cart: list[CartItem] = await self.cart_repo.get_cart_by_session_id(
                session=session,
                cart_session_id=shopping_session_id,
            )
        except (NotFoundError, DBError) as e:
            if type(e) == NotFoundError:
                logger.info(f"{e.entity} not found", exc_info=True)
                raise EntityDoesNotExist(e.entity)
            elif type(e) == DBError:
                logger.error("DB error", exc_info=True)
                raise ServerError()

        assembled_cart: ReturnCartS = cart_assembler(cart)  # converts data into ReturnCartS

        return assembled_cart

    @store_cart_to_cache(cache_time_seconds=10)
    async def get_cart_by_user_id(
            self,
            session: AsyncSession,
            user_id: int | str
    ) -> ReturnCartS:
        cart: list[CartItem] = []
        _ = await self.user_service.get_user_by_id(session=session, id=user_id)

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
            credentials: HTTPAuthorizationCredentials | None
    ) -> JSONResponse:
        """Cart is associated with a shopping_session_id.
        This method creates a shopping_session and stores it to the cookie"""

        user_id: Union[int, None] = None

        if credentials:
            token_payload: dict = get_token_payload(
                credentials=credentials
            )
            user_id = token_payload["user_id"]
            try:
                cart = await self.get_cart_by_user_id(
                    session=session,
                    user_id=user_id
                )
                if cart:
                    raise AlreadyExistsError(
                        entity="Cart",
                    )
            except EntityDoesNotExist:
                # it is okay if there is no cart for a user
                pass

        shopping_session_id: ShoppingSessionIdS = await self.shopping_session_service.create_shopping_session(
            session=session,
            dto=CreateShoppingSessionS(
                user_id=user_id,
                total=0.0
            )
        )

        shopping_session = await self.shopping_session_service.get_shopping_session_by_id(
            session=session,
            id=shopping_session_id.session_id
        )

        response = JSONResponse(
            content={"status": "success"},
            status_code=201
        )

        response.set_cookie(
            key=settings.SHOPPING_SESSION_COOKIE_NAME,
            value=str(shopping_session.id),
            expires=shopping_session.expiration_time,
            httponly=True,
            secure=True
        )

        return response

    async def delete_cart(
            self,
            session: AsyncSession,
            cart_session_id: uuid_UUID,
    ) -> None:
        _ = await super().delete(
            repo=self.cart_repo,
            session=session,
            instance_id=cart_session_id
        )

    async def add_book_to_cart(
            self,
            session: AsyncSession,
            session_id: uuid_UUID,
            dto: AddBookToCartS,
    ) -> ReturnCartS:
        """Adds a book to the cart / increments amount of ordered books"""
        domain_model = CartItemS(**dto.model_dump(exclude_none=True), session_id=session_id)

        _ = await self.book_service.get_book_by_id(
            session=session,
            id=dto.book_id
        )  # if not exists, exception will be raised

        cart: list[CartItem] = await self.cart_repo.get_cart_by_session_id(
            session=session,
            cart_session_id=session_id
        )

        for cart_item in cart:
            """check if book already in teh cart, if it is, then increment amount"""
            book: Book = cart_item.book
            if str(cart_item.book_id) == str(domain_model.book_id):

                if book.number_in_stock - domain_model.quantity >= 0:
                    cart_item.quantity += domain_model.quantity
                    book.number_in_stock -= cart_item.quantity
                    await super().commit(session=session)

                    cart: ReturnCartS = await self.get_cart_by_session_id(
                        session=session,
                        shopping_session_id=session_id
                    )

                    return cart
                else:
                    raise OutOfStockQuantity(
                        f"Only {book.number_in_stock} books left in stock"
                    )

        await super().create(
            session=session,
            repo=self.cart_repo,
            domain_model=domain_model
        )

        cart: ReturnCartS = await self.get_cart_by_session_id(
            session=session,
            shopping_session_id=session_id
        )

        return cart

    async def delete_book_from_cart(
            self,
            session: AsyncSession,
            book_id: uuid_UUID,
            shopping_session_id: uuid_UUID

    ) -> ReturnCartS:

        _ = await self.book_service.get_book_by_id(
            session=session,
            id=book_id
        )  # if not exists, exception will be raised

        try:
            _ = await self.cart_repo.delete_book_from_cart_by_session_id(
                session=session,
                session_id=shopping_session_id,
                book_id=book_id
            )

        except DBError:
            extra = {"session_id": session, "book_id": book_id}
            logger.error(
                "Deletion error: Error while deleting book from cart",
                extra,
                exc_info=True
            )
            raise ServerError(
                detail="Something went wrong. Failed to delete book from cart."
            )
        except NotFoundError:
            extra = {"session_id": session, "book_id": book_id}
            logger.debug(
                "Book that was tried to bed deleted from the cart wasn't found",
                extra,
                exc_info=True
            )
            raise EntityDoesNotExist(entity="Book")

        cart: ReturnCartS = await self.get_cart_by_session_id(
            session=session,
            shopping_session_id=shopping_session_id
        )

        return cart
