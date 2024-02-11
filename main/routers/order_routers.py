from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.db_conf import db_config
from main.schemas import CreateOrderS, ReturnOrderS, UpdateOrderS
from main.services import OrderService
from core import AbstractService


router = APIRouter(prefix="/orders", tags=["Orders CRUD"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReturnOrderS] | None)
async def get_all_orders(
        service: OrderService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session)


@router.get("/{order_id}",
            status_code=status.HTTP_200_OK,
            response_model=list[ReturnOrderS] | None)
@AbstractService.cachify(ReturnOrderS, cache_time=timedelta(seconds=10))
async def get_order_by_id(
        order_id: int,
        service: OrderService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session, id=order_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_order(
        data: CreateOrderS,
        service: OrderService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.create(session=session, data=data)


@router.delete('/{order_id}', status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_order(
        order_id: int,
        service: OrderService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.delete(session=session, instance_id=order_id)


@router.put('/{order_id}')
async def update_order(
        product_id: int,
        update_data: UpdateOrderS,
        service: OrderService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update(
        session=session,
        instance_id=product_id,
        data=update_data
    )


