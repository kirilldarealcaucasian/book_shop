from contextlib import asynccontextmanager
from fastapi import UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import logger
from core import EntityBaseService
from main.repositories import ImageRepository, BookRepository

from main.schemas import CreateImageS, ReturnImageS

# from main.services import ImageService
from main.services.facade_sublayer.storage_facade.configs import S3Conf
from aiobotocore.session import get_session

from main.services.facade_sublayer.storage_facade.internal_storage.image_manager import (
    ImageManager,
    ImageData,
)
from main.services.facade_sublayer.storage_facade.s3_storage.helpers import (
    format_for_deletion,
)
from logger import logger

__all__ = ("S3Client", "s3_client")


class S3Client(EntityBaseService):
    # implements functionality for managing storage of images in the remote S3 bucket

    def __init__(
        self,
        service_name: str = S3Conf.SERVICE_NAME,
        image_manager: ImageManager = Depends(),
        image_repo: ImageRepository = Depends(),
        # image_service: ImageService = Depends(),
        book_repo: BookRepository = Depends(),
    ):
        self.service_name = service_name
        self.session = get_session()
        # self.image_service = image_service
        self.book_repo = book_repo
        self.image_repo = image_repo
        self.bucket_name = S3Conf.BUCKET_NAME
        self.__image_manager = image_manager
        super().__init__(image_repo=image_repo)

    @asynccontextmanager
    async def get_client(self):
        try:
            async with self.session.create_client(
                self.service_name, **S3Conf.get_client_config
            ) as client:
                yield client
        except Exception as e:
            extra = {**S3Conf.get_client_config}
            logger.error(
                f"Unable to create S3 client session: {e}",
                extra=extra,
                exc_info=True,
            )
            return

    async def upload_image(
        self,
        instance_id: int | str,
        image: UploadFile,
    ) -> CreateImageS | None:
        image_to_bytes: bytes = await image.read()
        image_data: ImageData = await self.__image_manager(
            image=image, image_folder_name=instance_id
        )
        image_url = image_data.get("image_url", None)
        fixed_image_url = image_url[1:].replace("/", "-")

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=fixed_image_url,
                Body=image_to_bytes,
            )

        return CreateImageS(
            book_id=instance_id,
            url=f"https://s3.cloud.ru/{self.bucket_name}/{self.bucket_name}/{fixed_image_url}",
        )

    async def delete_image(self, image_id: int, image_url: str):
        async with self.get_client() as client:
            return await client.delete_object(
                Bucket=self.bucket_name, Key=image_url
            )

    async def delete_instance_with_images(
        self,
        instance_id: str | int,
        session: AsyncSession,
        delete_images: bool = False,
    ):
        if delete_images:
            images: list[ReturnImageS] = await self.image_repo.get_all(
                session=session, book_id=instance_id
            )

            image_keys_to_delete: list[dict[str, str]] = format_for_deletion(
                objects=images,
                bucket_name=self.bucket_name,
            )

            if not await self.book_repo.delete(
                session=session, instance_id=instance_id
            ):
                async with self.get_client() as client:
                    return await client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={"Objects": image_keys_to_delete},
                    )
        else:
            return await self.book_repo.delete(
                session=session, instance_id=instance_id
            )


s3_client = S3Client()
