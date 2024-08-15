from core import OrmEntityRepository
from application.models import  Category


class CategoryRepository(OrmEntityRepository):
    model: Category = Category
