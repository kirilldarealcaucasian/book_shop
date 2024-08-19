from fastapi import HTTPException, status


__all__ = (
    "AlreadyExistsError",
    "RelatedEntityDoesNotExist",
    "ServerError",
    "EntityDoesNotExist",
    "UnauthorizedError",
    "RepositoryResolutionError",
    "InvalidModelCredentials",
    "FilterAttributeError"
)


class AlreadyExistsError(HTTPException):
    def __init__(self, entity):
        super().__init__(
            detail=f"{entity} already exists",
            status_code=status.HTTP_409_CONFLICT
        )


class RelatedEntityDoesNotExist(HTTPException):
    def __init__(self, entity: str | None = None):
        if entity:
            super().__init__(
                detail=f"{entity} does not exist",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        else:
            super().__init__(
                detail=f"Invalid ForeignKey reference",
                status_code=status.HTTP_400_BAD_REQUEST)


class InvalidModelCredentials(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            detail=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class EntityDoesNotExist(HTTPException):
    def __init__(self, entity):
        super().__init__(
            detail=f"{entity} does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ServerError(HTTPException):
    def __init__(self, detail: str = "Something went wrong"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str | Exception):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

        
class RepositoryResolutionError(ValueError):
    def __init__(self):
        super().__init__("Unable to find desired repo in the repo_collector")


class FilterAttributeError(AttributeError):
    def __init__(self):
        super().__init__("Invalid filter name / value")


class DomainModelConversionError(HTTPException):
    def __init__(self, detail: str | Exception):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


