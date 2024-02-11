import os
from collections import namedtuple
from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from core import AbstractService
from ..schemas import CreateImageS, ReturnImageS, ReturnOrderProductS, ReturnUserWithOrderS
from ..repositories import (
    CategoryRepository,
    ImageRepository,
    OrderRepository,
    UserRepository,
    ProductRepository,

)
from ..helpers import construct_url, fix_image_dimensions
from PIL import Image, UnidentifiedImageError

__all__ = [
    "CategoryService",
    "ImageService",
    "OrderService",
    "UserService",
    "ProductService",
    "AbstractService",
]


class CategoryService(AbstractService):
    def __init__(self, repository: CategoryRepository = Depends()):
        super().__init__(repository)


class ImageService(AbstractService):
    def __init__(self, repository: ImageRepository = Depends()):
        super().__init__(repository)


    async def upload_image(self,
                           session: AsyncSession,
                           image: UploadFile,
                           product_id: int
                           ):
        image_fixed: namedtuple = fix_image_dimensions(image=image)
        image_format: str = image_fixed.image_format
        img_resource: Image = image_fixed.img_resource
        urls: namedtuple = construct_url(format=image_format, name=str(product_id))
        if urls:
            try:
                os.mkdir(urls.folder_url)
            except FileExistsError:
                img_resource.save(urls.image_url)
                await self.create(session=session,
                                  data=CreateImageS(product_id=product_id,
                                                    url=urls.image_url)
                                  )
                return
            try:
                img_resource.save(urls.image_url)
            except UnidentifiedImageError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong while uploading image"
                )
            await self.create(session=session,
                              data=CreateImageS(product_id=product_id,
                                                url=urls.image_url)
                              )
            return
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Unacceptable file format"
        )

    async def delete_image(self,
                           session: AsyncSession,
                           image_id: int
                           ):
        image: list[ReturnImageS] = await self.repository.get_all(session=session, id=image_id)
        image_url: str = image[0].url
        await self.repository.delete(session=session, instance_id=image[0].id)
        try:
            os.remove(image_url)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File you're trying to remove does not exist"
            )


class OrderService(AbstractService):
    def __init__(self, repository: OrderRepository = Depends()):
        super().__init__(repository)

    @staticmethod
    async def get_order_with_products(
            session: AsyncSession,
            instance_id: int,

    ) -> ReturnOrderProductS:
        return await OrderRepository.get_order_with_products(session=session,
                                                             order_id=instance_id)

    @staticmethod
    async def add_product_to_order(
            session: AsyncSession,
            product_id: int,
            order_id: int,
            quantity: int
    ) -> None:
        return await OrderRepository.add_product_to_order(
            session=session,
            product_id=product_id,
            order_id=order_id,
            quantity=quantity
        )


    @staticmethod
    async def delete_product_from_order(
            session: AsyncSession,
            product_id: int,
            order_id: int,
    ) -> None:
        return await OrderRepository.delete_product_from_order(
            session=session,
            product_id=product_id,
            order_id=order_id
        )


class UserService(AbstractService):
    def __init__(self, repository: UserRepository = Depends()):
        super().__init__(repository)

    @staticmethod
    async def get_user_with_orders(
                                   session: AsyncSession,
                                   user_id: int
                                   ) -> ReturnUserWithOrderS:
        return await UserRepository.get_user_with_orders(
            session=session,
            user_id=user_id
        )


class ProductService(AbstractService):
    def __init__(self, repository: ProductRepository = Depends()):
        super().__init__(repository)



