from datetime import timedelta

from fastapi import Depends, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services.permission_service import PermissionService
from core import db_config
from core.utils.cache import cachify
from application.schemas import (
    ReturnAuthorS,
    UpdateAuthorS,
    UpdatePartiallyAuthorS,
    CreateAuthorS
)
from application.services import AuthorService

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReturnAuthorS] | None)
async def get_all_authors(
        service: AuthorService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all_authors(session=session)


@router.get("/{author_id}",
            status_code=status.HTTP_200_OK,
            response_model=list[ReturnAuthorS] | None,
            dependencies=[Depends(PermissionService.get_admin_permission)]
            )
@cachify(ReturnAuthorS, cache_time=timedelta(seconds=10))
async def get_author_by_id(
        author_id: int,
        service: AuthorService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency),
):
    return await service.get_authors_by_filters(session=session, author_id=author_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_author(
        data: CreateAuthorS,
        service: AuthorService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.create_author(session=session, dto=data)


@router.delete('/{author_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               response_model=None,
               )
async def delete_author(
        author_id: int,
        service: AuthorService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.delete_author(session=session, author_id=author_id)


@router.put('/{author_id}', status_code=status.HTTP_200_OK)
async def update_author(
        author_id: int,
        update_data: UpdateAuthorS,
        service: AuthorService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update_author(
        session=session,
        author_id=author_id,
        data=update_data
    )


@router.patch('/{author_id}', status_code=status.HTTP_200_OK)
async def update_author_partially(
        author_id: int,
        update_data: UpdatePartiallyAuthorS,
        service: AuthorService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.update_author(
        session=session,
        author_id=author_id,
        data=update_data
    )
