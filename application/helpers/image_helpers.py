import os
from fastapi import HTTPException, status, File
from collections import namedtuple
from core.image_conf.conf import ImageConfig
# from application.static import STATIC_FOLDER_ABSOLUTE_PATH
import datetime


def get_image_format(image: File) -> str:
    format: str = image.filename.split(".")[1]

    if format not in ImageConfig.allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Not acceptable image format")
    return format


def construct_url(format: str, name: str):
    image_folder: str = ImageConfig.images_folder
    image_date: str = datetime.datetime.today().strftime("%Y-%d-%m-%S")
    folder_url = os.path.join(image_folder, name)
    image_url = os.path.join(folder_url, image_date) + f".{format}"
    image_name = image_date + f".{format}"
    urls = namedtuple("urls", ["folder_url", "image_url", "image_name"])
    return urls(folder_url, image_url, image_name)


def create_image_folder(concrete_image_folder_name: str) -> str:
    image_folder = os.path.join(
        ImageConfig.static_folder_path,
        ImageConfig.images_folder,
        concrete_image_folder_name
    )
    try:
        os.mkdir(image_folder)
    except FileExistsError:
        pass
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )
    return image_folder


# def move_image_to_folder(
#         image_name: str,
#         image: UploadFile,
#         product_id: str
# ):
#     image_folder_path = create_image_folder(product_id)  # ex./project/application/static/images/1/
#     image_full_url = os.path.join(image_folder_path, image_name)
#     # try:
#     #     with open(r'{}'.format(image_full_url), mode="wb+") as file_object:
#     #         shutil.copyfileobj(image.file, file_object)
#     try:
#         print('IMAGE NAME:', image_name)
#         with open(f"/project/application/tasks/{image_name}", mode="wb+") as file_object:
#             shutil.copyfileobj(image.file, file_object)
#         os.chmod(f"/project/application/tasks/{image_name}", 0o777)
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Something went wrong while uploading photo: {e}"
#         )
#     replace_with_fixed_image.delay(image_name)

