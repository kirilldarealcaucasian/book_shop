from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories import ShoppingSessionRepository
from application.schemas import ReturnShoppingSessionS, CreateShoppingSessionS, ShoppingSessionIdS, \
    UpdatePartiallyShoppingSessionS
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface


class ShoppingSession(EntityBaseService):
    def __init__(
            self,
            shopping_session_repo: Annotated[
                OrmEntityRepoInterface, ShoppingSessionRepository]
    ):
        super().__init__(shopping_session_repo=shopping_session_repo)
        self.shopping_session_repo = shopping_session_repo

    def get_shopping_session_by_id(
            self,
            session: AsyncSession,
            id: str
    ) -> ReturnShoppingSessionS:
        return await super().get_by_id(
            session=session,
            repo=self.shopping_session_repo,
            id=id
        )

    def create_shopping_session(
            self,
            session: AsyncSession,
            data: CreateShoppingSessionS
    ) -> ShoppingSessionIdS:
        return await super().create(
            session=session,
            repo=self.shopping_session_repo,
            dto=data
        )

    def update_shopping_session(
            self,
            session: AsyncSession,
            id: str | int,
            update_data: UpdatePartiallyShoppingSessionS
    ) -> ReturnShoppingSessionS:
        return await super().update(
            session=session,
            repo=self.shopping_session_repo,
            instance_id=id,
            dto=update_data
        )
