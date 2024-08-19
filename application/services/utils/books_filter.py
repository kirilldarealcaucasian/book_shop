from typing import Any
from pydantic import BaseModel, UUID4
from sqlalchemy import select, Select
from sqlalchemy.orm import joinedload

from application import Book
from application.models import Category


class BaseFilter(BaseModel):
    def get_filtering_data(self):
        filtering_fields: dict = self.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        print("FILTERING_FIELDS: ", filtering_fields)
        return filtering_fields.items()

    def filter(self, stmt: Select):
        for filter_name, filter_name_value in self.get_filtering_data():
            # example name__ilike=20 --> (name__ilike, 20)

            filter = getattr(self, filter_name, None)
            if isinstance(filter, BaseFilter):
                # case for a nested filter
                stmt = getattr(self, filter_name).filter(stmt)

            if "__" in filter_name:
                field_name, query_operator = filter_name.split("__")  # example name__ilike --> name, ilike
                orm_operator, filter_value = getattr(
                    self.FilterRules,
                    query_operator
                )(filter_name_value)  # use a mapper to get an orm operator and a filter value
                # to use it in the query
                model_field = getattr(self.Meta.Model, field_name)
                stmt = stmt.filter(getattr(model_field, orm_operator)(filter_value))
        return stmt

    class Meta:
        # install this attribute from a filter subclass
        Model: Any

    class FilterRules:
        neq = lambda value: ("__ne__", value)
        gt = lambda value: ("__gt__", value)
        gte = lambda value: ("__ge__", value)
        lt = lambda value: ("__lt__", value)
        lte = lambda value: ("__le__", value)
        ilike = lambda value: ("ilike", value)
        eq = lambda value: ("__eq__", value)


class CategoryFilter(BaseFilter):
    name__eq: str | None = None

    class Meta(BaseFilter.Meta):
        Model = Category


class BookFilter(BaseFilter):
    id__eq: UUID4 | None = None
    isbn__eq: str | None = None
    name__eq: str | None = None
    name__ilike: str | None = None
    number_in_stock: int | None = None
    category: CategoryFilter | None = None
    price_per_unit__gt: float | None = None
    price_per_unit__lt: float | None = None
    price_with_discount__gt: float | None = None
    price_with_discount__lt: float | None = None
    number_in_stock__gte: int | None = None
    number_in_stock__lte: int | None = None

    class Meta(BaseFilter.Meta):
        Model = Book


