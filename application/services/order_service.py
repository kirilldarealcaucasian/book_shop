from collections import defaultdict
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from core.exceptions import EntityDoesNotExist, InvalidModelCredentials
from application import Book
from application.helpers.uuid_helpers import is_valid_uuid
from application.models import Order, BookOrderAssoc
from application.repositories.order_repo import CombinedOrderRepositoryInterface
from application.schemas import (
    ReturnOrderS,
    CreateOrderS,
    BookSummaryS,
    OrderSummaryS,
    ReturnUserS,
    ShortenedReturnOrderS,
    ReturnUserWithOrdersS,
    UpdatePartiallyOrderS,
)

from application.repositories import (
    OrderRepository,
    BookRepository,
)
from application.schemas.filters import PaginationS
from application.schemas.order_schemas import AssocBookS
from application.services.user_service import UserService
from application.services.book_service import BookService
from application.tasks import send_order_summary_email
from typing import Annotated, TypeAlias
from logger import logger


OrderId: TypeAlias = str
books_data: TypeAlias = str


class OrderService(EntityBaseService):
    def __init__(
        self,
        order_repo: Annotated[
            CombinedOrderRepositoryInterface, Depends(OrderRepository)
        ],
        book_repo: Annotated[OrmEntityRepoInterface, Depends(BookRepository)],
        book_service: BookService = Depends(),
        user_service: UserService = Depends(),
    ):
        super().__init__(order_repo=order_repo, book_repo=book_repo)
        self.order_repo = order_repo
        self.book_repo = book_repo
        self.user_service = user_service
        self.book_service = book_service

    async def create_order(
        self, session: AsyncSession, data: CreateOrderS
    ) -> None:
        _ = await self.user_service.get_user_by_id(
            session=session, id=data.user_id
        )  # if no exception was raised

        return await super().create(
            repo=self.order_repo, session=session, dto=data
        )

    async def get_all_orders(
        self, session: AsyncSession, pagination: PaginationS
    ) -> list[ShortenedReturnOrderS]:
        return await self.order_repo.get_all_orders(
            session=session,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get_order_by_id(
        self, session: AsyncSession, order_id: int
    ) -> ReturnOrderS:
        order_res: Order = await self.order_repo.get_order_by_id(
            session=session, order_id=order_id
        )

        if not order_res:
            return ReturnOrderS(order_id=order_id, books=[])

        order_details: list[BookOrderAssoc] = order_res.order_details

        order_books: list[
            AssocBookS
        ] = []  # stores all books contained in the order

        for order_detail in order_details:
            if order_detail.order_id == order_id:
                book = order_detail.book

                authors: list[str] = [
                    " ".join([author.first_name, author.last_name])
                    for author in book.authors
                ]  # concat authors' first and last name

                order_books.append(
                    AssocBookS(
                        book_title=book.name,
                        authors=authors,
                        genre_name=book.genre_name,
                        rating=book.rating,
                        discount=book.discount,
                        count_ordered=order_detail.count_ordered,
                        price_per_unit=book.price_per_unit,
                    )
                )

        return ReturnOrderS(order_id=order_id, books=order_books)

    async def get_user_orders(self, session: AsyncSession, user_id: int):
        books_and_orders: list[
            BookOrderAssoc
        ] = await self.order_repo.get_orders_by_user_id(
            session=session,
            user_id=user_id,
        )

        try:
            user: ReturnUserS = (await self.user_service.get_user_by_id(
                session=session, id=user_id)
            )[0]
        except IndexError:
            raise EntityDoesNotExist("User")


        books_metadata: dict[OrderId:int, books_data : list[AssocBookS]] = (
            defaultdict(list)
        )  # stores books and order ids in which books are contained

        for detail in books_and_orders:
            book = detail.book
            authors = []

            for author in book.authors:
                authors.append(" ".join([author.first_name, author.last_name]))

            books_metadata[detail.order_id].append(
                AssocBookS(
                    book_title=book.name,
                    authors=authors,
                    genre_name=book.genre_name,
                    rating=book.rating,
                    discount=book.discount,
                    price_per_unit=book.price_per_unit,
                    count_ordered=detail.count_ordered,
                )
            )

        orders: list[ReturnOrderS] = [
            ReturnOrderS(order_id=order_id, books=books)
            for order_id, books in books_metadata.items()
        ]

        return ReturnUserWithOrdersS(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            orders=orders,
        )

    async def delete_order(self, session: AsyncSession, order_id: str | int):
        return await super().delete(
            repo=self.order_repo, session=session, instance_id=order_id
        )

    async def update_order(
        self,
        session: AsyncSession,
        order_id: int | str,
        data: UpdatePartiallyOrderS,
    ):
        return await super().update(
            repo=self.order_repo,
            session=session,
            instance_id=order_id,
            dto=data,
        )

    async def add_book_to_order(
        self,
        session: AsyncSession,
        book_id: str | int,
        order_id: int,
        quantity: int,
    ) -> None:
        if not is_valid_uuid(book_id):
            raise InvalidModelCredentials(message="Invalid id format for book")

        order: Order = await self.order_repo.get_order_with_books_by_id_with_order_details(
            session=session, order_id=order_id, book_id=book_id
        )

        book: Book = await self.book_repo.get_all(session=session, id=book_id)

        if quantity > book.number_in_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"""You're trying to order too many books, only {book.number_in_stock} left in stock""",
            )

        for book_in_order in order.order_details:
            # Firstly, check if the book already in the order
            if (
                book_in_order.book_id == book.id
                and book_in_order.order_id == order.id
            ):
                # if it is, change respective params for the book in the order
                book_in_order.count_ordered += quantity
                order.total_sum += book.price_with_discount * quantity
                book.number_in_stock -= quantity
                await session.commit()
                return

        # if the book was not found in the order, then we add a new record
        order.order_details.append(
            BookOrderAssoc(
                book_id=book_id, order_id=order_id, count_ordered=quantity
            )
        )
        order.total_sum = (
            book.price_with_discount * quantity
        )  # set initial total sum
        book.number_in_stock = book.number_in_stock - quantity
        await self.order_repo.commit(session=session)

    async def delete_book_from_order(
        self,
        session: AsyncSession,
        book_id: str | int,
        order_id: int,
    ) -> None:
        if not is_valid_uuid(book_id):
            raise InvalidModelCredentials(message="Invalid id format for book")

        order: (
            Order | None
        ) = await self.order_repo.get_order_with_order_details(
            session=session,
            order_id=order_id,
        )

        if not order:
            raise EntityDoesNotExist(entity="Order")

        for book in order.order_details:
            if str(book.book_id) == book_id and order_id == book.order_id:
                try:
                    order.order_details.remove(book)
                    await session.commit()
                    return
                except IntegrityError as e:
                    extra = {"book_id": book_id, "order_id": order_id}
                    logger.error(
                        f"Book deletion error: Unable to delete book from the order: {e}",
                        extra=extra,
                        exc_info=True,
                    )

        raise EntityDoesNotExist("Book")

    async def make_order(
        self,
        session: AsyncSession,
        order_id: int,
    ):
        user: ReturnUserS = await self.user_service.get_user_by_order_id(
            session=session, order_id=order_id
        )
        user_with_orders: ReturnUserWithOrdersS = (
            await self.user_service.get_user_with_orders(
                session=session, user_id=user.id
            )
        )
        order_books: list[BookSummaryS] = []

        for order in user_with_orders.orders:
            if order.order_id == order_id:
                for book in order.books:
                    total_price = book.count_ordered * book.price_per_unit
                    book_summary = BookSummaryS(
                        name=book.name,
                        count_ordered=book.count_ordered,
                        total_price=total_price,
                    )
                    order_books.append(book_summary)
                break

        data = OrderSummaryS(
            username=user.name, email=user.email, books=order_books
        ).model_dump()

        send_order_summary_email.delay(
            order_data=data,
        )
