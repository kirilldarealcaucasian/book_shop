from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_repos import OrmEntityRepoInterface
from typing import TypeVar
from core.exceptions import RelatedEntityDoesNotExist, ServerError, EntityDoesNotExist, RepositoryResolutionError, \
    FilterAttributeError
from main.schemas import (CreateBookS,
                          CreateOrderS,
                          CreateImageS,
                          CreateAuthorS,
                          CreatePublisherS,
                          RegisterUserS,
                          UpdateBookS,
                          UpdateOrderS,
                          UpdateAuthorS,
                          UpdateUserS,
                          UpdatePublisherS,
                          UpdatePartiallyBookS,
                          UpdatePartiallyUserS,
                          UpdatePartiallyAuthorS,
                          UpdatePartiallyPublisherS,
                          ReturnBookS,
                          ReturnOrderS,
                          ReturnUserS,
                          ReturnImageS,
                          ReturnPublisherS, UpdatePartiallyOrderS
                          )
from logger import logger

CreateDataT = TypeVar(
    "CreateDataT",
    CreateBookS, CreateOrderS, RegisterUserS,
    CreateImageS, CreateAuthorS, CreatePublisherS
)

UpdateDataT = TypeVar(
    "UpdateDataT",
    UpdateBookS, UpdateOrderS, UpdateUserS,
    UpdateAuthorS, UpdateUserS, UpdatePublisherS, UpdatePartiallyOrderS
)

PartialUpdateDataT = TypeVar(
    "PartialUpdateDataT",
    UpdatePartiallyBookS, UpdatePartiallyUserS,
    UpdatePartiallyAuthorS, UpdatePartiallyPublisherS
)

ReturnDataT = TypeVar(
    "ReturnDataT", ReturnBookS, ReturnOrderS,
    ReturnUserS, ReturnImageS, ReturnPublisherS
)

ArgDataT = TypeVar("ArgDataT", str, int)


class RepositoryResolver:
    """
    returns desired repository from the EntityBaseService attributes
    (EntityBaseService might be initialized by different repositories)
    """

    def __init__(self, repository_pool: dict):
        self.repo_pool: dict = repository_pool

    def __call__(self, desired_repo: OrmEntityRepoInterface) -> OrmEntityRepoInterface:
        for repo in self.repo_pool.values():
            if repo == desired_repo:
                return repo
        raise RepositoryResolutionError


class EntityBaseService:
    # calls to the repository defined by the service in main/services

    def __init__(self, **repos):
        for repo_name, instance in repos.items():
            # store received repository instances in the attributes
            setattr(self, repo_name, instance)
        self.repository_resolver = RepositoryResolver(repository_pool=vars(self))

    async def create(
            self,
            repo: OrmEntityRepoInterface,
            session: AsyncSession,
            dto: CreateDataT
    ) -> None:
        try:
            return await self.repository_resolver(repo).create(
                data=dto.model_dump(),
                session=session
            )
        except RepositoryResolutionError:
            extra = {"repo": repo}
            logger.error("Repository Resolution error while creating: ", extra=extra, exc_info=True)
            raise ServerError(detail="Unable to create instance due to server error")

        except ServerError:
            raise ServerError(detail="Unable to create instance due to server error")

        except RelatedEntityDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error in the provided data (cannot find related entity/entities)"
            )

    async def update(self,
                     repo: OrmEntityRepoInterface,
                     session: AsyncSession,
                     instance_id: ArgDataT,
                     dto: UpdateDataT | PartialUpdateDataT
                     ) -> ReturnDataT:

        fixed_data = dto.model_dump(exclude_unset=True)
        try:
            return await self.repository_resolver(repo).update(
                instance_id=instance_id,
                data=fixed_data,
                session=session,
            )
        except RepositoryResolutionError:
            extra = {"repo", repo}
            logger.error("Repository Resolution error while updating: ", extra=extra, exc_info=True)
            raise ServerError(detail="Unable to update instance due to server error")

        except ServerError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to update instance due to server error"
            )

        except RelatedEntityDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error in the provided data (cannot find related entity/entities)"
            )

    async def get_all(
            self,
            repo: OrmEntityRepoInterface,
            session: AsyncSession,
            **filters
    ) -> list[ReturnDataT] | ReturnDataT:
        try:
            return await self.repository_resolver(repo).get_all(**filters, session=session)

        except RepositoryResolutionError:
            extra = {"repo", repo}
            logger.error("Repository Resolution error while retrieving data: ", extra=extra, exc_info=True)
            raise ServerError(detail="Unable to retrieve instance/instances due to server error")

        except ServerError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to get instance due to server error"
            )

        except FilterAttributeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def delete(
            self,
            repo: OrmEntityRepoInterface,
            session: AsyncSession,
            instance_id: ArgDataT,

    ) -> None:
        try:
            await self.repository_resolver(repo).delete(instance_id=instance_id, session=session)
        except RepositoryResolutionError:
            extra = {"repo", repo}
            logger.error("Repository Resolution error while deleting data: ", extra=extra, exc_info=True)
            raise ServerError(detail="Unable to delete instance due to server error")

        except ServerError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to delete instance due to server error"
            )
        except EntityDoesNotExist as e:
            raise e
