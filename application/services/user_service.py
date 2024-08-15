from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError, PydanticSchemaGenerationError
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.user_repo import UnitedUserInterface
from application.schemas.domain_model_schemas import UserS
from core import EntityBaseService
from application.repositories import UserRepository
from application.schemas import (
    ReturnUserS,
    UpdateUserS,
    UpdatePartiallyUserS,
    ReturnUserWithOrdersS,
)
from application.schemas.filters import PaginationS
from core.exceptions import EntityDoesNotExist, DomainModelConversionError, NotFoundError
from logger import logger


class UserService(EntityBaseService):
    def __init__(
        self,
        user_repo: Annotated[UnitedUserInterface, Depends(UserRepository)],
    ):
        super().__init__(user_repo=user_repo)
        self.user_repo = user_repo

    async def get_all_users(
        self, session: AsyncSession, pagination: PaginationS
    ) -> list[ReturnUserS] | ReturnUserS:
        try:
            users = await super().get_all(
                repo=self.user_repo,
                session=session,
                page=pagination.page,
                limit=pagination.limit,
            )
        except NotFoundError:
            raise EntityDoesNotExist(entity="User")
        return users

    async def get_user_by_id(
        self,
        session: AsyncSession,
        id: int
    ) -> ReturnUserS:
        try:
            user: ReturnUserS | None = await super().get_by_id(
                repo=self.user_repo,
                session=session,
                id=id
            )
        except NotFoundError:
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
        dto: UpdateUserS | UpdatePartiallyUserS,
    ) -> None:
        dto: dict = dto.model_dump(exclude_unset=True)

        try:
            domain_model = UserS(**dto)
        except (ValidationError, PydanticSchemaGenerationError) as e:
            logger.error(
                "Failed to generate domain model",
                extra={"dto": dto},
                exc_info=True
            )
            raise DomainModelConversionError

        return await super().update(
            session=session,
            repo=self.user_repo,
            instance_id=user_id,
            domain_model=domain_model
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
