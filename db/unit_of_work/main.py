from contextlib import contextmanager
from typing import AsyncGenerator, Type
import abc
from db.repositories import UsersRepositoryProtocol, UsersRepository
from db.repositories import MediaCollectionsRepositoryProtocol, MediaCollectionRepository
from typing_extensions import Protocol, Self, AsyncContextManager


class UnitOfWorkProtocol(abc.ABC):
    users: UsersRepositoryProtocol
    media_collections: MediaCollectionsRepositoryProtocol

    @abc.abstractmethod
    async def __aenter__(self) -> Self:
        return self

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        ...



class UnitOfWork(UnitOfWorkProtocol):
    users: UsersRepositoryProtocol
    media_collections: MediaCollectionsRepositoryProtocol

    def __init__(self,
                 session_factory,
                 users_repository: Type[UsersRepositoryProtocol],
                 media_collections_repository: Type[MediaCollectionsRepositoryProtocol]):
        self.session_factory = session_factory
        self._session = None
        self.users_repository = users_repository
        self.media_collections_repository = media_collections_repository

    async def __aenter__(self) -> Self:
        uow = await super(UnitOfWork, self).__aenter__()
        self._session = self.session_factory()
        return uow

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()

    @property
    def users(self) -> UsersRepositoryProtocol:
        return self.users_repository(self._session)

    @property
    def media_collections(self) -> MediaCollectionsRepositoryProtocol:
        return self.media_collections_repository(self._session)