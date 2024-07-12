from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from auth.services import AuthService
from auth.repositories import AuthRepository
from core.base_repos import OrmEntityRepoInterface
from main.models import Order
from main.repositories import OrderRepository
from main.repositories.order_repo import CombinedOrderRepositoryInterface
from main.services import OrderService
from core.db_conf.config import db_config
from core.exceptions import UnauthorizedError


class PermissionService(AuthRepository):


    @staticmethod
    def get_admin_permission(
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        payload = AuthService.get_token_payload(credentials=credentials)

        if not payload["role"] == "admin":
            raise UnauthorizedError(
                detail="You don't have permission to perform this action"
            )
        return True

    async def get_order_permission(
            self,
            order_id: int,
            order_repo: Annotated[CombinedOrderRepositoryInterface, Depends(OrderRepository)],
            order_service: OrderService = Depends(),
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
            session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
    ) -> int:
        payload: dict = AuthService.get_token_payload(credentials=credentials)
        user_id = payload["user_id"]

        try:
            order: Order = await order_service.get_all(
                repo=order_repo,
                session=session,
                id=order_id
            )

        except IndexError:
            raise UnauthorizedError(
                detail="You don't have permission to access this data"
            )

        if order.user_id != user_id and not payload["role"] == "admin":
            raise UnauthorizedError(
                detail="You don't have permission to perform this action"
            )
        return user_id



