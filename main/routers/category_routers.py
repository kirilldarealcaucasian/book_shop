from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.db_conf import db_config
from main.schemas import ReturnCategoryS, CreateCategoryS, UpdateCategoryS
from main.services import CategoryService
from auth.services import PermissionService
from core import AbstractService

router = APIRouter(prefix="/categories", tags=["Categories CRUD"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReturnCategoryS] | None)
async def get_all_categories(
        service: CategoryService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session)


@router.get("/{category_id}",
            status_code=status.HTTP_200_OK,
            response_model=list[ReturnCategoryS] | None)
@AbstractService.cachify(ReturnCategoryS, cache_time=timedelta(seconds=10))
async def get_category_by_id(
        category_id: int,
        service: CategoryService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session, id=category_id)


@router.post('/', status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(PermissionService.get_admin_permission)]
             )
async def create_category(
        data: CreateCategoryS,
        service: CategoryService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
) -> None:
    return await service.create(session=session, data=data)


@router.delete('/{category_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(PermissionService.get_admin_permission)]
               )
async def delete_category(
        category_id: int,
        service: CategoryService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
) -> None:
    return await service.delete(session=session, instance_id=category_id)


@router.put('/{category_id}', dependencies=[Depends(PermissionService.get_admin_permission)])
async def update_category(
        product_id: int,
        update_data: UpdateCategoryS,
        service: CategoryService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update(
        session=session,
        instance_id=product_id,
        data=update_data
    )
