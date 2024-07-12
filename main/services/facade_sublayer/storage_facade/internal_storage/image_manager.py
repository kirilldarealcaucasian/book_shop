from fastapi import HTTPException, status, UploadFile
from datetime import datetime
from core import ImageConfig
from os import path
from typing import TypedDict


class ImageData(TypedDict):
    image_url: str
    image_name: str


class ImageManager:
    # validates image credentials and generates url

    @staticmethod
    async def image_validate(image: UploadFile) -> bool:
        content_type = image.content_type.split("/")[1]

        validators = [
            content_type in ImageConfig.allowed_formats,
            len(await image.read()) < 4000000,
        ]

        if not validators[0]:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Not acceptable file format",
            )

        elif not validators[1]:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="File size is too big",
            )
        return True if all(validators) else False

    @staticmethod
    def construct_image_url(format: str, image_folder_name: str) -> ImageData:
        image_folder: str = (
            ImageConfig.images_folder
        )  # generic folder where images are stored
        image_identifier: str = datetime.today().strftime(
            "%Y-%d-%m-%S"
        )  # unique identifier of an image
        image_folder_url = path.join(
            image_folder, image_folder_name
        )  # path to folder where the image is stored (like images/1)
        image_url = (
            path.join(image_folder_url, image_identifier) + f".{format}"
        )  # path to folder where the image is

        relative_concrete_image_path = path.join(
            ImageConfig.static_folder_path, image_url
        )  # path up to static folder merged with image_url
        absolute_concrete_image_path = path.abspath(
            relative_concrete_image_path
        )  # absolute path to the image

        return ImageData(
            image_url=absolute_concrete_image_path,
            image_name=image_identifier + f".{format}",
        )

    async def __call__(
        self, image: UploadFile, image_folder_name: str
    ) -> ImageData:
        format = image.content_type.split("/")[1]

        if await self.image_validate(image=image):
            return self.construct_image_url(
                format=format, image_folder_name=image_folder_name
            )
