from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from main import User
from auth.repositories.auth_repository import AuthRepository
from main.schemas import LoginUserS, RegisterUserS, ReturnUserS, AuthenticatedUserS
from auth import helpers
from auth.helpers import decode_jwt
from auth.schemas.token_schema import TokenPayload, AccessToken


class AuthService:

    def __init__(self, repository: AuthRepository = Depends(AuthRepository)):
        self.repository = repository


    async def register_user(self, session: AsyncSession, data: RegisterUserS):
        user: ReturnUserS = await self.repository.create_user(
            session=session,
            data=data
        )
        return user

    async def authorize_user(self, session: AsyncSession, user_creds: LoginUserS) -> AccessToken:
        user: dict[str: TokenPayload, str: str] = \
            await self.repository.login_user(session=session, user_creds=user_creds)
        if helpers.validate_password(user_creds.password, user["hashed_password"]):
            return helpers.create_token(user["payload"], expire_timedelta=timedelta(minutes=10))

    @classmethod
    def get_token_payload(cls, credentials: HTTPAuthorizationCredentials):
        token: str = credentials.credentials
        if not token:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="No token in the header. You are not authorized"
            )
        payload: dict = decode_jwt(token)
        return payload

    @staticmethod
    def validate_token(payload: dict):
        email: str = payload["sub"]
        expiration: int = payload["exp"]
        if not email or not expiration or "is_admin" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email


    async def get_auth_user(self,
                            session: AsyncSession,
                            credentials: HTTPAuthorizationCredentials
                            ) -> AuthenticatedUserS:
        payload: dict = self.get_token_payload(credentials=credentials)
        email: str = self.validate_token(payload)

        user: User = await self.repository.retrieve_user_by_email(session=session,
                                                                  email=email, is_login=True
                                                                  )

        return AuthenticatedUserS(
            id=user.id,
            name=user.name,
            email=user.email,
            is_admin=user.is_admin
        )







