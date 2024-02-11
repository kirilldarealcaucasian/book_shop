from fastapi import UploadFile, HTTPException, status
from core import ImageConfig
from collections import namedtuple
from PIL import Image
import datetime


def construct_url(format: str, name: str):
    image_path: str = ImageConfig.image_path
    image_date: str = datetime.datetime.today().strftime("%Y-%d-%m-%S")
    folder_url = [image_path, name]
    image_url = [image_path, name, "/", image_date, ".", format]
    urls = namedtuple("urls", ["folder_url", "image_url"])
    return urls("".join(folder_url), "".join(image_url))


def fix_image_dimensions(image: UploadFile) -> namedtuple:
    image_format: str = image.filename.split(".")[-1]

    if image_format not in ImageConfig.allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Unacceptable file format"
        )

    fixed_image = Image.open(image.file)
    width, height = fixed_image.size

    if width > ImageConfig.image_width_bound:
        width = ImageConfig.image_width_bound
        fixed_image = fixed_image.resize((width, height))

    if height > ImageConfig.image_height_bound:
        height = ImageConfig.image_height_bound
        fixed_image = fixed_image.resize((width, height))
    image = namedtuple("image", ["image_format", "img_resource"])
    return image(image_format, fixed_image)
