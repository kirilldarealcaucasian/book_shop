from datetime import timedelta

from fastapi import Depends, status, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from main.services import (
    UserService
)
from core.db_conf import db_config

from main.schemas import (UpdateUserS,
                          UpdatePartiallyUserS,
                          ReturnUserS, ReturnUserWithOrderS
                          )
from auth.services import PermissionService
from core import AbstractService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", status_code=status.HTTP_200_OK,
            response_model=list[ReturnUserS] | None,
            dependencies=[Depends(PermissionService.get_admin_permission)]
            )
async def get_all_users(
        service: UserService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session)


@router.get("/{user_id}",
            status_code=status.HTTP_200_OK,
            response_model=list[ReturnUserS] | None,
            dependencies=[Depends(PermissionService.get_admin_permission)])
@AbstractService.cachify(ReturnUserS, cache_time=timedelta(seconds=10))
async def get_user_by_id(
        user_id: int,
        service: UserService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session, id=user_id)


@router.get("/orders/{user_id}", status_code=status.HTTP_200_OK,
            response_model=ReturnUserWithOrderS)
async def get_user_with_orders(
        user_id: int,
        service: UserService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_user_with_orders(session=session, user_id=user_id)


@router.delete('/{user_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               response_model=None,
               dependencies=[Depends(PermissionService.get_admin_permission)]
               )
async def delete_user(
        user_id: int,
        service: UserService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.delete(session=session, instance_id=user_id)


@router.put('/{user_id}', dependencies=[Depends(PermissionService.get_admin_permission)])
async def update_user(
        user_id: int,
        update_data: UpdateUserS,
        service: UserService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update(
        session=session,
        instance_id=user_id,
        data=update_data
    )


@router.patch('/{user_id}', dependencies=[Depends(PermissionService.get_admin_permission)])
async def update_user_partially(
        user_id: int,
        update_data: UpdatePartiallyUserS,
        service: UserService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update(
        session=session,
        instance_id=user_id,
        data=update_data
    )


