from sqlalchemy import select, update, ResultProxy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from logger import logger
from core.exceptions.storage_exceptions import (
    DuplicateError,
    DBError, NotFoundError
)
from sqlalchemy.exc import NoSuchTableError, NoSuchColumnError, NoReferenceError
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
            logger.error(
                "Model resolution error: Error while creating a domain model"
            )
            raise DBError("Error while creating a domain model")

        try:
            session.add(to_add)
            await session.commit()
        except NoSuchTableError:
            extra = {"model": self.model, "domain_model": domain_model}
            logger.error(f"Creation error: Error while creating {self.model.__name__}: Table does not exist",
                         extra=extra,
                         exc_info=True)
            raise DBError(f"Table for {self.model} does not exist")

        except NoSuchColumnError as e:
            logger.error(f"Creation error: Error while creating {self.model.__name__}: Column does not exist", extra=e,
                         exc_info=True)
            raise DBError("Unable to create instance due to server error")

        except IntegrityError as e:
            logger.error(f"Creation error: Error while creating {self.model.__name__}: unique violation level: {e}")
            raise DuplicateError(entity=self.model.__name__)

        except NoReferenceError:
            logger.error(
                f"Creation error: Error while creating {self.model}: Invalid ForeignKey reference in the model",
                domain_model,
                exc_info=True
            )
            raise DBError

    async def get_all(
            self,
            session: AsyncSession,
            page: int = 0,
            limit: int = 5,
            **filters
    ) -> list:
        stmt = select(self.model).filter_by(**filters).offset(page * limit).limit(limit)
        print("IN REPO GET_ALL")
        try:
            domain_models: list | [] = (await session.scalars(stmt)).all()
        except NoSuchTableError:
            extra = {"model": self.model}
            logger.error(
                f"Creation error: Error while creating {self.model}: Table does not exist", extra=extra,
                exc_info=True
            )
            raise DBError(f"Table for {self.model} does not exist")

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
            logger.error(
                "Model resolution error: Error while converting to SQLAlchemy model"
            )
            raise DBError("Error while creating a domain model")

        try:
            stmt = update(self.model).where(self.model.id == instance_id).values(**to_update)
            await session.execute(stmt)
            await session.commit()

        except IntegrityError:
            logger.error(
                f"Update error: Unable to add update due to database conflict (likely that entity does not exist)",
                domain_model,
                exc_info=True
            )
            raise DBError

        except NoReferenceError:
            logger.error(
                f"Update error: Error while updating {self.model.__name__}: Invalid ForeignKey reference in the model",
                domain_model,
                exc_info=True
            )
            raise DBError

    async def delete(self,
                     session: AsyncSession,
                     instance_id: int | str,
                     ) -> None:
        try:
            instance = await self.get_all(session=session, id=instance_id)
        except IndexError:
            logger.warning("Trying to delete entity that doesn't exist")
            raise NotFoundError(entity=self.model.__name__)

        try:
            await session.delete(instance)
            await session.commit()
        except NoSuchTableError:
            extra = {"model": self.model, "instance_id": instance_id}
            logger.error(f"Deletion error: Error while deleting {self.model.__name__}: Table does not exist",
                         extra=extra,
                         exc_info=True)
            raise DBError(f"Table for {self.model.__name__} does not exist")

    async def commit(self, session: AsyncSession):
        try:
            await session.commit()
        except Exception:
            logger.error("Error while commiting session", exc_info=True)


