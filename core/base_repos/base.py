from sqlalchemy.ext.asyncio import AsyncSession
from typing import Protocol

__all__ = (
    "EntityRepoInterface",
    "OrmEntityRepoInterface"
)
class EntityRepoInterface(Protocol):
    async def create(
            self,
            data: dict,
            session: AsyncSession | None,
    ):
        ...

    async def get_all(
            self,
            session: AsyncSession | None,
            **filters,
    ):
        ...

    async def update(
            self,
            data: dict,
            instance_id: int,
            session: AsyncSession | None,
    ):
        ...

    async def delete(
            self,
            instance_id: int,
            session: AsyncSession | None,
    ):
        ...


class OrmEntityRepoInterface(Protocol):

    async def create(
            self,
            data: dict,
            session: AsyncSession
    ):
        ...

    async def get_all(
            self,
            session: AsyncSession,
            **filters,
    ):
        ...


    async def update(
            self,
            data: dict,
            instance_id: int,
            session: AsyncSession,
    ):
        ...

    async def delete(
            self,
            session: AsyncSession,
            instance_id: int,
    ):
        ...

    async def commit(self, session: AsyncSession):
        ...



