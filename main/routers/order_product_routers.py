from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_config
from main.schemas import ReturnOrderProductS
from main.services import OrderService

from core import AbstractService

router = APIRouter(prefix="/order", tags=["Orders & Products"])


@router.get("/{order_id}", response_model=ReturnOrderProductS)
async def get_order_with_products(
        order_id: int,
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await OrderService.get_order_with_products(session=session, instance_id=order_id)


@router.get("/{order_id}/product{product_id}/{quantity}", status_code=status.HTTP_200_OK)
async def add_product_to_order(
        order_id: int,
        product_id: int,
        quantity: int = 1,
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency),
        service: OrderService = Depends()
):
    return await service.add_product_to_order(
        session=session,
        product_id=product_id,
        order_id=order_id,
        quantity=quantity
    )


@router.delete("/{order_id}/product{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_from_order(
        order_id: int,
        product_id: int,
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency),
        service: OrderService = Depends()
):
    return await service.delete_product_from_order(
        session=session,
        product_id=product_id,
        order_id=order_id)

