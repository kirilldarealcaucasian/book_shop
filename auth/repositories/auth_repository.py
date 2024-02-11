from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from main import User
from main.schemas import RegisterUserS, LoginUserS, ReturnUserS
from auth.schemas.token_schema import TokenPayload
from auth import helpers


class AuthRepository:
    model = User

    async def retrieve_user_by_email(self,
                                     session: AsyncSession,
                                     email: str,
                                     is_login: bool = False
                                     ) -> User:
        stmt = select(self.model).filter_by(email=email)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user and not is_login:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with that email already exists"
            )
        if not user and is_login:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User was not found."
            )
        return user

    async def create_user(self,
                          data: RegisterUserS,
                          session: AsyncSession
                          ) -> ReturnUserS:
        user_exists: User | None = await self.retrieve_user_by_email(session=session,
                                                                     email=data.email
                                                                     )
        if not user_exists:
            payload_copy: dict = data.model_copy().model_dump()
            hashed_password = helpers.hash_password(payload_copy["password"])
            del payload_copy["password"]
            payload_copy["hashed_password"] = hashed_password
            user = User(**payload_copy)
            session.add(user)
            await session.commit()
            stmt = select(User).filter_by(email=data.email)
            db_user: ReturnUserS = (await session.scalars(stmt)).one_or_none()
            return db_user


    async def login_user(self,
                         session: AsyncSession,
                         user_creds: LoginUserS
                         ) -> dict[str: TokenPayload, str: str]:
        user: User = await self.retrieve_user_by_email(
            session=session,
            email=user_creds.email,
            is_login=True
        )
        return {"payload": TokenPayload(email=user.email, is_admin=user.is_admin),
                "hashed_password": user.hashed_password
                }





