from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from main.repositories import PublisherRepository
from main.schemas import CreatePublisherS, ReturnPublisherS


class PublisherService(EntityBaseService):
    def __init__(
        self,
        publisher_repo: Annotated[
            OrmEntityRepoInterface, Depends(PublisherRepository)
        ],
    ):
        super().__init__(publisher_repo=publisher_repo)
        self.publisher_repo = publisher_repo

    async def get_all_publishers(self, session: AsyncSession):
        return super().get_all(repo=self.publisher_repo, session=session)

    async def get_publishers_by_filters(
        self, session: AsyncSession, **filters
    ) -> list[ReturnPublisherS]:
        return await super().get_all(
            repo=self.publisher_repo, session=session, **filters
        )

    async def create_publisher(
        self, session: AsyncSession, dto: CreatePublisherS
    ) -> None:
        await super().create(
            repo=self.publisher_repo, session=session, dto=dto
        )

    async def delete_publisher(
        self, session: AsyncSession, publisher_id: int
    ) -> None:
        await super().delete(
            repo=self.publisher_repo, session=session, instance_id=publisher_id
        )
