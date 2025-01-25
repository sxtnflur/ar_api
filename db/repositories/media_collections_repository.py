from typing import Protocol
from uuid import UUID

from db.main import async_session
from exceptions.core import EntityNotFound
from schemas.media_collections import CollectionResponse, CreatedCollectionResponse, MediaBlock as MediaBlockSchema
from sqlalchemy import select, insert, delete, update
from db.models import MediaBlock, Collection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only


class MediaCollectionsRepositoryProtocol(Protocol):

    async def get_collection(self, collection_uuid: UUID,
                                    media_blocks_offset: int = 0,
                                    media_blocks_limit: int | None = None) -> CollectionResponse:
        ...

    async def get_collections_by_user(self, telegram_user_id: int,
                                      offset: int | None = None, limit: int | None = None) -> list[CollectionResponse]:
        ...

    async def get_collection_media_block(self, collection_uuid: UUID) -> list[MediaBlockSchema]:
        ...

    async def get_media_block(self, media_block_uuid: UUID) -> MediaBlockSchema:
        ...

    async def create_collection(self, name: str, telegram_user_id: int,
                                startup_url: str | None = None, qr_code_url: str | None = None) -> UUID:
        ...

    async def update_collection(self, collection_uuid: UUID, telegram_user_id: int,
                                updates: dict) -> None:
        ...

    async def add_media_block_to_collection(self, collection_uuid: UUID, photo_url: str,
                                            video_url: str, telegram_user_id: int) -> UUID:
        ...

    async def delete_collection(self, collection_uuid: UUID, telegram_user_id: int) -> None:
        ...

    async def delete_media_block(self, media_block_uuid: UUID, telegram_user_id: int) -> None:
        ...

    async def update_media_block(self, media_block_uuid: UUID, telegram_user_id: int,
                                 updates: dict) -> None:
        ...

    async def update_collection_name(self, collection_uuid: UUID, telegram_user_id: int,
                                     name: str) -> None:
        ...


class MediaCollectionRepository(MediaCollectionsRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_collection(self, collection_uuid: UUID,
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
                                      offset: int | None = None, limit: int | None = None) -> list[CollectionResponse]:
        stmt = (
            select(Collection)
            .options(
                selectinload(Collection.blocks)
            )
            .where(Collection.telegram_user_id == telegram_user_id)
            .order_by(Collection.created_at.asc())
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        collections = await self.session.scalars(stmt)
        return [CollectionResponse.from_orm(c) for c in collections]

    async def get_collection_media_block(self, collection_uuid: UUID) -> list[MediaBlockSchema]:
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


    async def get_media_block(self, media_block_uuid: UUID) -> MediaBlockSchema:
        print(f'{media_block_uuid=}')
        stmt = (
            select(MediaBlock)
            .where(MediaBlock.uuid == media_block_uuid)
        )
        block: MediaBlock | None = await self.session.scalar(stmt)
        if not block:
            raise EntityNotFound(entity="media_block", by_field="id")
        return MediaBlockSchema.from_orm(block)

    async def create_collection(self, name: str, telegram_user_id: int,
                                startup_url: str | None = None, qr_code_url: str | None = None) -> UUID:
        stmt = (
            insert(Collection)
            .values(
                name=name, telegram_user_id=telegram_user_id,
                startup_url=startup_url, qr_code_url=qr_code_url
            )
            .returning(Collection.uuid)
        )
        collection_uuid: UUID = await self.session.scalar(stmt)
        print(f'{collection_uuid=}')
        return collection_uuid

    async def add_media_block_to_collection(self, collection_uuid: UUID, photo_url: str,
                                            video_url: str, telegram_user_id: int) -> UUID:
        stmt = (
            insert(MediaBlock)
            .values(
                collection_uuid=collection_uuid,
                photo_url=photo_url, video_url=video_url
            )
            .returning(MediaBlock.uuid)
        )
        block_uuid: UUID = await self.session.scalar(stmt)
        return block_uuid


    async def delete_collection(self, collection_uuid: UUID, telegram_user_id: int) -> None:
        stmt = (
            delete(Collection)
            .where(Collection.uuid == collection_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(Collection.uuid)
        )
        uuid: UUID | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="collection", by_field="id")

    async def delete_media_block(self, media_block_uuid: UUID, telegram_user_id: int) -> None:
        stmt = (
            delete(MediaBlock)
            .where(MediaBlock.uuid == media_block_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(MediaBlock.uuid)
        )
        uuid: UUID | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="media_block", by_field="id")

    async def update_media_block(self, media_block_uuid: UUID, telegram_user_id: int,
                                 updates: dict) -> None:
        stmt = (
            update(MediaBlock)
            .values(**updates)

            # TODO: Исправить
            .where(MediaBlock.uuid == media_block_uuid)

            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(MediaBlock.uuid)
        )
        uuid: UUID | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="media_block", by_field="id")

    async def update_collection_name(self, collection_uuid: UUID, telegram_user_id: int,
                                     name: str) -> None:
        stmt = (
            update(Collection)
            .values(name=name)
            .where(Collection.uuid == collection_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(Collection.uuid)
        )
        uuid: UUID | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="collection", by_field="id")

    async def update_collection(self, collection_uuid: UUID, telegram_user_id: int,
                                updates: dict) -> None:
        stmt = (
            update(Collection)
            .values(**updates)
            .where(Collection.uuid == collection_uuid)
            .where(Collection.telegram_user_id == telegram_user_id)
            .returning(Collection.uuid)
        )
        uuid: UUID | None = await self.session.scalar(stmt)
        if not uuid:
            raise EntityNotFound(entity="collection", by_field="id")
