from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_repos import OrmEntityRepoInterface
from typing import TypeVar
from core.exceptions import RelatedEntityDoesNotExist, ServerError, EntityDoesNotExist, RepositoryResolutionError, \
    FilterAttributeError, DuplicateError
from application.schemas import (
    CreateBookS,
    CreateOrderS,
    CreateImageS,
    CreateAuthorS,
    CreatePublisherS,
    RegisterUserS,
    UpdateBookS,
    UpdateOrderS,
    UpdateAuthorS,
    UpdateUserS,
    UpdateCategoryS,
    UpdatePublisherS,
    UpdatePartiallyBookS,
    UpdatePartiallyUserS,
    UpdatePartiallyAuthorS,
    UpdatePartiallyPublisherS,
    ReturnBookS,
    ReturnOrderS,
    ReturnUserS,
    ReturnImageS,
    ReturnPublisherS, UpdatePartiallyOrderS,
    CreateCategoryS, ReturnCategoryS,
    ReturnShoppingSessionS, ShoppingSessionIdS,
    CreateShoppingSessionS,
    UpdatePartiallyShoppingSessionS
)
from application.schemas.domain_model_schemas import \
    (
    AuthorS,
    BookS,
    BookOrderAssocS,
    CartItemS,
    CategoryS,
    OrderS,
    PaymentDetailS,
    PublisherS,
    ShoppingSessionS
)

from logger import logger

CreateDataT = TypeVar(
    "CreateDataT",
    CreateBookS, CreateOrderS, RegisterUserS,
    CreateImageS, CreateAuthorS, CreatePublisherS,
    CreateCategoryS, CreateShoppingSessionS
)

UpdateDataT = TypeVar(
    "UpdateDataT",
    UpdateBookS, UpdateOrderS, UpdateUserS,
    UpdateAuthorS, UpdateUserS, UpdatePublisherS,
    UpdatePartiallyOrderS, UpdateCategoryS
)

PartialUpdateDataT = TypeVar(
    "PartialUpdateDataT",
    UpdatePartiallyBookS, UpdatePartiallyUserS,
    UpdatePartiallyAuthorS, UpdatePartiallyPublisherS,
    UpdatePartiallyShoppingSessionS
)

ReturnDataT = TypeVar(
    "ReturnDataT", ReturnBookS, ReturnOrderS,
    ReturnUserS, ReturnImageS, ReturnPublisherS,
    ReturnCategoryS, ReturnShoppingSessionS
)

CreateReturnDataT = TypeVar("CreateReturnDataT", ShoppingSessionIdS, None)

ArgDataT = TypeVar("ArgDataT", str, int)

DomainModelDataT = TypeVar(
    "DomainModelDataT",
    AuthorS, BookS, BookOrderAssocS,
    CartItemS, CategoryS, OrderS,
    PaymentDetailS, PublisherS, ShoppingSessionS
)


class RepositoryResolver:
    """
    returns desired repository from the EntityBaseService attributes
    (EntityBaseService might be initialized by different repositories
    from service layer)
    """

    def __init__(self, repository_pool: dict):
        self.repo_pool: dict = repository_pool

    def __call__(self, desired_repo: OrmEntityRepoInterface) -> OrmEntityRepoInterface:
        for repo in self.repo_pool.values():
            if repo == desired_repo:
                return repo
        raise RepositoryResolutionError


class EntityBaseService:
    # calls to the repository defined by the service in application/services

    def __init__(self, **repos):
        for repo_name, instance in repos.items():
            # store received repository instances in the attributes
            setattr(self, repo_name, instance)
        self.repository_resolver = RepositoryResolver(repository_pool=vars(self))

    async def create(
            self,
            repo: OrmEntityRepoInterface,
            session: AsyncSession,
            domain_model: DomainModelDataT
    ) -> CreateReturnDataT:

        try:
            return await self.repository_resolver(repo).create(
                data=domain_model,
                session=session
            )
        except RepositoryResolutionError:
            extra = {"repo": repo}
            logger.error("Repository Resolution error while creating: ", extra=extra, exc_info=True)
            raise ServerError(detail="Unable to create instance due to server error")

        except ServerError:
            raise ServerError(detail="Unable to create instance due to server error")

        except DuplicateError:
            raise

        except RelatedEntityDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error in the provided data (cannot find related entity/entities)"
            )

    async def update(
            self,
            repo: OrmEntityRepoInterface,
            session: AsyncSession,
            instance_id: ArgDataT,
            domain_model: DomainModelDataT
    ) -> ReturnDataT:
        try:
            return await self.repository_resolver(repo).update(
                instance_id=instance_id,
                domain_model=domain_model,
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

    async def get_by_id(
            self,
            session: AsyncSession,
            repo: OrmEntityRepoInterface,
            id: int | str,
    ) -> ReturnDataT | None:
        try:
            return (await self.repository_resolver(repo).get_all(id=id, session=session))[0]
        except (RepositoryResolutionError, IndexError) as e:
            extra = {"repo", repo}
            if isinstance(e, RepositoryResolutionError):
                logger.error("Repository Resolution error while retrieving data: ", extra=extra, exc_info=True)
                raise ServerError(detail="Unable to retrieve instance/instances due to server error")
            elif isinstance(e, IndexError):
                logger.debug("No instance was received", extra=extra)
                # fix: find out entity type
                return None

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
