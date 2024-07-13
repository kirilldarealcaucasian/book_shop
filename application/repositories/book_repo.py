import logging
from collections import defaultdict
from sqlalchemy import select, desc, func
from sqlalchemy.exc import StatementError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Literal

from core import OrmEntityRepository
from core.exceptions import InvalidModelCredentials, FilterAttributeError, ServerError
from application.models import Book


class BookRepository(OrmEntityRepository):
    model: Book = Book

    async def get_all(
            self,
            session: AsyncSession,
            page: int = 0,
            limit: int = 5,
            **filters
    ):
        key_value_filters: dict[str, str] | None = filters.get("key_value_filters", None)
        order_by_filters: defaultdict[Literal["desc", "asc"], list[str]] = filters.get("order_by_filters", None)

        if key_value_filters is None and order_by_filters is None:
            return await super().get_all(session=session, page=page, limit=limit, **filters)

        model_attributes = {a for a in dir(self.model) if not a.startswith('_')}  # get model attributes(fields) to
        # perform checking against client filters

        if key_value_filters:
            for filter in list(key_value_filters.keys()):
                """
                if there is no attribute(field) in the model that client wants to filter by, 
                then we just won't filter by this field instead of raising an Exception
                """
                if filter not in model_attributes:
                    # remove invalid filter from the key_value_filters
                    del key_value_filters[filter]

        if order_by_filters:
            for filter in list(order_by_filters.keys()):
                # remove invalid filter from order_by_filters
                if filter not in model_attributes:
                    del order_by_filters[filter]

        stmt = None

        if "name" in key_value_filters.keys():
            # special case when we want to use LIKE

            stmt = select(self.model).filter(
                self.model.name.ilike(f"%{key_value_filters['name']}%")
            ).filter(
                *[
                    func.lower(getattr(self.model, filter_name)) == func.lower(filter_value) for
                    filter_name, filter_value in
                    key_value_filters.items() if filter_name != "name"
                ]  # apply key_value_filter (example of filter: name="some name")
            ).order_by(
                *[desc(value) for value in order_by_filters["desc"]],  # apply order_by for "descending" fields
                *[value for value in order_by_filters["asc"]]  # apply order_by for "ascending" fields
            ).offset(page * limit).limit(limit)  # pagination

        elif key_value_filters and order_by_filters and "name" not in key_value_filters:
            try:
                stmt = select(self.model).filter(
                    *[
                        getattr(self.model, filter_name) == filter_value for filter_name, filter_value in
                        key_value_filters.items()
                    ]  # apply key_value_filters
                ).order_by(
                    *[desc(value) for value in order_by_filters["desc"]],
                    *[value for value in order_by_filters["asc"]]
                ).offset(page * limit).limit(limit)
                # return (await session.scalars(stmt)).all()
            except AttributeError:
                extra = {"key_value_filters": key_value_filters}
                logging.error("Error while applying filters to the statement", extra, exc_info=True)
                raise FilterAttributeError

        elif key_value_filters and not order_by_filters and "name" not in key_value_filters:
            try:
                stmt = select(self.model).filter(
                    *[
                        getattr(self.model, filter_name) == filter_value for filter_name, filter_value in
                        key_value_filters.items()
                    ]  # apply key_value_filters
                ).offset(page * limit).limit(limit)
            except AttributeError:
                extra = {"key_value_filters": key_value_filters}
                logging.error("Error while applying filters to the statement", extra, exc_info=True)
                raise FilterAttributeError

        elif order_by_filters and not key_value_filters and "name" not in key_value_filters:
            try:
                stmt = select(self.model).order_by(
                    *[desc(value) for value in order_by_filters["desc"]],
                    *[value for value in order_by_filters["asc"]]
                ).offset(page * limit).limit(limit)
            except AttributeError:
                raise FilterAttributeError

        else:
            stmt = select(self.model).offset(page * limit).limit(limit)

        try:
            return (await session.scalars(stmt)).all()
        except (StatementError, InvalidRequestError) as e:
            logging.error("Error while trying to perform request to db:", exc_info=True)
            raise ServerError("Unexpected server error")

    async def update(
            self,
            data: dict,
            instance_id: str | int,
            session: AsyncSession,
    ) -> None:

        try:
            self.model(**data).validate_id(key="id", id=instance_id)
        except ValueError:
            raise InvalidModelCredentials(
                message="Invalid id format for book"
            )
        return await super().update(session=session, data=data, instance_id=instance_id)
