from fastapi import Security, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .auth_service import AuthService
from ..repositories import AuthRepository


#!!! implement specificity pattern for roles


class PermissionService(AuthRepository):
    __slots__ = ("repository",)

    def __init__(self, repository: AuthRepository = AuthRepository):
        self.repository = repository

    @staticmethod
    def get_admin_permission(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
                             ):
        payload = AuthService.get_token_payload(credentials=credentials)

        if not payload["is_admin"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have permission to perform this action"
            )
        return True

    async def get_order_permission(
            self, order_id,
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        payload = AuthService.get_token_payload(credentials=credentials)
        email = payload["sub"]
        await self.repository.retrieve_user_by_email()
