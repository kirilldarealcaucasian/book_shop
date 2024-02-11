from abc import ABC


class ImageConfig(ABC):
    image_path: str = "static/images/"
    allowed_formats: list = ["jpeg", "jpg", "gif", "png", "tiff", "bpm"]

    image_width_bound: int = 1024
    image_height_bound: int = 1024
