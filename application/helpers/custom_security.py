from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

from logger import logger


class CustomSecurity(HTTPBearer):
        async def __call__(self, request: Request):
            try:
                credentials: HTTPAuthorizationCredentials = await super().__call__(request)
                return credentials
            except HTTPException as e:
                logger.debug("failed to retrieve a token from request", exc_info=True)
                return None
                # raise HTTPException(status_code=401, detail=e.args)