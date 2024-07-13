from core import OrmEntityRepository
from application.models import Publisher


class PublisherRepository(OrmEntityRepository):
    model: Publisher = Publisher