from sqlalchemy import Boolean, TIMESTAMP, func, ForeignKey, UniqueConstraint, Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship, DeclarativeBase, declared_attr, validates,
)
from datetime import datetime



class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self):
        return str(self)


class User(Base):
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    registration_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    orders: Mapped[list["Order"] | None] = relationship(back_populates="user")

    @validates("email")
    def validate_email(self, key, address):
        if "@" not in address or "." not in address:
            raise ValueError(
                "Incorrect email format"
            )
        return address


    def __str__(self):
        return f"""
        User(
        id={self.id},
        name={self.name}, 
        email={self.email}, 
        is_admin={self.is_admin},
        registration_date={self.registration_date})
                """


class Category(Base):
    __tablename__ = "categories"
    name: Mapped[str]

    product: Mapped["Product"] = relationship(back_populates="categories")

    def __str__(self):
        return f"Category(id={self.id}, name={self.name})"


class Product(Base):
    name: Mapped[str]
    description: Mapped[str]
    price_per_unit: Mapped[int]
    number_in_stock: Mapped[int]
    image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id"), unique=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id")
    )

    images: Mapped[list["Image"]] = relationship(back_populates="product")
    categories: Mapped[list["Category"] | None] = relationship(back_populates="product")
    product_details: Mapped[list["ProductOrderAssoc"]] = relationship(
        back_populates="product"
    )

    def __str__(self):
        return f"""
        Product(id={self.id}, 
        name={self.name}
        description={self.description},
        price_per_unit={self.price_per_unit},
        number_in_stock={self.number_in_stock},
        )"""


class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    order_details: Mapped[list["ProductOrderAssoc"]] = relationship(
        back_populates="order"
    )
    user: Mapped["User"] = relationship(back_populates="orders")


    def __str__(self):
        return f"Order(id={self.id}, user_id={self.user_id}, order_details={self.order_details})"


class ProductOrderAssoc(Base):
    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="product_order_key"),
    )
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    count_ordered: Mapped[int] = mapped_column(default=1, server_default="1")

    product: Mapped["Product"] = relationship(back_populates="product_details")
    order: Mapped["Order"] = relationship(back_populates="order_details")

    def __str__(self):
        return f"""
        ProductOrderAssoc(
        id={self.id},
        order_id={self.order_id},
        product_id={self.product_id},
        count_ordered={self.count_ordered},
        product={self.product},
        order={self.order}
          )
        """

    def __repr__(self):
        return f"""
                ProductOrderAssoc(
                id={self.id},
                order_id={self.order_id},
                product_id={self.product_id},
                count_ordered={self.count_ordered},
                  )
                """


class Image(Base):
    product_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    url: Mapped[str]

    product: Mapped["Product"] = relationship(back_populates="images")

    def __str__(self):
        return f"Image(id={self.id}, product_id={self.product_id}, url={self.url})"
