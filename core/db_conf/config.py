from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, async_scoped_session, AsyncSession
from .get_db_data import \
    (
    db_url
     )
from asyncio import current_task
from abc import ABC


class AbstractDbConfig(ABC):
    __slots__ = ("engine", "async_session")

    def __init__(self, echo: bool = False):
        self.engine = create_async_engine(url=db_url, echo=echo)
        self.async_session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False
        )

    def get_async_scoped_session(self):
        return async_scoped_session(
            session_factory=self.async_session,
            scopefunc=current_task
        )

    async def get_scoped_session_dependency(self) -> AsyncSession:
        session = self.get_async_scoped_session()
        yield session
        await session.remove()


db_config = AbstractDbConfig(echo=False)
