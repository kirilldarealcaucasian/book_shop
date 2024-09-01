from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Protocol, TypeVar

__all__ = (
    "OrmEntityRepoInterface"
)

DomainModelDataT = TypeVar("DomainModelDataT",)


class OrmEntityRepoInterface(Protocol):

    async def create(
            self,
            domain_model: DomainModelDataT,
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
            domain_model: DomainModelDataT,
            instance_id: int | UUID,
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




