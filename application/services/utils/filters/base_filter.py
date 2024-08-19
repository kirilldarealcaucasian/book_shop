from typing import Any

from pydantic import BaseModel
from sqlalchemy import Select


__all__ = ("BaseFilter", )


class BaseFilter(BaseModel):
    def get_filtering_data(self):
        filtering_fields: dict = self.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
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