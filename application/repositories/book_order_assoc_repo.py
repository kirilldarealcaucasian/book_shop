from core import OrmEntityRepository
from application.models import BookOrderAssoc


class BookOrderAssocRepository(OrmEntityRepository):
    model = BookOrderAssoc