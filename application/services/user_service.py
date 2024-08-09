from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core import EntityBaseService
from application.repositories import OrmEntityUserInterface, UserRepository
from application.schemas import (
    ReturnUserS,
    UpdateUserS,
    UpdatePartiallyUserS,
    ReturnUserWithOrdersS,
)
from application.schemas.filters import PaginationS
from core.exceptions import EntityDoesNotExist


class UserService(EntityBaseService):
    def __init__(
        self,
        user_repo: Annotated[OrmEntityUserInterface, Depends(UserRepository)],
    ):
        super().__init__(user_repo=user_repo)
        self.user_repo = user_repo

    async def get_all_users(
        self, session: AsyncSession, pagination: PaginationS
    ) -> list[ReturnUserS] | ReturnUserS:
        return await super().get_all(
            repo=self.user_repo,
            session=session,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get_user_by_id(
        self,
        session: AsyncSession,
        id: int
    ) -> ReturnUserS:
        user: ReturnUserS | None = await super().get_by_id(
            repo=self.user_repo,
            session=session,
            id=id
        )
        if user is None:
            raise EntityDoesNotExist(entity="User")
        return user

    async def delete_user(
        self, session: AsyncSession, user_id: str | int
    ) -> None:
        return await super().delete(
            repo=self.user_repo, session=session, instance_id=user_id
        )

    async def update_user(
        self,
        session: AsyncSession,
        user_id: str | int,
        data: UpdateUserS | UpdatePartiallyUserS,
    ) -> None:
        return await super().update(
            repo=self.user_repo, session=session, instance_id=user_id, dto=data
        )

    async def get_user_with_orders(
        self, session: AsyncSession, user_id: int
    ) -> ReturnUserWithOrdersS:
        return await self.user_repo.get_user_with_orders(
            session=session, user_id=user_id
        )

    async def get_user_by_order_id(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> ReturnUserS:
        return await self.user_repo.get_user_by_order_id(
            session=session, order_id=order_id
        )
