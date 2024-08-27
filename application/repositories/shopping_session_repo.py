from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import  selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, Protocol

from core import OrmEntityRepository
from application.models import ShoppingSession
from core.base_repos import OrmEntityRepoInterface
from core.exceptions import NotFoundError, DBError


class ShoppingSessionRepoInterface(Protocol):
    async def get_by_id(
            self,
            session: AsyncSession,
            id: UUID
    ) -> ShoppingSession:
        pass


CombinedShoppingSessionRepositoryInterface = Union[OrmEntityRepoInterface, ShoppingSessionRepoInterface]


class ShoppingSessionRepository(OrmEntityRepository):
    model: ShoppingSession = ShoppingSession

    async def get_by_id(
        self,
        session: AsyncSession,
        id: UUID
    ) -> ShoppingSession:
        stmt = select(self.model).where(
            self.model.id == str(id)
        ).options(
            selectinload(self.model.user),
            selectinload(self.model.cart_items)
        )

        try:
            res = (await session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DBError(traceback=str(e))

        if not res:
            raise NotFoundError(entity=self.model.__name__)

        return res
