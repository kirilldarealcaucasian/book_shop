from core import OrmEntityRepository
from application.models import Author

class AuthorRepository(OrmEntityRepository):
    model: Author = Author