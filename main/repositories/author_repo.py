from core import OrmEntityRepository
from main.models import Author

class AuthorRepository(OrmEntityRepository):
    model: Author = Author