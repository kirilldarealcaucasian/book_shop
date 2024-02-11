import json
from datetime import timedelta
from functools import wraps
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract_repository import AbstractRepository
from typing import TypeVar, Generic, Callable
from main.schemas import (CreateProductS,
                          CreateCategoryS,
                          CreateOrderS,
                          CreateImageS,
                          RegisterUserS,
                          UpdateProductS,
                          UpdateCategoryS,
                          UpdateOrderS,
                          UpdateUserS,
                          UpdatePartiallyProductS,
                          UpdatePartiallyUserS,
                          ReturnProductS,
                          ReturnCategoryS,
                          ReturnOrderS,
                          ReturnUserS,
                          ReturnImageS
                          )

CreateDataT = TypeVar("CreateDataT", CreateProductS, CreateCategoryS, CreateOrderS, RegisterUserS, CreateImageS)
UpdateDataT = TypeVar("UpdateDataT", UpdateProductS, UpdateCategoryS, UpdateOrderS, UpdateUserS)
PartialUpdateDataT = TypeVar("PartialUpdateDataT", UpdatePartiallyProductS, UpdatePartiallyUserS)
ReturnDataT = TypeVar("ReturnDataT", ReturnProductS, ReturnCategoryS, ReturnOrderS, ReturnUserS, ReturnImageS)


class AbstractService(Generic[CreateDataT, UpdateDataT, PartialUpdateDataT, ReturnDataT]):
    __slots__ = ("repository",)

    def __init__(self, repository: AbstractRepository):
        self.repository = repository

    async def create(self, session: AsyncSession, data: CreateDataT) -> None:
        return await self.repository.create(data=data.model_dump(), session=session)

    async def update(self,
                     session: AsyncSession,
                     instance_id,
                     data: UpdateDataT | PartialUpdateDataT
                     ) -> None:

        fixed_data = data.model_dump(exclude_unset=True)
        return await self.repository.update(instance_id=instance_id,
                                            data=fixed_data,
                                            session=session,
                                            )

    async def get_all(self, session: AsyncSession, **filters) -> list[ReturnDataT]:
        return await self.repository.get_all(**filters, session=session)

    async def delete(self, session: AsyncSession, instance_id: int) -> None:
        return await self.repository.delete(instance_id=instance_id, session=session)

    @staticmethod
    def cachify(instance_return_schema, cache_time: timedelta | int) -> Callable:
        """Endpoint cache decorator"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> list[instance_return_schema]:
                from main.ma1n import redis
                try:
                    await redis.ping()
                except Exception:
                    return await func(*args, **kwargs)

                key = list(kwargs)[2]
                instance_id: int = kwargs[key]
                instance = await redis.get(str(instance_id))

                if instance:
                    return [json.loads(instance)]  # return value from redis
                else:
                    retrieved_instance = (await func(*args, **kwargs))[0]
                    retrieved_instance_adapter = TypeAdapter(type=instance_return_schema)
                    final_instance: dict = (
                        retrieved_instance_adapter  # validate retrieved model to match pydantic schema
                        .validate_python(retrieved_instance).model_dump())
                    await redis.set(instance_id, json.dumps(final_instance))  # save value to redis
                    await redis.expire(name=str(instance_id), time=cache_time)
                    return [retrieved_instance]
            return wrapper
        return decorator
