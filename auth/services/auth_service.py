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
        payload_copy: dict = data.model_copy().model_dump()
        hashed_password = helpers.hash_password(payload_copy["password"])
        del payload_copy["confirm_password"]
        del payload_copy["password"]

        payload_copy["hashed_password"] = hashed_password
        user: ReturnUserS = await self.repository.create_user(
            session=session,
            data=payload_copy
        )
        return user

    async def authorize_user(self, session: AsyncSession, user_creds: LoginUserS) -> AccessToken:
        user: dict[str: TokenPayload, str: str] = \
            await self.repository.login_user(
                session=session,
                email=user_creds.email,
                password=user_creds.password
            )
        if helpers.validate_password(user_creds.password, user["hashed_password"]):
            return helpers.create_token(user["payload"], expire_timedelta=timedelta(minutes=100))

    @classmethod
    def get_token_payload(cls, credentials: HTTPAuthorizationCredentials) -> dict:
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
        if not email or not expiration or "role_name" not in payload:
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

        user: User = await self.repository.retrieve_user_by_email(
            session=session,
            email=email, is_login=True
            )

        return AuthenticatedUserS(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role_name=user.role_name
        )
