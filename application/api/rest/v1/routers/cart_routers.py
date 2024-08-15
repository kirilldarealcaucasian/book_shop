from datetime import timedelta
from fastapi import APIRouter, Depends, status, Body, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from application.services.cart_service import CartService
from infrastructure.postgres import db_client
from application.schemas import ReturnOrderS, AddBookToCartS, ReturnCartS
from core.utils.cache import cachify
from auth.services.permission_service import PermissionService
from uuid import UUID


router = APIRouter(prefix="/v1/cart", tags=["Cart"])

@router.get(
    "/session/{session_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReturnCartS
)
async def get_cart_by_session_id(
        session_id:  UUID,
        service: CartService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency),
):
    return await service.get_cart_by_session_id(
        session=session,
        cart_session_id=session_id
    )


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK
)
async def get_cart_by_user_id(
        user_id: int,
        service: CartService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency),
):
    return await service.get_cart_by_user_id(
        session=session,
        user_id=user_id
    )


@router.post(
    '/{user_id}',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionService().get_authorized_permission)]
)
async def create_cart(
        user_id: str | int,
        service: CartService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.create_cart(session=session, user_id=user_id)


@router.delete(
    '/',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionService().get_order_permission)]
)
async def delete_cart(
        user_id: int | str,
        cart_session_id: UUID = Cookie(None),
        service: CartService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.delete_cart(
        session=session,
        cart_session_id=cart_session_id
    )


@router.post(
    '/items',
    dependencies=[Depends(PermissionService().get_order_permission)],
    status_code=status.HTTP_200_OK,
)
async def add_book_to_cart(
        data: AddBookToCartS,
        cart_session_id: UUID = Cookie(None),
        service: CartService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.add_book_to_cart(
        session=session,
        dto=data,
        session_id=cart_session_id
    )


@router.delete("/items", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_from_cart(
        book_id: UUID = Body(),
        cart_session_id: UUID = Cookie(None),
        service: CartService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
) -> None:
    return await service.delete_book_from_cart(
        session=session,
        book_id=book_id,
        cart_session_id=cart_session_id
    )


