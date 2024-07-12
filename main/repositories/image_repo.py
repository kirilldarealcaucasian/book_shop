from core import OrmEntityRepository
from main.models import Image


class ImageRepository(OrmEntityRepository):
    model: Image = Image