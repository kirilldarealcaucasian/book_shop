from typing import Annotated

from fastapi import Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from core.exceptions import RelatedEntityDoesNotExist
from main.repositories import ImageRepository
from main.schemas import ReturnImageS, CreateImageS, ReturnBookS
from main.services.book_service import BookService
from main.services.facade_sublayer import InternalStorage
from main.services.facade_sublayer.storage_facade.storage_interface import (
    StorageInterface,
)


class ImageService(EntityBaseService):
    def __init__(
        self,
        image_repo: Annotated[
            OrmEntityRepoInterface, Depends(ImageRepository)
        ],
        storage: Annotated[StorageInterface, Depends(InternalStorage)],
        book_service: BookService = Depends(),
    ):
        super().__init__(repository=image_repo)
        self.image_repo = image_repo
        self.book_service = book_service
        self.storage = storage

    async def get_all_images(
        self, session: AsyncSession, book_id: str | int
    ) -> list[ReturnImageS]:
        return await super().get_all(
            session=session, repo=self.image_repo, book_id=book_id
        )

    async def upload_image(
        self,
        session: AsyncSession,
        book_id: str | int,
        image: UploadFile = File(...),
    ):
        book: (
            list[ReturnBookS] | None
        ) = await self.book_service.get_books_by_filters(
            session=session, book_id=book_id
        )

        if not book:
            raise RelatedEntityDoesNotExist(entity="Book")

        image_data: CreateImageS = await self.storage.upload_image(
            image=image, instance_id=book_id
        )

        if image_data:
            await super().create(
                repo=self.image_repo, session=session, dto=image_data
            )

    async def delete_image(self, session: AsyncSession, image_id: int) -> None:
        image: list[ReturnImageS] = await super().get_all(
            repo=self.image_repo, session=session, id=image_id
        )

        if not image:
            raise RelatedEntityDoesNotExist("Image")
        image_url: str = image[0].url

        if await super().delete(
            repo=self.image_repo, session=session, instance_id=image[0].id
        ):
            await self.storage.delete_image(
                image_url=image_url, image_id=image_id
            )

    # async def delete_image(
    #         self,
    #         session: AsyncSession,
    #         image_id: int
    # ):
    #     image: list[ReturnImageS] = await self.repository.get_all(session=session, id=image_id)
    #     image_url: str = image[0].url
    #     await self.repository.delete(session=session, instance_id=image[0].id)
    #     try:
    #         logger.info("Image url: ", image_url)
    #         image_path = os.path.join(image_url)
    #         os.remove(image_path)
    #         return
    #     except FileNotFoundError:
    #         extra = {"image_id": image_id, "image_url": image_url}
    #         logger.error("File deletion Error: Error while trying to delete file", extra, exc_info=True)
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="File you're trying to remove does not exist"
    #         )
