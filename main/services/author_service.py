from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from main.repositories import AuthorRepository
from main.schemas import (
    CreateAuthorS,
    ReturnAuthorS,
    UpdateAuthorS,
    UpdatePartiallyAuthorS,
)


class AuthorService(EntityBaseService):
    def __init__(
        self,
        author_repo: Annotated[
            OrmEntityRepoInterface, Depends(AuthorRepository)
        ],
    ):
        super().__init__(auhor_repo=author_repo)
        self.author_repo = author_repo

    async def get_all_authors(
        self, session: AsyncSession
    ) -> list[ReturnAuthorS]:
        return await super().get_all(
            repo=self.author_repo,
            session=session,
        )

    async def get_authors_by_filters(
        self, session: AsyncSession, **filters
    ) -> list[ReturnAuthorS]:
        return await super().get_all(
            repo=self.author_repo, session=session, **filters
        )

    async def create_author(
        self, session: AsyncSession, dto: CreateAuthorS
    ) -> None:
        await super().create(repo=self.author_repo, session=session, dto=dto)

    async def delete_author(
        self, session: AsyncSession, author_id: int
    ) -> None:
        await super().delete(
            repo=self.author_repo, session=session, instance_id=author_id
        )

    async def update_author(
        self,
        author_id: int,
        session: AsyncSession,
        data: UpdateAuthorS | UpdatePartiallyAuthorS,
    ):
        await super().update(
            repo=self.author_repo,
            session=session,
            dto=data,
            instance_id=author_id,
        )
