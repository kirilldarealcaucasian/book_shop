from collections import defaultdict
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from core.exceptions import EntityDoesNotExist
from main import CreateBookS
from main.schemas import (
    ReturnImageS,
    ReturnBookS,
    UpdateBookS,
    UpdatePartiallyBookS,
    BookFilterS,
)

from main.repositories import BookRepository, ImageRepository
from main.services.facade_sublayer.storage_facade.storage_interface import (
    StorageInterface,
)
from main.services.facade_sublayer.storage_facade.internal_storage import (
    InternalStorage,
)
from typing import Annotated, Literal


class BookService(EntityBaseService):
    def __init__(
        self,
        storage: Annotated[StorageInterface, Depends(InternalStorage)],
        book_repo: Annotated[OrmEntityRepoInterface, Depends(BookRepository)],
        image_repo: Annotated[
            OrmEntityRepoInterface, Depends(ImageRepository)
        ],
    ):
        self.book_repo = book_repo
        self.image_repo = image_repo
        super().__init__(book_repo=book_repo, image_repo=image_repo)
        self.storage: StorageInterface = storage

    async def get_books_by_filters(
        self, session: AsyncSession, **filters
    ) -> list[ReturnBookS]:
        return await super().get_all(
            repo=self.book_repo, session=session, **filters
        )

    async def get_all_books(
        self, session: AsyncSession, filters: BookFilterS
    ) -> list[ReturnBookS]:
        key_value_filters = {}
        if filters.filterby:
            key_value_filters: dict = {
                subrow.split("=")[0]: subrow.split("=")[1]
                for subrow in (row for row in filters.filterby.split(","))
            }  # example: title="book1",genre="genre2" -> {"title": "book1", "genre": "genre2}"

        order_by_filters: dict[Literal["asc", "desc"], list[str]] = (
            defaultdict(list)
        )
        if filters.order_by:
            for order_filter in filters.order_by.split(","):
                if "-" == order_filter[0]:
                    order_by_filters["desc"].append(order_filter[1:])
                else:
                    order_by_filters["asc"].append(order_filter)

        return await super().get_all(
            repo=self.book_repo,
            session=session,
            key_value_filters=key_value_filters,
            order_by_filters=order_by_filters,
            page=filters.page,
            limit=filters.limit,
        )

    async def create_book(
        self, session: AsyncSession, dto: CreateBookS
    ) -> None:
        return await super().create(
            repo=self.book_repo, session=session, dto=dto
        )

    async def delete_book(
        self,
        session: AsyncSession,
        book_id: str,
    ) -> None:
        try:
            _: list[ReturnImageS] = await super().get_all(
                repo=self.image_repo, session=session, book_id=book_id
            )
        except EntityDoesNotExist:
            return await self.storage.delete_instance_with_images(
                delete_images=False, instance_id=book_id, session=session
            )
        return await self.storage.delete_instance_with_images(
            delete_images=True, instance_id=book_id, session=session
        )

    async def update_book(
        self,
        session: AsyncSession,
        book_id: str | int,
        data: UpdateBookS | UpdatePartiallyBookS,
    ) -> ReturnBookS:
        return await super().update(
            repo=self.book_repo, session=session, instance_id=book_id, dto=data
        )
