from typing import Protocol

from db.main import async_session
from exceptions.core import EntityNotFound
from schemas.media_collections import CollectionResponse, CreatedCollectionResponse, MediaBlock as MediaBlockSchema
from sqlalchemy import select, insert, delete, update
from db.models import MediaBlock, Collection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only


class MediaCollectionsRepositoryProtocol(Protocol):

    async def get_collection(self, collection_uuid: str,
                                    media_blocks_offset: int = 0,
                                    media_blocks_limit: int | None = None) -> CollectionResponse:
        ...

    async def get_collections_by_user(self, telegram_user_id: int,
                                      offset: int = 0, limit: int = 10) -> list[CreatedCollectionResponse]:
        ...

    async def get_collection_media_block(self, collection_uuid: str) -> list[MediaBlockSchema]:
        ...

    async def get_media_block(self, media_block_uuid: str) -> MediaBlockSchema:
        ...

    async def create_collection(self, name: str, telegram_user_id: int,
                                startup_url: str | None = None, qr_code_url: str | None = None) -> str:
        ...

    async def update_collection(self, collection_uuid: str, telegram_user_id: int,
                                updates: dict) -> None:
        ...

    async def add_media_block_to_collection(self, collection_uuid: str, photo_url: str,
                                            video_url: str, telegram_user_id: int) -> str:
        ...

    async def delete_collection(self, collection_uuid: str, telegram_user_id: int) -> None:
        ...

    async def delete_media_block(self, media_block_uuid: str, telegram_user_id: int) -> None:
        ...

    async def update_media_block(self, media_block_uuid: str, telegram_user_id: int,
                                 updates: dict) -> None:
        ...

    async def update_collection_name(self, collection_uuid: str, telegram_user_id: int,
                                     name: str) -> None:
        ...


class MediaCollectionRepository(MediaCollectionsRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_collection(self, collection_uuid: str,
                                      media_blocks_offset: int = 0,
                             media_blocks_limit: int | None = None) -> CollectionResponse:
        stmt = (
            select(Collection)
            .options(
                selectinload(Collection.blocks)
            )
            .where(Collection.uuid == collection_uuid)
            .offset(media_blocks_offset)
        )
        if media_blocks_limit:
            stmt = stmt.limit(media_blocks_limit)

        collection: Collection | None = await self.session.scalar(stmt)
        if not collection:
            raise EntityNotFound(entity="collection", by_field="id")

        return CollectionResponse.from_orm(collection)

    async def get_collections_by_user(self, telegram_user_id: int,
                                      offset: int = 0, limit: int = 10) -> list[CreatedCollectionResponse]:
        stmt = (
            select(Collection)
            .where(Collection.telegram_user_id == telegram_user_id)
            .order_by(Collection.created_at.desc())
            .offset(offset).limit(limit)
        )
        collections = await self.session.scalars(stmt)
        return [CreatedCollectionResponse.from_orm(c) for c in collections]

    async def get_collection_media_block(self, collection_uuid: str) -> list[MediaBlockSchema]:
        stmt = (
            select(MediaBlock)
            .options(
                load_only(MediaBlock.uuid, MediaBlock.photo_url, MediaBlock.video_url)
            )
            .where(MediaBlock.collection_uuid == collection_uuid)
            .order_by(MediaBlock.created_at.desc())
        )
        blocks = await self.session.scalars(stmt)
        return [MediaBlockSchema.from_orm(b) for b in blocks]


    async def get_media_block(self, media_block_uuid: str) -> MediaBlockSchema:
        stmt = (
            select(MediaBlock)
            .where(MediaBlock.uuid == media_block_uuid)
        )
        block = await self.session.scalar(stmt)
        return MediaBlockSchema.from_orm(block)

    async def create_collection(self, name: str, telegram_user_id: int,
                                startup_url: str | None = None, qr_code_url: str | None = None) -> str:
        stmt = (
            insert(Collection)
            .values(
                name=name, telegram_user_id=telegram_user_id,
                startup_url=startup_url, qr_code_url=qr_code_url
            )
            .returning(Collection.uuid)
        )
        collection_uuid: str = await self.session.scalar(stmt)
        return collection_uuid

    async def add_media_block_to_collection(self, collection_uuid: str, photo_url: str,
                                            video_url: str, telegram_user_id: int) -> str:
        stmt = (
            insert(MediaBlock)
            .values(
                collection_uuid=collection_uuid,
                photo_url=photo_url, video_url=video_url
            )
            .returning(MediaBlock.uuid)
        )
        block_uuid: str = await self.session.scalar(stmt)
        return block_uuid


    async def delete_collection(self, collection_uuid: str, telegram_user_id: int) -> None:
        stmt = (
            delete(Collection)
            .where(Collection.uuid == collection_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(Collection.uuid)
        )
        uuid: str | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="collection", by_field="id")

    async def delete_media_block(self, media_block_uuid: str, telegram_user_id: int) -> None:
        stmt = (
            delete(MediaBlock)
            .where(MediaBlock.uuid == media_block_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(MediaBlock.uuid)
        )
        uuid: str | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="media_block", by_field="id")

    async def update_media_block(self, media_block_uuid: str, telegram_user_id: int,
                                 updates: dict) -> None:
        stmt = (
            update(MediaBlock)
            .values(**updates)

            # TODO: Исправить
            .where(MediaBlock.uuid == media_block_uuid)

            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(MediaBlock.uuid)
        )
        uuid: str | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="media_block", by_field="id")

    async def update_collection_name(self, collection_uuid: str, telegram_user_id: int,
                                     name: str) -> None:
        stmt = (
            update(Collection)
            .values(name=name)
            .where(Collection.uuid == collection_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(Collection.uuid)
        )
        uuid: str | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="collection", by_field="id")

    async def update_collection(self, collection_uuid: str, telegram_user_id: int,
                                updates: dict) -> None:
        stmt = (
            update(Collection)
            .values(**updates)
            .where(Collection.uuid == collection_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(Collection.uuid)
        )
        uuid: str | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="collection", by_field="id")
