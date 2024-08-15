from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from application.models import User
from application.schemas import ReturnUserS
from auth.schemas.token_schema import TokenPayload
from auth import helpers
from sqlalchemy.exc import DBAPIError, NoSuchTableError
from core.exceptions import ServerError, DuplicateError, UnauthorizedError
from logger import logger
from typing import TypeVar

TokenDataT = TypeVar("TokenDataT")


class AuthRepository:
    model = User

    async def retrieve_user_by_email(self,
                                     session: AsyncSession,
                                     email: str,
                                     is_login: bool = False
                                     ) -> User:
        stmt = select(self.model).filter_by(email=email)
        try:
            res = await session.execute(stmt)
        except NoSuchTableError:
            extra = {email: "email"}
            logger.error("Database error: User table does not exist", extra=extra, exc_info=True)
            raise ServerError("Unable to retrieve data")

        user = res.scalar_one_or_none()

        if user and not is_login:
            raise DuplicateError(self.model.__name__)

        if not user and is_login:
            raise UnauthorizedError(detail="Incorrect email")

        return user

    async def create_user(self,
                          data: dict,
                          session: AsyncSession
                          ) -> ReturnUserS:
        user_exists: User | None = await self.retrieve_user_by_email(
            session=session,
            email=data["email"]
        )
        if not user_exists:
            user = User(**data)
            user.email.lower()
            user.first_name.lower()
            user.last_name.lower()

            try:
                session.add(user)
                await session.commit()
            except (TypeError, DBAPIError) as e:
                raise ServerError(detail=str(e))
            except NoSuchTableError:
                extra = {"data": data}
                logger.error("Database error: User table does not exist", extra=extra, exc_info=True)
                raise ServerError("Unable to add data")

            stmt = select(User).filter_by(email=data["email"])

            db_user: ReturnUserS = (await session.scalars(stmt)).one_or_none()
            return db_user

    async def login_user(self,
                         session: AsyncSession,
                         email: str,
                         password: str,
                         ) -> dict[str: TokenDataT, str: str]:
        user: User = await self.retrieve_user_by_email(
            session=session,
            email=email,
            is_login=True
        )
        if helpers.validate_password(
                password=password,
                hashed_password=user.hashed_password
        ):
            return {"payload": TokenPayload(user_id=user.id, email=user.email, role=user.role_name),
                    "hashed_password": user.hashed_password
                    }
        raise UnauthorizedError(
            detail="Wrong password"
        )
