from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from auth.services import AuthService
from auth.repositories import AuthRepository
from application.models import Order
from application.repositories import OrderRepository
from application.repositories.order_repo import CombinedOrderRepositoryInterface
from application.services import OrderService, UserService
from infrastructure.postgres import db_client
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
            session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
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

    async def get_authorized_permission(
            self,
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
            user_service: UserService = Depends(),
            session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
    ):
        "Checks if the user is logged in"

        payload: dict = AuthService.get_token_payload(credentials=credentials)
        user_id = payload["user_id"]
        _ = await user_service.get_user_by_id(session=session, id=user_id)  # if no user,  exception
        # will be raised by user_service
