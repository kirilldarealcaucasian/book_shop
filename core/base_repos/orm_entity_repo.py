from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from logger import logger
from core.exceptions.storage_exceptions import (
    DuplicateError,
    DBError, NotFoundError
)
from sqlalchemy.exc import NoSuchTableError, NoReferenceError
from typing import TypeVar
from application.schemas.domain_model_schemas import \
    (
    AuthorS,
    BookS,
    BookOrderAssocS,
    CartItemS,
    CategoryS,
    OrderS,
    PaymentDetailS,
    PublisherS,
    ShoppingSessionS
)

DomainModelDataT = TypeVar(
    "DomainModelDataT",
    AuthorS, BookS, BookOrderAssocS,
    CartItemS, CategoryS, OrderS,
    PaymentDetailS, PublisherS, ShoppingSessionS
)


class OrmEntityRepository:
    model = None

    async def create(
            self,
            session: AsyncSession,
            domain_model: DomainModelDataT,
    ) -> None:
        to_add = None
        try:
            to_add = self.model(domain_model.model_dump(exclude_unset=True))
        except Exception as e:
            raise DBError(
                message="Error while creating a domain model",
                traceback=str(e)
            )
        try:
            session.add(to_add)
            await session.commit()
        except NoSuchTableError as e:
            raise DBError(
                message=f"Table for {self.model} does not exist",
                traceback=str(e)
            )

        except IntegrityError as e:
            raise DuplicateError(
                entity=self.model.__name__,
                traceback=str(e)
            )

        except NoReferenceError as e:
            raise DBError(
                message="Invalid ForeignKey reference",
                traceback=str(e)
            )

    async def get_all(
            self,
            session: AsyncSession,
            page: int = 0,
            limit: int = 5,
            **filters
    ) -> list:
        stmt = select(self.model).filter_by(**filters).offset(page * limit).limit(limit)
        try:
            domain_models: list | [] = (await session.scalars(stmt)).all()
        except NoSuchTableError as e:
            raise DBError(
                message=f"Table for {self.model} does not exist",
                traceback=str(e)
            )

        if not domain_models or domain_models is None:
            return []

        return list(domain_models)

    async def update(
            self,
            domain_model: DomainModelDataT,
            instance_id: str | int,
            session: AsyncSession,
    ) -> None:

        _ = await self.get_all(session=session, id=instance_id)  # check existence of the entity
        to_update = None

        try:
            to_update = self.model(domain_model.model_dump(exclude_unset=True))
        except Exception as e:
            raise DBError(
                message="Error while creating a domain model",
                traceback=str(e)
            )

        try:
            stmt = update(self.model).where(self.model.id == instance_id).values(**to_update)
            await session.execute(stmt)
            await session.commit()

        except IntegrityError as e:
            raise DBError(
                message="Integrity error",
                traceback=str(e)
            )

        except NoReferenceError as e:
            raise DBError(
                message="Invalid ForeignKey reference",
                traceback=str(e)
            )

    async def delete(self,
                     session: AsyncSession,
                     instance_id: int | str,
                     ) -> None:
        async with session.begin():
            instance = await self.get_all(session=session, id=instance_id)
            if not instance:
                raise NotFoundError
            await session.delete(instance)
        try:
            await session.delete(instance)
            await session.commit()
        except NoSuchTableError as e:
            raise DBError(
                message=f"Table {self.model} does not exist",
                traceback=str(e)
            )

    async def commit(self, session: AsyncSession):
        try:
            await session.commit()
        except Exception:
            logger.error("Error while commiting session", exc_info=True)


