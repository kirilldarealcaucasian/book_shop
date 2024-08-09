from core import OrmEntityRepository
from application.models import Image, Category


class CategoryRepository(OrmEntityRepository):
    model: Category = Category
