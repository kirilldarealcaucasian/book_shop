from application.models import Category
from application.services.utils.filters.base_filter import BaseFilter
from pydantic import Field


class CategoryFilter(BaseFilter):
    name__eq: str | None = Field(default=None, alias="category_name__eq")

    class Meta(BaseFilter.Meta):
        Model = Category