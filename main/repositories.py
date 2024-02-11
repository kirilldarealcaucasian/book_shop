from fastapi import HTTPException, status
from sqlalchemy import select, ScalarResult, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from core import AbstractRepository
from main.schemas import ReturnUserWithOrderS
from collections import defaultdict
from main.schemas.product_order_schemas import (ReturnOrderIdProductS,
                                                ReturnOrderProductS,
                                                AssocProductS
                                                )
from models import Category, User, Order, Image, Product, ProductOrderAssoc

__all__ = [
    "CategoryRepository",
    "ImageRepository",
    "OrderRepository",
    "UserRepository",
]


class CategoryRepository(AbstractRepository):
    model: Category = Category


class ImageRepository(AbstractRepository):
    model: Image = Image


class OrderRepository(AbstractRepository):
    model: Order = Order

    @staticmethod
    async def get_order_with_products(session: AsyncSession, order_id: int):
        stmt = (select(Order)
                .where(Order.id == order_id)
                .options(selectinload(Order.order_details)
                         .joinedload(ProductOrderAssoc.product)
                         )
                )
        order_res: Result = await session.execute(stmt)
        order: Order = order_res.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order was not found"
            )
        order_details: list[ProductOrderAssoc] = order.order_details

        return_product_arr = []
        for product in order_details:
            return_product_arr.append(AssocProductS(name=product.product.name,
                                                    price_per_unit=product.product.price_per_unit,
                                                    number_in_stock=product.product.number_in_stock,
                                                    count_ordered=product.count_ordered
                                                    )
                                      )
        return ReturnOrderProductS(
            products=return_product_arr
        )

    @staticmethod
    async def add_product_to_order(
            session: AsyncSession,
            order_id: int,
            product_id: int,
            quantity: int
    ):
        prod_res: ScalarResult = await session.scalars(select(Product)
                                                       .where(Product.id == product_id))
        product: Product = prod_res.one_or_none()

        if quantity > product.number_in_stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"""You're trying to order too many products, only {product.number_in_stock} left in stock"""
            )

        stmt = select(Order).where(Order.id == order_id) \
            .options(selectinload(Order.order_details))
        order_res: ScalarResult = (await session.scalars(stmt))
        order: Order = order_res.one_or_none()

        if not product or not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product / Order (both) was not found")
        try:
            order.order_details.append(ProductOrderAssoc(
                product=product,
                count_ordered=quantity))
            product.number_in_stock -= quantity
            await session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The product you are trying to add already exists in the order"
            )

    @staticmethod
    async def delete_product_from_order(session: AsyncSession, product_id: int, order_id: int):
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.order_details))
        order: Order = (await session.scalars(stmt)).one_or_none()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order was not found")

        for product in order.order_details:
            if product.product_id == product_id:
                await session.delete(product)
                await session.commit()
                return

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such product in the order"
        )


class UserRepository(AbstractRepository):
    model: User = User

    @staticmethod
    async def get_user_with_orders(
            session: AsyncSession,
            user_id: int
    ) -> ReturnUserWithOrderS:
        stmt = select(User).where(User.id == user_id) \
            .options(selectinload(User.orders)
            .options(selectinload(Order.order_details)
            .options(selectinload(ProductOrderAssoc.product))
                     ))
        user: User = (await session.scalars(stmt)).one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User was not found"
            )

        orders_dict = defaultdict(list)

        for order in user.orders:
            for order_detail in order.order_details:
                product = AssocProductS(
                    name=order_detail.product.name,
                    price_per_unit=order_detail.product.price_per_unit,
                    number_in_stock=order_detail.product.number_in_stock,
                    count_ordered=order_detail.count_ordered)
                orders_dict[order.id].append(product)

        orders = []
        for key, value in orders_dict.items():
            orders.append(
                ReturnOrderIdProductS(
                    order_id=key,
                    products=value
                )
            )

        return ReturnUserWithOrderS(
            orders=orders,
            user_name=user.name,
            email=user.email,

        )



class ProductRepository(AbstractRepository):
    model: Product = Product
