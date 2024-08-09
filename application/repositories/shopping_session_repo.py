from sqlalchemy.ext.asyncio import AsyncSession

from application.schemas import CreateShoppingSessionS
from core import OrmEntityRepository
from application.models import ShoppingSession
from core.config import settings
from datetime import datetime
from application.schemas.domain_model_schemas import ShoppingSessionS
from pydantic import ValidationError
from logger import logger


class ShoppingSessionRepository(OrmEntityRepository):
    model: ShoppingSession = ShoppingSession

    async def create(
            self, session: AsyncSession,
            dto: CreateShoppingSessionS
    ):
        expiration_time = datetime.now() + settings.SHOPPING_SESSION_DURATION

        try:
            domain_model = ShoppingSessionS(
                **dto.model_dump(exclude_unset=True),
                expiration_time=expiration_time
            )
        except ValidationError:
            logger.error(f"Failed to validate domain model", exc_info=True)
            return

        await super().create(
            session=session,
            data=domain_model.model_dump(exclude_unset=True)
        )



