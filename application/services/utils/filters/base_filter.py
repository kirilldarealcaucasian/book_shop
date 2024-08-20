from collections import defaultdict
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Select, desc

__all__ = ("BaseFilter", )

from sqlalchemy.exc import CompileError

from core.exceptions import OrderingFilterError, FilterError
from logger import logger


class BaseFilter(BaseModel):
    def get_filtering_data(self):
        filtering_fields: dict = self.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        if getattr(filtering_fields, "order_by", None):
            del filtering_fields["order_by"]
        return filtering_fields.items()

    def filter(self, stmt: Select) -> Select:
        for filter_name, filter_name_value in self.get_filtering_data():
            # example name__ilike=20 --> (name__ilike, 20)

            filter = getattr(self, filter_name, None)
            if isinstance(filter, BaseFilter):
                # case for a nested filter
                try:
                    stmt = getattr(self, filter_name, None).filter(stmt)
                except (CompileError) as e:
                    logger.debug("filter error", exc_info=True)
                    raise FilterError

            if "__" in filter_name:
                field_name, query_operator = filter_name.split("__")  # example name__ilike --> name, ilike
                try:
                    orm_operator, filter_value = getattr(
                        self.FilterRules,
                        query_operator,
                        None
                    )(filter_name_value)  # use a mapper to get an orm operator and a filter value
                    # to use it in the query

                    model_field = getattr(self.Meta.Model, field_name)
                    stmt = stmt.filter(getattr(model_field, orm_operator)(filter_value))
                except CompileError as e:
                    extra = {
                        "field_name": field_name,
                        "query_operator": query_operator,
                        "filter_name_value": filter_name_value
                    }
                    logger.debug("filter error", extra=extra, exc_info=True)
                    raise FilterError
        return stmt

    def sort(self, stmt: Select) -> Select:
        if not self.order_by:
            return stmt

        fields: list = self.order_by.split(",")
        directions: dict[str, list[str]] = defaultdict(list)
        for field in fields:
            if "-" in field:
                directions["desc"].append(field.lstrip("-"))
            else:
                directions["asc"].append(field)
        try:
            stmt = stmt.order_by(
                        *[desc(value) for value in directions["desc"]],  # apply order_by for "descending" fields
                        *[value for value in directions["asc"]])
            return stmt
        except CompileError:
            logger.debug("incorrect order_by filter format", exc_info=True)
            raise OrderingFilterError

    class Meta:
        # install this attribute from a filter subclass
        Model: Any

    class FilterRules:
        neq = lambda value: ("__ne__", value)
        gt = lambda value: ("__gt__", value)
        gte = lambda value: ("__ge__", value)
        lt = lambda value: ("__lt__", value)
        lte = lambda value: ("__le__", value)
        ilike = lambda value: ("ilike", f"{value}%")
        eq = lambda value: ("__eq__", value)


