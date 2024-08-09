from uuid import UUID
from fastapi import Depends, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from auth.services.permission_service import PermissionService
from application.services import BookService
from infrastructure.postgres import db_client
from application.schemas import (ReturnBookS,
                                 CreateBookS,
                                 UpdateBookS,
                                 UpdatePartiallyBookS
                                 )
from core.utils.cache import cachify
from datetime import timedelta
from application.schemas import BookFilterS


router = APIRouter(prefix="v1/books", tags=["Books CRUD"])


@router.get("", status_code=status.HTTP_200_OK, response_model=list[ReturnBookS] | None)
async def get_all_books(
        filters: BookFilterS = Depends(),
        service: BookService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.get_all_books(session=session, filters=filters)


@router.get("/{book_id}",
            status_code=status.HTTP_200_OK,
            response_model=list[ReturnBookS],
            )
@cachify(ReturnBookS, cache_time=timedelta(seconds=10))
async def get_book_by_id(
        book_id: str,
        service: BookService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency),
):
    return await service.get_book_by_id(session=session, id=book_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_book(
        data: CreateBookS,
        service: BookService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.create_book(session=session, dto=data)


@router.delete('/{book_id}',
               status_code=status.HTTP_204_NO_CONTENT,
               response_model=None,
               )
async def delete_book(
        book_id: UUID,
        service: BookService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.delete_book(session=session, book_id=str(book_id))


@router.put('/{book_id}', status_code=status.HTTP_200_OK)
async def update_book(
        book_id: UUID,
        update_data: UpdateBookS,
        service: BookService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.update_book(
        session=session,
        book_id=str(book_id),
        data=update_data
    )


@router.patch('/{book_id}', status_code=status.HTTP_200_OK)
async def update_book_partially(
        book_id: UUID,
        update_data: UpdatePartiallyBookS,
        service: BookService = Depends(),
        session: AsyncSession = Depends(db_client.get_scoped_session_dependency)
):
    return await service.update_book(
        session=session,
        book_id=str(book_id),
        data=update_data
    )
