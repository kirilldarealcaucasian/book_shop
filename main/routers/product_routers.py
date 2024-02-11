from fastapi import Depends, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services import PermissionService
from main.services import (
    ProductService,
)
from core.db_conf import db_config
from main.schemas import (ReturnProductS,
                          CreateProductS,
                          UpdateProductS,
                          UpdatePartiallyProductS
                          )
from core import AbstractService
from datetime import timedelta

router = APIRouter(prefix="/products", tags=["Products CRUD"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReturnProductS] | None)
async def get_all_products(
        service: ProductService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session)


@router.get("/{product_id}",
            status_code=status.HTTP_200_OK,
            response_model=list[ReturnProductS] | None,
            dependencies=[Depends(PermissionService.get_admin_permission)]
            )
@AbstractService.cachify(ReturnProductS, cache_time=timedelta(seconds=10))
async def get_product_by_id(
        product_id: int,
        service: ProductService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency),
):
    return await service.get_all(session=session, id=product_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(
        data: CreateProductS,
        service: ProductService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.create(session=session, data=data)


@router.delete('/{product_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               response_model=None,
               )
async def delete_product(
        product_id: int,
        service: ProductService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.delete(session=session, instance_id=product_id)


@router.put('/{product_id}', status_code=status.HTTP_200_OK)
async def update_product(
        product_id: int,
        update_data: UpdateProductS,
        service: ProductService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update(
        session=session,
        instance_id=product_id,
        data=update_data
    )


@router.patch('/{product_id}', status_code=status.HTTP_200_OK)
async def update_product_partially(
        product_id: int,
        update_data: UpdatePartiallyProductS,
        service: ProductService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update(
        session=session,
        instance_id=product_id,
        data=update_data
    )

