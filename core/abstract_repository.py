from abc import ABC

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status


class AbstractRepository(ABC):
    model = None

    async def create(self,
                     session: AsyncSession,
                     data: dict,
                     ):
        to_add = self.model(**data)
        try:
            session.add(to_add)
            await session.commit()
            return
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to add data due to database conflict (likely that entity does not exist)"
            )


    async def get_all(self,
                      session: AsyncSession,
                      **filters
                      ):

        stmt = select(self.model).filter_by(**filters)
        try:
            res = (await session.scalars(stmt)).all()
            if not res:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entity you're trying to retrieve does not exist"
                )
            return res
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Unable to add data due to database conflict (likely that entity does not exist)"
                                )


    async def update(self,
                     data: dict,
                     instance_id: int,
                     session: AsyncSession,
                     ) -> None:
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You didn't send any data"
            )
        try:
            stmt = update(self.model).where(self.model.id == instance_id).values(**data)
            await session.execute(stmt)
            await session.commit()

        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to add data due to database conflict (likely that entity does not exist)"
            )

    async def delete(self,
                     session: AsyncSession,
                     instance_id: int,
                     ):
        instance = await self.get_all(session=session, id=instance_id)
        await session.delete(instance[0])
        await session.commit()


