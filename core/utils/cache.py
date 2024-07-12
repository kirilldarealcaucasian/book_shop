import json
from datetime import timedelta
from functools import wraps
from pydantic import TypeAdapter
from typing_extensions import Callable


__all__ = (
    "cachify",
)


def cachify(instance_return_schema, cache_time: timedelta | int) -> Callable:
    """Endpoint redis-cache decorator-function"""

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
            print("instance_id: ", instance, "instance: ", instance)

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