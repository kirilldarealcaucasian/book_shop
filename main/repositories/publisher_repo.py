from core import OrmEntityRepository
from main.models import Publisher


class PublisherRepository(OrmEntityRepository):
    model: Publisher = Publisher