from datetime import datetime
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories import ShoppingSessionRepository
from application.schemas import ReturnShoppingSessionS, CreateShoppingSessionS, ShoppingSessionIdS, \
    UpdatePartiallyShoppingSessionS
from core import EntityBaseService
from core.base_repos import OrmEntityRepoInterface
from application.schemas.domain_model_schemas import ShoppingSessionS
from pydantic import ValidationError, PydanticSchemaGenerationError

from core.config import settings
from core.exceptions import DomainModelConversionError
from logger import logger


class ShoppingSession(EntityBaseService):
    def __init__(
            self,
            shopping_session_repo: Annotated[
                OrmEntityRepoInterface, ShoppingSessionRepository]
    ):
        super().__init__(shopping_session_repo=shopping_session_repo)
        self.shopping_session_repo = shopping_session_repo

    def get_shopping_session_by_id(
            self,
            session: AsyncSession,
            id: str
    ) -> ReturnShoppingSessionS:
        return await super().get_by_id(
            session=session,
            repo=self.shopping_session_repo,
            id=id
        )

    def create_shopping_session(
            self,
            session: AsyncSession,
            dto: CreateShoppingSessionS
    ) -> ShoppingSessionIdS:
        dto: dict = dto.model_dump(exclude_unset=True)

        try:
            domain_model = ShoppingSessionS(**dto)
            domain_model.expiration_time = datetime.now() + settings.SHOPPING_SESSION_DURATION
        except (ValidationError, PydanticSchemaGenerationError) as e:
            extra = {"dto": dto}
            logger.error("failed to convert to domain model", extra, exc_info=True)
            raise DomainModelConversionError

        return await super().create(
            session=session,
            repo=self.shopping_session_repo,
            domain_model=domain_model
        )

    def update_shopping_session(
            self,
            session: AsyncSession,
            id: str | int,
            dto: UpdatePartiallyShoppingSessionS
    ) -> ReturnShoppingSessionS:
        dto: dict = dto.model_dump(exclude_unset=True)

        try:
            domain_model = ShoppingSessionS(**dto)
        except (ValidationError, PydanticSchemaGenerationError) as e:
            extra = {"dto": dto}
            logger.error("failed to convert to domain model", extra, exc_info=True)
            raise DomainModelConversionError

        return await super().update(
            session=session,
            repo=self.shopping_session_repo,
            instance_id=id,
            domain_model=domain_model
        )
