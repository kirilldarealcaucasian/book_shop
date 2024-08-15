from core import OrmEntityRepository
from application.models import ShoppingSession


class ShoppingSessionRepository(OrmEntityRepository):
    model: ShoppingSession = ShoppingSession



