# from collections import defaultdict
# from fastapi import Depends, UploadFile, File, HTTPException, status
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.ext.asyncio import AsyncSession
# from core import EntityBaseService
# from core.base_repos import OrmEntityRepoInterface
# from core.exceptions import RelatedEntityDoesNotExist, EntityDoesNotExist, InvalidModelCredentials
# from main import CreateBookS, Book
# from main.helpers.uuid_helpers import is_valid_uuid
# from main.models import Order, BookOrderAssoc
# from main.repositories.order_repo import CombinedOrderRepositoryInterface
# from main.schemas import (
#     ReturnImageS,
#     ReturnOrderS,
#     CreateOrderS, BookSummaryS, OrderSummaryS,
#     ReturnUserS, CreateImageS, CreateAuthorS,
#     ReturnBookS, CreatePublisherS, ReturnAuthorS, UpdateAuthorS,
#     UpdatePartiallyAuthorS, UpdateBookS, UpdatePartiallyBookS, ReturnPublisherS, UpdateUserS,
#     UpdatePartiallyUserS, ShortenedReturnOrderS, ReturnUserWithOrdersS, UpdatePartiallyOrderS, BookFilterS
# )
#
# from main.repositories import (
#     OrderRepository,
#     UserRepository,
#     OrmEntityUserInterface,
#     BookRepository,
#     AuthorRepository,
#     PublisherRepository,
#     ImageRepository
# )
# from main.schemas.filters import PaginationS
# from main.schemas.order_schemas import AssocBookS
# from main.services.facade_sublayer.storage_facade.storage_interface import StorageInterface
# from main.tasks import send_order_summary_email
# from main.services.facade_sublayer.storage_facade.internal_storage import InternalStorage
# from typing import Annotated, Literal, TypeAlias
# from logger import logger
#
# __all__ = (
#     "ImageService",
#     "OrderService",
#     "UserService",
#     "BookService",
# )
#
#
# class BookService(EntityBaseService):
#     def __init__(
#             self,
#             storage: Annotated[StorageInterface, Depends(InternalStorage)],
#             book_repo: Annotated[OrmEntityRepoInterface, Depends(BookRepository)],
#             image_repo: Annotated[OrmEntityRepoInterface, Depends(ImageRepository)],
#     ):
#         self.book_repo = book_repo
#         self.image_repo = image_repo
#         super().__init__(book_repo=book_repo, image_repo=image_repo)
#         self.storage: StorageInterface = storage
#
#     async def get_books_by_filters(self, session: AsyncSession, **filters) -> list[ReturnBookS]:
#         return await super().get_all(repo=self.book_repo, session=session, **filters)
#
#     async def get_all_books(self, session: AsyncSession, filters: BookFilterS) -> list[ReturnBookS]:
#         key_value_filters = {}
#         if filters.filterby:
#             key_value_filters: dict = {
#                 subrow.split("=")[0]: subrow.split("=")[1]
#                 for subrow in (
#                     row for row in filters.filterby.split(",")
#                 )
#             }  # example: title="book1",genre="genre2" -> {"title": "book1", "genre": "genre2}"
#
#         order_by_filters: dict[Literal["asc", "desc"], list[str]] = defaultdict(list)
#         if filters.order_by:
#             for order_filter in filters.order_by.split(","):
#                 if "-" == order_filter[0]:
#                     order_by_filters["desc"].append(order_filter[1:])
#                 else:
#                     order_by_filters["asc"].append(order_filter)
#
#         return await super().get_all(
#             repo=self.book_repo,
#             session=session,
#             key_value_filters=key_value_filters,
#             order_by_filters=order_by_filters,
#             page=filters.page,
#             limit=filters.limit
#         )
#
#     async def create_book(self, session: AsyncSession, dto: CreateBookS) -> None:
#         return await super().create(repo=self.book_repo, session=session, dto=dto)
#
#     async def delete_book(
#             self,
#             session: AsyncSession,
#             book_id: str,
#     ) -> None:
#         try:
#             _: list[ReturnImageS] = await super().get_all(repo=self.image_repo, session=session, book_id=book_id)
#         except EntityDoesNotExist:
#             return await self.storage.delete_instance_with_images(
#                 delete_images=False,
#                 instance_id=book_id,
#                 session=session
#             )
#         return await self.storage.delete_instance_with_images(
#             delete_images=True,
#             instance_id=book_id,
#             session=session
#         )
#
#     async def update_book(
#             self,
#             session: AsyncSession,
#             book_id: str | int,
#             data: UpdateBookS | UpdatePartiallyBookS
#     ) -> ReturnBookS:
#         return await super().update(
#             repo=self.book_repo,
#             session=session,
#             instance_id=book_id,
#             dto=data
#         )
#
#
# class ImageService(EntityBaseService):
#     def __init__(
#             self,
#             image_repo: Annotated[OrmEntityRepoInterface, Depends(ImageRepository)],
#             storage: Annotated[StorageInterface, Depends(InternalStorage)],
#             book_service: BookService = Depends(),
#     ):
#         super().__init__(repository=image_repo)
#         self.image_repo = image_repo
#         self.book_service = book_service
#         self.storage = storage
#
#     async def get_all_images(
#             self, session: AsyncSession,
#             book_id: str | int
#     ) -> list[ReturnImageS]:
#         return await super().get_all(session=session, repo=self.image_repo, book_id=book_id)
#
#     async def upload_image(
#             self,
#             session: AsyncSession,
#             book_id: str | int,
#             image: UploadFile = File(...)
#     ):
#         book: list[ReturnBookS] | None = await self.book_service.get_books_by_filters(
#             session=session,
#             book_id=book_id
#         )
#
#         if not book:
#             raise RelatedEntityDoesNotExist(entity="Book")
#
#         image_data: CreateImageS = await self.storage.upload_image(
#             image=image,
#             instance_id=book_id
#         )
#
#         if image_data:
#             await super().create(
#                 repo=self.image_repo,
#                 session=session,
#                 dto=image_data
#             )
#
#     async def delete_image(
#             self,
#             session: AsyncSession,
#             image_id: int
#     ) -> None:
#         image: list[ReturnImageS] = await super().get_all(
#             repo=self.image_repo,
#             session=session,
#             id=image_id
#         )
#
#         if not image:
#             raise RelatedEntityDoesNotExist("Image")
#         image_url: str = image[0].url
#
#         if await super().delete(
#                 repo=self.image_repo,
#                 session=session,
#                 instance_id=image[0].id
#         ):
#             await self.storage.delete_image(image_url=image_url, image_id=image_id)
#
#     # async def delete_image(
#     #         self,
#     #         session: AsyncSession,
#     #         image_id: int
#     # ):
#     #     image: list[ReturnImageS] = await self.repository.get_all(session=session, id=image_id)
#     #     image_url: str = image[0].url
#     #     await self.repository.delete(session=session, instance_id=image[0].id)
#     #     try:
#     #         logger.info("Image url: ", image_url)
#     #         image_path = os.path.join(image_url)
#     #         os.remove(image_path)
#     #         return
#     #     except FileNotFoundError:
#     #         extra = {"image_id": image_id, "image_url": image_url}
#     #         logger.error("File deletion Error: Error while trying to delete file", extra, exc_info=True)
#     #         raise HTTPException(
#     #             status_code=status.HTTP_404_NOT_FOUND,
#     #             detail="File you're trying to remove does not exist"
#     #         )
#
#
# class UserService(EntityBaseService):
#     def __init__(
#             self,
#             user_repo: Annotated[OrmEntityUserInterface, Depends(UserRepository)],
#     ):
#         super().__init__(user_repo=user_repo)
#         self.user_repo = user_repo
#
#     async def get_all_users(self, session: AsyncSession, pagination: PaginationS) -> list[ReturnUserS] | ReturnUserS:
#         return await super().get_all(
#             repo=self.user_repo,
#             session=session,
#             page=pagination.page,
#             limit=pagination.limit
#         )
#
#     async def get_users_with_filters(self, session: AsyncSession, **filters) -> list[ReturnUserS] | ReturnUserS:
#         return await super().get_all(repo=self.user_repo, session=session, **filters)
#
#     async def delete_user(self, session: AsyncSession, user_id: str | int) -> None:
#         return await super().delete(repo=self.user_repo, session=session, instance_id=user_id)
#
#     async def update_user(
#             self, session: AsyncSession,
#             user_id: str | int,
#             data: UpdateUserS | UpdatePartiallyUserS
#     ) -> None:
#         return await super().update(
#             repo=self.user_repo,
#             session=session,
#             instance_id=user_id,
#             dto=data
#         )
#
#     async def get_user_with_orders(
#             self,
#             session: AsyncSession,
#             user_id: int
#     ) -> ReturnUserWithOrdersS:
#         return await self.user_repo.get_user_with_orders(
#             session=session,
#             user_id=user_id
#         )
#
#     async def get_user_by_order_id(
#             self,
#             session: AsyncSession,
#             order_id: int,
#     ) -> ReturnUserS:
#         return await self.user_repo.get_user_by_order_id(
#             session=session,
#             order_id=order_id
#         )
#
#
# OrderId: TypeAlias = str
# books_data: TypeAlias = str
#
# class OrderService(EntityBaseService):
#     def __init__(
#             self,
#             order_repo: Annotated[CombinedOrderRepositoryInterface, Depends(OrderRepository)],
#             book_repo: Annotated[OrmEntityRepoInterface, Depends(BookRepository)],
#             book_service: BookService = Depends(),
#             user_service: UserService = Depends(),
#     ):
#         super().__init__(order_repo=order_repo, book_repo=book_repo)
#         self.order_repo = order_repo
#         self.book_repo = book_repo
#         self.user_service = user_service
#         self.book_service = book_service
#
#     async def create_order(
#             self,
#             session: AsyncSession,
#             data: CreateOrderS
#     ) -> None:
#
#         _ = await self.user_service.get_users_with_filters(
#             session=session,
#             id=data.user_id
#         )  # if no exception was raised
#
#         return await super().create(
#             repo=self.order_repo,
#             session=session,
#             dto=data
#         )
#
#     async def get_all_orders(
#             self,
#             session: AsyncSession,
#             pagination: PaginationS
#     ) -> list[ShortenedReturnOrderS]:
#         return await self.order_repo.get_all_orders(
#             session=session,
#             page=pagination.page,
#             limit=pagination.limit,
#         )
#
#     async def get_order_by_id(
#             self,
#             session: AsyncSession,
#             order_id: int
#     ) -> ReturnOrderS:
#
#         order_res: Order = await self.order_repo.get_order_by_id(session=session, order_id=order_id)
#
#         if not order_res:
#             return ReturnOrderS(
#                 order_id=order_id,
#                 books=[]
#             )
#
#         order_details: list[BookOrderAssoc] = order_res.order_details
#
#         order_books: list[AssocBookS] = []  # stores all books contained in the order
#
#         for order_detail in order_details:
#             if order_detail.order_id == order_id:
#                 book = order_detail.book
#
#                 authors: list[str] = [
#                     " ".join(
#                         [author.first_name, author.last_name]
#                     ) for author in book.authors
#                 ]  # concat authors' first and last name
#
#                 order_books.append(
#                     AssocBookS(
#                         book_title=book.name,
#                         authors=authors,
#                         genre_name=book.genre_name,
#                         rating=book.rating,
#                         discount=book.discount,
#                         count_ordered=order_detail.count_ordered,
#                         price_per_unit=book.price_per_unit
#                     ))
#
#         return ReturnOrderS(
#             order_id=order_id,
#             books=order_books
#         )
#
#     async def get_user_orders(
#             self,
#             session: AsyncSession,
#             user_id: int
#     ):
#         books_and_orders: list[BookOrderAssoc] = await self.order_repo.get_orders_by_user_id(
#             session=session,
#             user_id=user_id,
#         )
#
#         user: ReturnUserS = await self.user_service.get_users_with_filters(
#             session=session,
#             id=user_id
#         )
#
#         books_metadata: dict[OrderId:int, books_data:list[AssocBookS]] = defaultdict(
#             list)  # stores books and order ids in which books are contained
#
#         for detail in books_and_orders:
#             book = detail.book
#             authors = []
#
#             for author in book.authors:
#                 authors.append(
#                     " ".join([author.first_name, author.last_name])
#                 )
#
#             books_metadata[detail.order_id].append(
#                 AssocBookS(
#                     book_title=book.name,
#                     authors=authors,
#                     genre_name=book.genre_name,
#                     rating=book.rating,
#                     discount=book.discount,
#                     price_per_unit=book.price_per_unit,
#                     count_ordered=detail.count_ordered
#                 ))
#
#         orders: list[ReturnOrderS] = [ReturnOrderS(order_id=order_id, books=books) for order_id, books in
#                                       books_metadata.items()]
#
#         return ReturnUserWithOrdersS(
#             first_name=user.first_name,
#             last_name=user.last_name,
#             email=user.email,
#             orders=orders
#         )
#
#     async def delete_order(
#             self,
#             session: AsyncSession,
#             order_id: str | int
#     ):
#         return await super().delete(
#             repo=self.order_repo,
#             session=session,
#             instance_id=order_id
#         )
#
#     async def update_order(
#             self,
#             session: AsyncSession,
#             order_id: int | str,
#             data: UpdatePartiallyOrderS
#     ):
#         return await super().update(
#             repo=self.order_repo,
#             session=session,
#             instance_id=order_id,
#             dto=data
#         )
#
#     async def add_book_to_order(
#             self,
#             session: AsyncSession,
#             book_id: str | int,
#             order_id: int,
#             quantity: int
#     ) -> None:
#
#         if not is_valid_uuid(book_id):
#             raise InvalidModelCredentials(
#                 message="Invalid id format for book"
#             )
#
#         order: Order = await self.order_repo.get_order_with_books_by_id_with_order_details(
#             session=session,
#             order_id=order_id,
#             book_id=book_id
#         )
#
#         book: Book = await self.book_repo.get_all(session=session, id=book_id)
#
#         if quantity > book.number_in_stock:
#             raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail=f"""You're trying to order too many books, only {book.number_in_stock} left in stock"""
#                     )
#
#         for book_in_order in order.order_details:
#             # Firstly, check if the book already in the order
#             if book_in_order.book_id == book.id and book_in_order.order_id == order.id:
#                 # if it is, change respective params for the book in the order
#                 book_in_order.count_ordered += quantity
#                 order.total_sum += (book.price_with_discount * quantity)
#                 book.number_in_stock -= quantity
#                 await session.commit()
#                 return
#
#         # if the book was not found in the order, then we add a new record
#         order.order_details.append(
#             BookOrderAssoc(
#                 book_id=book_id,
#                 order_id=order_id,
#                 count_ordered=quantity)
#             )
#         order.total_sum = book.price_with_discount * quantity # set initial total sum
#         book.number_in_stock = book.number_in_stock - quantity
#         await self.order_repo.commit(session=session)
#
#     async def delete_book_from_order(
#             self,
#             session: AsyncSession,
#             book_id: str | int,
#             order_id: int,
#     ) -> None:
#
#         if not is_valid_uuid(book_id):
#             raise InvalidModelCredentials(
#                 message="Invalid id format for book"
#             )
#
#         order: Order | None = await self.order_repo.get_order_with_order_details(
#             session=session,
#             order_id=order_id,
#         )
#
#         if not order:
#             raise EntityDoesNotExist(entity="Order")
#
#         for book in order.order_details:
#             if str(book.book_id) == book_id and order_id == book.order_id:
#                 try:
#                     order.order_details.remove(book)
#                     await session.commit()
#                     return
#                 except IntegrityError as e:
#                     extra = {"book_id": book_id, "order_id": order_id}
#                     logger.error(
#                         f"Book deletion error: Unable to delete book from the order: {e}", extra=extra, exc_info=True
#                     )
#
#         raise EntityDoesNotExist("Book")
#
#     async def make_order(
#             self,
#             session: AsyncSession,
#             order_id: int,
#
#     ):
#         user: ReturnUserS = await self.user_service.get_user_by_order_id(session=session, order_id=order_id)
#         user_with_orders: ReturnUserWithOrdersS = await self.user_service.get_user_with_orders(
#             session=session,
#             user_id=user.id
#         )
#         order_books: list[BookSummaryS] = []
#
#         for order in user_with_orders.orders:
#             if order.order_id == order_id:
#                 for book in order.books:
#                     total_price = book.count_ordered * book.price_per_unit
#                     book_summary = BookSummaryS(
#                         name=book.name,
#                         count_ordered=book.count_ordered,
#                         total_price=total_price
#                     )
#                     order_books.append(book_summary)
#                 break
#
#         data = OrderSummaryS(
#             username=user.name,
#             email=user.email,
#             books=order_books
#         ).model_dump()
#
#         send_order_summary_email.delay(
#             order_data=data,
#         )
#
#
# class AuthorService(EntityBaseService):
#
#     def __init__(
#             self,
#             author_repo: Annotated[OrmEntityRepoInterface, Depends(AuthorRepository)],
#     ):
#         super().__init__(auhor_repo=author_repo)
#         self.author_repo = author_repo
#
#     async def get_all_authors(self, session: AsyncSession) -> list[ReturnAuthorS]:
#         return await super().get_all(
#             repo=self.author_repo,
#             session=session,
#         )
#
#     async def get_authors_by_filters(self, session: AsyncSession, **filters) -> list[ReturnAuthorS]:
#         return await super().get_all(
#             repo=self.author_repo,
#             session=session,
#             **filters
#         )
#
#     async def create_author(
#             self,
#             session: AsyncSession,
#             dto: CreateAuthorS
#     ) -> None:
#         await super().create(repo=self.author_repo, session=session, dto=dto)
#
#     async def delete_author(
#             self,
#             session: AsyncSession,
#             author_id: int
#     ) -> None:
#         await super().delete(repo=self.author_repo, session=session, instance_id=author_id)
#
#     async def update_author(
#             self,
#             author_id: int,
#             session: AsyncSession,
#             data: UpdateAuthorS | UpdatePartiallyAuthorS
#     ):
#         await super().update(
#             repo=self.author_repo,
#             session=session,
#             dto=data,
#             instance_id=author_id
#         )
#
#
# class PublisherService(EntityBaseService):
#
#     def __init__(
#             self,
#             publisher_repo: Annotated[OrmEntityRepoInterface, Depends(PublisherRepository)]
#     ):
#         super().__init__(publisher_repo=publisher_repo)
#         self.publisher_repo = publisher_repo
#
#     async def get_all_publishers(self, session: AsyncSession):
#         return super().get_all(repo=self.publisher_repo, session=session)
#
#     async def get_publishers_by_filters(
#             self,
#             session: AsyncSession,
#             **filters
#     ) -> list[ReturnPublisherS]:
#         return await super().get_all(
#             repo=self.publisher_repo,
#             session=session,
#             **filters
#         )
#
#     async def create_publisher(
#             self,
#             session: AsyncSession,
#             dto: CreatePublisherS
#     ) -> None:
#         await super().create(repo=self.publisher_repo, session=session, dto=dto)
#
#     async def delete_publisher(
#             self,
#             session: AsyncSession,
#             publisher_id: int
#     ) -> None:
#         await super().delete(repo=self.publisher_repo, session=session, instance_id=publisher_id)
