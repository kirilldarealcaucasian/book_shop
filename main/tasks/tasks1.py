import os
import shutil
import socket
from typing import BinaryIO

from PIL import Image
from fastapi import HTTPException, status, UploadFile
from main.static import STATIC_FOLDER_ABSOLUTE_PATH
from core.image_conf import ImageConfig
from email.message import EmailMessage
from main.tasks.celery_init import celery
from main.tasks.config.email_config import email_settings
from main.tasks.helpers import email_generator
from pathlib import Path
import smtplib
from logger import logger


def create_image_folder(concrete_image_folder_name: str) -> str:
    image_folder_path: str = os.path.join(
        STATIC_FOLDER_ABSOLUTE_PATH,
        ImageConfig.images_folder,
        concrete_image_folder_name
    )
    try:
        if not Path(image_folder_path).is_dir():
            os.makedirs(image_folder_path, exist_ok=True)
    except OSError:
        extra = {"problem_directory": concrete_image_folder_name}
        logger.error("Os Exception: Unable to create image directory", extra, exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong while uploading an image"
        )
    return image_folder_path


def fix_and_save_image(image: BinaryIO, full_image_path: str):
    try:
        with Image.open(image) as fixed_image:
            width, height = fixed_image.size

            if width > ImageConfig.image_width_bound:
                width = ImageConfig.image_width_bound
                fixed_image = fixed_image.resize((width, height))

            if height > ImageConfig.image_height_bound:
                height = ImageConfig.image_height_bound
                fixed_image = fixed_image.resize((width, height))

            fixed_image.save(full_image_path)
    except OSError as e:
        extra = {"full_image_path": full_image_path}
        logger.error("Os Error: Error while opening or saving image", extra, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sth went wrong while fixing image, {e}"
            )


@celery.task
def upload_image(
        image: BinaryIO,
        image_folder_name: str,
        image_name: str,
):
    image_folder_path: str = create_image_folder(image_folder_name)
    full_image_path = os.path.join(image_folder_path, image_name)
    fix_and_save_image(image=image, full_image_path=full_image_path)


@celery.task
def send_order_summary_email(
        order_data: dict,
) -> None:
    email: EmailMessage = email_generator.create_order_confirmation_template(data=order_data)
    try:
        with smtplib.SMTP_SSL(
                email_settings.SMTP_HOST,
                email_settings.SMTP_PORT
        ) as server:
            server.login(email_settings.SMTP_USER, email_settings.SMTP_PASS)
            server.send_message(email)
    except socket.error:
        extra = {
            "SMTP_HOST": email_settings.SMTP_HOST,
            "SMTP_PORT": email_settings.SMTP_PORT
        }
        logger.error(
            "SMTP Exc: Error while connecting to SMTP server. Umable to send email", extra, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong while sending email"
        )


@celery.task
def delete_all_images(concrete_image_folder: int):
    try:
        shutil.rmtree(
            os.path.join(
                STATIC_FOLDER_ABSOLUTE_PATH,
                ImageConfig.images_folder,
                str(concrete_image_folder)
            )
        )
    except OSError:
        extra = {"folder_with_images": concrete_image_folder}
        logger.info("OS Exc: Unable to remove folder with images", extra, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while deleting images"
        )
