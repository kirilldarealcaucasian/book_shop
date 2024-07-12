import os
from typing import BinaryIO
from fastapi import UploadFile, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import EntityDoesNotExist
from main.repositories import BookRepository
from main.services.facade_sublayer.storage_facade.internal_storage.image_manager import (
    ImageManager,
    ImageData,
)
from main.schemas import CreateImageS
from main.tasks import upload_image
from logger import logger
from celery.exceptions import TaskError
from main.tasks import delete_all_images


class InternalStorage:
    # implements functionality for managing storage of images in the main/static/images folder

    def __init__(
        self,
        book_repo: BookRepository = Depends(),
        image_manager: ImageManager = Depends(),
    ):
        self.book_repo = book_repo
        self.__image_manager = image_manager

    async def upload_image(
        self,
        image: UploadFile,
        instance_id: str | int,
    ) -> CreateImageS:
        res: ImageData = await self.__image_manager(
            image=image, image_folder_name=instance_id
        )

        image_url = res.get("image_url", None)
        image_name = res.get("image_name", None)
        image_to_binary: BinaryIO = image.file

        if image_url is None or image_name is None:
            raise HTTPException(
                status_code=500, detail="Unable to upload the file"
            )

        try:
            upload_image.delay(
                image=image_to_binary,
                image_folder_name=instance_id,
                image_name=image_name,
            )
        except TaskError:
            extra = {"instance_id": instance_id}
            logger.error(
                "Celery error: error while trying to upload the image",
                extra,
                exc_info=True,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to upload the file",
            )

        return CreateImageS(book_id=instance_id, url=image_url)

    async def delete_image(self, image_url: str, image_id: int) -> None:
        try:
            image_path = os.path.join(image_url)
            os.remove(image_path)
        except FileNotFoundError:
            extra = {"image_id": image_id, "image_url": image_url}
            logger.error(
                "File deletion Error: Error while trying to delete file",
                extra,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File you're trying to remove does not exist",
            )

    async def delete_instance_with_images(
        self,
        instance_id: str,
        session: AsyncSession,
        delete_images: bool = False,
    ) -> None:
        if delete_images:
            if not await self.book_repo.delete(
                session=session, instance_id=instance_id
            ):  # if no exceptions was raised
                delete_all_images.delay(instance_id)
        else:
            try:
                print("IN DELETE INSTANCE WITH IMAGES")
                return await self.book_repo.delete(
                    session=session, instance_id=instance_id
                )
            except EntityDoesNotExist:
                raise EntityDoesNotExist(entity="Book")

        # try:
        #     # await self.image_repo.get_all(session=session, book_id=book_id)
        #     await self.image_service.get_all(session=session, book_id=book_id)
        # except EntityDoesNotExist: # if there are no images for the given book
        #     # await self.book_repo.delete(session=session, instance_id=book_id)
        #     await self.image_service.book_service.delete(session=session, book_id=book_id)
        #     return
