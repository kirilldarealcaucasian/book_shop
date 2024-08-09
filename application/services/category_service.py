from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.category_repo import CategoryRepository
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from core.exceptions import EntityDoesNotExist
from application.schemas import (
    ReturnCategoryS, CreateCategoryS, UpdateCategoryS,
)
from typing import Annotated


class CategoryService(EntityBaseService):
    def __init__(
        self,
        category_repo: Annotated[OrmEntityRepoInterface, Depends(CategoryRepository)],
    ):
        super().__init__(category_repo=category_repo)
        self.category_repo = category_repo

    async def get_all_categories(
        self,
        session: AsyncSession
    ) -> list[ReturnCategoryS]:
        categories = await super().get_all(
            repo=self.category_repo,
            session=session,
            limit=1000,
        )
        if len(categories) == 0:
            raise EntityDoesNotExist("Category")
        return categories

    async def get_category_by_id(
        self,
        session: AsyncSession,
        id: int
    ) -> ReturnCategoryS:
        category:  ReturnCategoryS | None = await super().get_by_id(
            repo=self.category_repo,
            session=session,
            id=id
        )
        if category is None:
            raise EntityDoesNotExist(entity="Category")
        return category

    async def delete_category(
        self, session: AsyncSession, category_id: int
    ) -> None:
        return await super().delete(
            repo=self.category_repo, session=session, instance_id=category_id
        )

    async def create_category(
            self,
            session: AsyncSession,
            dto: CreateCategoryS,
    ):
        return await super().create(
            repo=self.category_repo,
            session=session,
            dto=dto
        )

    async def update_category(
            self,
            session: AsyncSession,
            instance_id: int | str,
            dto: UpdateCategoryS
    ):
        return await super().update(
            repo=self.category_repo,
            session=session,
            instance_id=instance_id,
            dto=dto,
        )
