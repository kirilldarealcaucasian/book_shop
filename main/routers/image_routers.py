from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.db_conf import db_config
from main.services import ImageService


router = APIRouter(prefix="/images", tags=["Images"])


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_all_images(
        product_id: int,
        service: ImageService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
):
    return await service.get_all(session=session, product_id=product_id)


@router.post('/product/{product_id}', status_code=status.HTTP_201_CREATED)
async def create_image(
        file: UploadFile,
        product_id: int,
        service: ImageService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
) -> None:
    return await service.upload_image(session=session,
                                      image=file, product_id=product_id)


@router.delete('/product/{image_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
        image_id: int,
        service: ImageService = Depends(),
        session: AsyncSession = Depends(db_config.get_scoped_session_dependency)
) -> None:
    return await service.delete_image(session=session,
                                      image_id=image_id,

                                      )

