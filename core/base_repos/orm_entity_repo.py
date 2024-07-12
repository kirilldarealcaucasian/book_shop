from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from logger import logger
from core.exceptions import RelatedEntityDoesNotExist, ServerError, EntityDoesNotExist, DuplicateError
from sqlalchemy.exc import NoSuchTableError, NoSuchColumnError, NoReferenceError


class OrmEntityRepository:
    model = None

    async def create(self,
                     session: AsyncSession,
                     data: dict,
                     ) -> None:
        to_add = self.model(**data)
        try:
            session.add(to_add)
            await session.commit()

        except NoSuchTableError:
            extra = {"model": self.model, "data": data}
            logger.error(f"Creation error: Error while creating {self.model.__name__}: Table does not exist",
                         extra=extra,
                         exc_info=True)
            raise ServerError(f"Table for {self.model} does not exist")

        except NoSuchColumnError as e:
            logger.error(f"Creation error: Error while creating {self.model.__name__}: Column does not exist", extra=e,
                         exc_info=True)
            raise ServerError("Unable to create instance due to server error")

        except IntegrityError as e:
            logger.error(f"Creation error: Error while creating {self.model.__name__}: unique violation level: {e}")
            raise DuplicateError(entity=self.model.__name__)

        except NoReferenceError:
            logger.error(
                f"Creation error: Error while creating {self.model}: Invalid ForeignKey reference in the model",
                data,
                exc_info=True
            )
            raise RelatedEntityDoesNotExist

    async def get_all(self,
                      session: AsyncSession,
                      page: int = 0,
                      limit: int = 5,
                      **filters
                      ) -> list:
        stmt = select(self.model).filter_by(**filters).offset(page * limit).limit(limit)

        try:
            res: list | [] = (await session.scalars(stmt)).all()
            print("RES: ", res)
            if len(res) == 1:
                return res[0]
        except NoSuchTableError:
            extra = {"model": self.model}
            logger.error(f"Creation error: Error while creating {self.model}: Table does not exist", extra=extra,
                         exc_info=True)
            raise ServerError(f"Table for {self.model} does not exist")

        if not res:
            raise EntityDoesNotExist(entity=self.model.__name__)

        return list(res)

    async def update(
            self,
            data: dict,
            instance_id: str | int,
            session: AsyncSession,
    ) -> None:

        if not data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unprocessable entity"
            )

        _ = await self.get_all(session=session, id=instance_id)  # check existence of the entity

        try:
            stmt = update(self.model).where(self.model.id == instance_id).values(**data)
            await session.execute(stmt)
            await session.commit()

        except IntegrityError:
            logger.error(f"Update error: Error while updating {self.model.__name__} due to Integrity error", data,
                         exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to add data due to database conflict (likely that entity does not exist)"
            )

        except NoReferenceError:
            logger.error(
                f"Update error: Error while updating {self.model.__name__}: Invalid ForeignKey reference in the model",
                data,
                exc_info=True
            )
            raise RelatedEntityDoesNotExist

    async def delete(self,
                     session: AsyncSession,
                     instance_id: int | str,
                     ) -> None:

        try:
            instance = await self.get_all(session=session, id=instance_id)
        except IndexError:
            raise EntityDoesNotExist(entity=self.model.__name__)

        try:
            await session.delete(instance)
            await session.commit()

        except NoSuchTableError:
            extra = {"model": self.model, "instance_id": instance_id}
            logger.error(f"Deletion error: Error while deleting {self.model.__name__}: Table does not exist",
                         extra=extra,
                         exc_info=True)
            raise ServerError(f"Table for {self.model.__name__} does not exist")

    async def commit(self, session: AsyncSession):
        try:
            await session.commit()
        except Exception:
            logger.error("Error while commiting session", exc_info=True)