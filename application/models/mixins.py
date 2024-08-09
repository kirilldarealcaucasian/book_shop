from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import validates, Mapped, mapped_column, declared_attr

__all__ = (
    "FirstLastNameValidationMixin",
    "TimestampMixin"
)


class FirstLastNameValidationMixin:

    @validates("first_name")
    def validate_first_name(self, key, name):
        if len(name) < 2:
            raise ValueError(
                "First name should be at least 2 characters"
            )
        return name

    @validates("last_name")
    def validate_last_name(self, key, last_name):
        if len(last_name) < 2:
            raise ValueError(
                "Last name should be at least 2 characters"
            )
        return last_name


class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            TIMESTAMP(timezone=True), server_default=func.now(), default=datetime.now()

        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            TIMESTAMP(timezone=True), server_default=func.now(), default=datetime.now()
        )
