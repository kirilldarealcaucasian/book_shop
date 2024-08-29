from core import OrmEntityRepository


class AuthorRepository(OrmEntityRepository):
    from application.models import Author
    model: Author = Author