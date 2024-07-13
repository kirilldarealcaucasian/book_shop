from core import OrmEntityRepository
from application.models import Image


class ImageRepository(OrmEntityRepository):
    model: Image = Image