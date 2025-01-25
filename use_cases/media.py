from typing import Protocol
from uuid import UUID

from db.repositories import MediaCollectionsRepositoryProtocol
from db.unit_of_work import UnitOfWorkProtocol
from schemas.media_collections import (
    CreatedCollectionResponse, CreatedMediaBlockResponse,
    MediaBlockPatches, CollectionResponse, MediaBlock
)
from services import FileStorageServiceProtocol
from services import TelegramUtilsServiceProtocol
from services.qr_code_service import QrCodeServiceProtocol
from urllib.parse import quote


class MediaUseCaseProtocol(Protocol):

    async def create_collection(self, telegram_user_id: int, name: str) -> CollectionResponse:
        ...

    async def add_media_block_to_collection(self,
                                            collection_uuid: UUID,
                                            photo: bytes,
                                            video: bytes,
                                            telegram_user_id: int) -> CreatedMediaBlockResponse:
        ...

    async def patch_media_block(self, block_uuid: UUID, telegram_user_id: int,
                                video: bytes | None = None, photo: bytes | None = None) -> None:
        ...

    async def delete_collection(self, collection_uuid: UUID, telegram_user_id: int) -> None:
        ...

    async def delete_media_block(self, block_uuid: UUID, telegram_user_id: int) -> None:
        ...

    async def update_collection_name(self, collection_uuid: UUID, telegram_user_id: int, name: str) -> None:
        ...
    async def get_collection(self, collection_uuid: UUID,
                             media_blocks_offset: int = 0,
                             media_blocks_limit: int | None = None) -> CollectionResponse:
        ...

    async def get_user_collections(self, telegram_user_id: int,
                                   offset: int = 0,
                                   limit: int | None = None) -> list[CollectionResponse]:
        ...

    async def get_collection_media_blocks(self, collection_uuid: UUID) -> list[MediaBlock]:
        ...

class MediaUseCase(MediaUseCaseProtocol):
    def __init__(self,
                 file_storage_service: FileStorageServiceProtocol,
                 uow: UnitOfWorkProtocol,
                 telegram_utils_service: TelegramUtilsServiceProtocol,
                 qr_code_service: QrCodeServiceProtocol,
                 ):
        self.file_storage_service = file_storage_service
        self.uow: UnitOfWorkProtocol = uow
        self.telegram_utils_service = telegram_utils_service
        self.qr_code_service = qr_code_service

    async def create_collection(self, telegram_user_id: int, name: str) -> CollectionResponse:
        async with self.uow as uow:
            # Создание коллекции
            collection_uuid: UUID = await uow.media_collections.create_collection(
                name=name, telegram_user_id=telegram_user_id
            )

            # Создание реф ссылки на коллекцию
            startup_url: str = await self.telegram_utils_service.create_startup_url(
                payload=f'collection|{collection_uuid}'
            )

            # Создание QR-кода
            qr_code_bytes: bytes = await self.qr_code_service.create_qr_code(payload=startup_url)

            valid_name = quote(name)
            qr_code_url: str = await self.file_storage_service.save_file_get_url(
                file=qr_code_bytes, filename=f"{telegram_user_id}-{valid_name}-qrcode"
            )

            # Добавление ссылок к коллекции
            await uow.media_collections.update_collection(
                collection_uuid=collection_uuid, telegram_user_id=telegram_user_id,
                updates=dict(
                    startup_url=startup_url,
                    qr_code_url=qr_code_url
                )
            )

        return CollectionResponse(
            uuid=collection_uuid,
            name=name,
            startup_url=startup_url,
            qr_code_url=qr_code_url
        )

    async def add_media_block_to_collection(self, collection_uuid: UUID,
                                            photo: bytes,
                                            video: bytes,
                                            telegram_user_id: int) -> CreatedMediaBlockResponse:
        photo_url: str = await self.file_storage_service.save_file_get_url(
            file=photo, filename=self.file_storage_service.format_filename(
                user_id=telegram_user_id, file_type=self.file_storage_service.file_types.photo
            )
        )
        video_url: str = await self.file_storage_service.save_file_get_url(
            file=video, filename=self.file_storage_service.format_filename(
                user_id=telegram_user_id, file_type=self.file_storage_service.file_types.video
            )
        )
        async with self.uow as uow:
            block_uuid: UUID = await uow.media_collections.add_media_block_to_collection(
                collection_uuid=collection_uuid, telegram_user_id=telegram_user_id,
                photo_url=photo_url, video_url=video_url
            )
        return CreatedMediaBlockResponse(
            photo_url=photo_url,
            video_url=video_url,
            id=block_uuid
        )

    async def patch_media_block(self, block_uuid: UUID, telegram_user_id: int,
                                video: bytes | None = None, photo: bytes | None = None) -> None:
        updates = {}
        if video:
            video_url = await self.file_storage_service.save_file_get_url(
                file=video, filename=self.file_storage_service.format_filename(
                user_id=telegram_user_id, file_type=self.file_storage_service.file_types.video
            )
            )
            updates.update(video_url=video_url)
        if photo:
            photo_url = await self.file_storage_service.save_file_get_url(
                file=photo, filename=self.file_storage_service.format_filename(
                user_id=telegram_user_id, file_type=self.file_storage_service.file_types.photo
            )
            )
            updates.update(photo_url=photo_url)

        # Получение и добавление обновлений
        async with self.uow as uow:
            block = await uow.media_collections.get_media_block(media_block_uuid=block_uuid)
            await uow.media_collections.update_media_block(
                media_block_uuid=block_uuid, telegram_user_id=telegram_user_id,
                updates=updates
            )

        # Удалить прошлые картинку и видео
        if video:
            await self.file_storage_service.delete_file_by_url(url=block.video_url)
        if photo:
            await self.file_storage_service.delete_file_by_url(url=block.photo_url)

    async def delete_collection(self, collection_uuid: UUID, telegram_user_id: int) -> None:
        async with self.uow as uow:
            await uow.media_collections.delete_collection(
                collection_uuid, telegram_user_id
            )

    async def delete_media_block(self, block_uuid: UUID, telegram_user_id: int) -> None:
        async with self.uow as uow:
            await uow.media_collections.delete_media_block(
                media_block_uuid=block_uuid, telegram_user_id=telegram_user_id
            )

    async def update_collection_name(self, collection_uuid: UUID, telegram_user_id: int, name: str) -> None:
        async with self.uow as uow:
            await uow.media_collections.update_collection_name(
                collection_uuid, telegram_user_id, name
            )

    async def get_collection(self, collection_uuid: UUID,
                             media_blocks_offset: int = 0,
                             media_blocks_limit: int | None = None) -> CollectionResponse:
        async with self.uow as uow:
            collection = await uow.media_collections.get_collection(
                collection_uuid=collection_uuid,
                media_blocks_offset=media_blocks_offset,
                media_blocks_limit=media_blocks_limit
            )
        return collection

    async def get_user_collections(self, telegram_user_id: int,
                                   offset: int = 0, limit: int | None = None) -> list[CollectionResponse]:
        async with self.uow as uow:
            collections = await uow.media_collections.get_collections_by_user(
                telegram_user_id=telegram_user_id,
                offset=offset, limit=limit
            )
        return collections

    async def get_collection_media_blocks(self, collection_uuid: UUID) -> list[MediaBlock]:
        async with self.uow as uow:
            blocks = await uow.media_collections.get_collection_media_block(collection_uuid)
        return blocks