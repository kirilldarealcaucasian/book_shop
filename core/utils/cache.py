import json
from datetime import timedelta
from functools import wraps
from uuid import UUID

from aioredis import Redis
from pydantic import TypeAdapter
from typing import Callable, Union

__all__ = (
    "cachify",
)

from infrastructure.redis import redis_client
from logger import logger


def cachify(instance_return_schema, cache_time: timedelta | int) -> Callable:
    """Endpoint redis-cache decorator function"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> list[instance_return_schema]:
            redis: Redis = await redis_client.connect()

            if not redis:
                logger.info(f"No caching for {func.__name__} as no connection to redis")
                return await func(*args, **kwargs)

            key = list(kwargs)[2]  # retrieve id parameter (it must always be at the 2 place)
            instance_id: Union[int, UUID, str] = kwargs[key]

            instance = await redis.get(str(instance_id))

            if instance:
                print("INSTANCE RETURN SCH: ", instance_return_schema)
                return json.loads(instance)  # return value from redis

            else:
                retrieved_instance = await func(*args, **kwargs)
                retrieved_instance_adapter = TypeAdapter(type=instance_return_schema)
                final_instance: dict = (
                    retrieved_instance_adapter  # validate retrieved model to match given pydantic schema
                    .validate_python(retrieved_instance).model_dump())

                instance_id_to_fix = final_instance["id"]
                logger.debug(msg="instance id", exc_info={"instance_id_to_fix": instance_id_to_fix})

                if instance_id_to_fix and type(instance_id_to_fix) != str:
                    # uuid is not json serializable, so we need to convert it to string
                    del final_instance["id"]
                    final_instance["id"] = str(instance_id_to_fix)

                await redis.set(
                    name=str(instance_id),
                    value=json.dumps(final_instance),
                    ex=cache_time
                )  # save value to redis

                return retrieved_instance

        return wrapper

    return decorator
