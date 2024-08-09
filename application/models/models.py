from uuid import uuid4
from sqlalchemy import (
    func,
    ForeignKey,
    UniqueConstraint,
    Date,
    String,
    Double,
    UUID,
    BIGINT,
    Computed,
    DateTime,
    Index
)
import uuid
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship, DeclarativeBase, declared_attr, validates,
)
from datetime import date, datetime
from typing_extensions import Literal
from application.models.mixins import FirstLastNameValidationMixin, TimestampMixin

__all__ = (
    "Base",
    "User",
    "Book",
    "Order",
    "BookOrderAssoc",
    "Author",
    "Publisher",
    "Image",
    "Category",
    "ShoppingSession",
    "CartItem",
    "PaymentDetail"
)

Gender = Literal["male", "female"]


class Base(DeclarativeBase):
    __abstract__ = True

    type_annotation_map = {
        int: BIGINT,
        float: Double
    }

    @declared_attr.directive
    def __tablename__(self):
        return f"{self.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(unique=True)


class Book(Base):
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    isbn: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str]
    description: Mapped[str | None]
    price_per_unit: Mapped[float]
    price_with_discount: Mapped[float] = mapped_column(Double, Computed("price_per_unit - (price_per_unit * (discount*0.01))"))
    number_in_stock: Mapped[int]
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    rating: Mapped[float | None]
    discount: Mapped[int | None]

    # relationships
    images: Mapped[list["Image"]] = relationship(back_populates="book")
    book_details: Mapped[list["BookOrderAssoc"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    publishers: Mapped[list["Publisher"]] = relationship(back_populates="books")
    authors: Mapped[list["Author"]] = relationship(back_populates="books")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="book")

    @validates("price_per_unit")
    def validate_price_per_unit(self, key, price_per_unit):
        if price_per_unit < 1:
            raise ValueError(
                "Minimum price per unit is 1"
            )
        return price_per_unit

    @validates("id")
    def validate_id(self, key, id: str):
        try:
            uuid.UUID(id)
        except ValueError:
            raise ValueError(
                "Incorrect uuid"
            )
        return True

    def __repr__(self):
        return f"""
        Book(
        isbn={self.isbn},
        name={self.name},
        description={self.description[:30]},
        price_per_unit={self.price_per_unit},
        price_with_discount={self.price_with_discount}
        number_in_stock={self.number_in_stock},
        category_id={self.category_id},
        rating={self.rating},
        discount={self.discount}
        )"""


class User(Base, FirstLastNameValidationMixin):
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[Gender] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str]
    registration_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now()
    )
    role_name: Mapped[str | None] = mapped_column(default="user", server_default="user")
    date_of_birth: Mapped[date | None] = mapped_column(Date, server_default=None)

    # relationship
    orders: Mapped[list["Order"] | None] = relationship(back_populates="user",
                                                        cascade="all, delete-orphan")

    shopping_session: Mapped["ShoppingSession"] = relationship(back_populates="user")

    @validates("email")
    def validate_email(self, key, address):
        if "@" not in address or "." not in address:
            raise ValueError(
                "Incorrect email format"
            )
        return address

    def __repr__(self):
        return f"""
        User(
        id={self.id},
        first_name={self.first_name},
        last_name={self.last_name},
        gender: {self.gender},
        email={self.email},
        registration_date={self.registration_date},
        role_name={self.role_name}
        date_of_birth={self.date_of_birth})
                """


class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_status: Mapped[str | None] = mapped_column(default="pending", server_default="pending")
    order_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_sum: Mapped[float | None] = mapped_column(Double)
    payment_id: Mapped[str | None] = mapped_column(ForeignKey("payment_details.id", ondelete="RESTRICT"))


    # relationships
    order_details: Mapped[list["BookOrderAssoc"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )

    payment_detail: Mapped["PaymentDetail"] = relationship(
        back_populates="order",
    )

    user: Mapped["User"] = relationship(back_populates="orders")

    def __repr__(self):
        return f"Order(id={self.id}, user_id={self.user_id}, total_sum={self.total_sum})"


class BookOrderAssoc(Base):

    __table_args__ = (
        UniqueConstraint("order_id", "book_id", name="idx_unique_book_order_key"),
    )

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    count_ordered: Mapped[int] = mapped_column(default=1, server_default="1")

    # realtionships
    book: Mapped["Book"] = relationship(back_populates="book_details")
    order: Mapped["Order"] = relationship(back_populates="order_details")

    def __repr__(self):
        return f"""
                BookOrderAssoc(
                id={self.id},
                order_id={self.order_id},
                book_id={self.book_id},
                count_ordered={self.count_ordered},
                  )
                """


class Author(Base, FirstLastNameValidationMixin):
    first_name: Mapped[str]
    last_name: Mapped[str]

    book_id: Mapped[str | None] = mapped_column(ForeignKey("books.id", ondelete="SET NULL"))

    books: Mapped[list["Book"]] = relationship(back_populates="authors")

    def __repr__(self):
        return f"""
            Author(
            author_id={self.id},
            author_first_name={self.first_name},
            author_last_name={self.last_name}
            )
            """


class Publisher(Base, FirstLastNameValidationMixin):
    first_name: Mapped[str]
    last_name: Mapped[str]

    book_id: Mapped[str | None] = mapped_column(ForeignKey("books.id", ondelete="SET NULL"))

    # relationships
    books: Mapped[list["Book"]] = relationship(back_populates="publishers")

    def __repr__(self):
        return f"""
            Author(
            publisher_id={self.id},
            publisher_first_name={self.first_name},
            publisher_last_name={self.last_name}
            )
            """


class ShoppingSession(Base, TimestampMixin):
    __tablename__ = "shopping_sessions"

    __table_args__ = (
        Index("idx_expiration_time", "expiration_time")
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), unique=True)
    total: Mapped[float | None]
    expiration_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="shopping_session")
    cart_item: Mapped["ShoppingSession"] = relationship(back_populates="shopping_session")


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("session_id", "book_id", name="idx_unique_book_session_key"),
    )

    session_id: Mapped[str] = mapped_column(ForeignKey("shopping_sessions.id", ondelete="CASCADE"))
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id", ondelete="RESTRICTED"))
    quantity: Mapped[int]

    book: Mapped["Book"] = relationship(back_populates="cart_items")
    shopping_session: Mapped["ShoppingSession"] = relationship(back_populates="cart_item")


class PaymentDetail(Base, TimestampMixin):
    __tablename__ = "payment_details"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="RESTRICT"), unique=True)
    status: Mapped[str] = mapped_column(server_default="pending", default="pending")
    payment_provider: Mapped[str | None]
    amount: Mapped[float] = mapped_column(default=0.0, server_default="0.0")

    order: Mapped["Order"] = relationship(back_populates="payment_detail")


class Image(Base):
    book_id: Mapped[str | None] = mapped_column(ForeignKey("books.id"))
    url: Mapped[str | None]

    book: Mapped["Book"] = relationship(back_populates="images")

    def __repr__(self):
        return f"Image(id={self.id}, book_id={self.book_id}, url={self.url})"
