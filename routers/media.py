from typing import Annotated

from depends import MediaUseCaseAnnotated, CurrentUserAnnotated
from fastapi import APIRouter, UploadFile, Body, Query
from schemas.api import BaseResponse
from schemas.media_collections import CollectionResponse, CreatedCollectionResponse, CreatedMediaBlockResponse, \
    MediaBlock
from uuid import UUID

router = APIRouter(prefix="/collections", tags=["Коллекции"])


@router.post("")
async def create_collection(
    name: Annotated[str, Body(embed=True)],
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated
) -> CreatedCollectionResponse:
    return await media_use_case.create_collection(
        telegram_user_id=current_user.telegram_id, name=name
    )


@router.post("/{collection_id}/media_blocks")
async def send_media(
    collection_id: UUID,
    photo: UploadFile,
    video: UploadFile,
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated
) -> CreatedMediaBlockResponse:
    media_block = await media_use_case.add_media_block_to_collection(
        collection_uuid=collection_id,
        telegram_user_id=current_user.telegram_id,
        photo=await photo.read(),
        video=await video.read()
    )
    return media_block


@router.get("/my")
async def get_my_collections(
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1)
) -> list[CreatedCollectionResponse]:
    return await media_use_case.get_user_collections(
        telegram_user_id=current_user.telegram_id,
        offset=offset, limit=limit
    )


@router.get("/{collection_id}")
async def get_collection(
    collection_id: UUID,
    media_use_case: MediaUseCaseAnnotated,
    offset: int = Query(default=0, ge=0),
    limit: int | None = Query(default=None, ge=1)
) -> CollectionResponse:
    collection = await media_use_case.get_collection(
        collection_uuid=collection_id,
        media_blocks_offset=offset,
        media_blocks_limit=limit
    )
    return collection


@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: UUID,
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated
) -> BaseResponse:
    await media_use_case.delete_collection(
        collection_uuid=collection_id, telegram_user_id=current_user.telegram_id
    )
    return BaseResponse(
        message="Коллекция успешно удалена"
    )


@router.delete("/media_blocks/{block_id}")
async def delete_media_block(
    block_id: UUID,
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated
) -> BaseResponse:
    await media_use_case.delete_media_block(
        block_uuid=block_id, telegram_user_id=current_user.telegram_id
    )
    return BaseResponse(
        message="Блок успешно удален"
    )

@router.patch("/{collection_id}")
async def update_collection_name(
    collection_id: UUID,
    name: Annotated[str, Body(embed=True)],
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated
) -> BaseResponse:
    await media_use_case.update_collection_name(
        collection_uuid=collection_id, telegram_user_id=current_user.telegram_id,
        name=name
    )
    return BaseResponse(
        message="Имя коллекции изменено"
    )


@router.patch("/media_blocks/{block_id}")
async def patch_block(
    block_id: UUID,
    current_user: CurrentUserAnnotated,
    media_use_case: MediaUseCaseAnnotated,
    video: UploadFile | None = None,
    photo: UploadFile | None = None,
) -> BaseResponse:
    photo_: bytes | None = None
    video_: bytes | None = None

    if photo:
        photo_ = await photo.read()
    if video:
        video_ = await video.read()

    await media_use_case.patch_media_block(
        block_uuid=block_id, telegram_user_id=current_user.telegram_id,
        photo=photo_,
        video=video_
    )
    return BaseResponse(
        message="Данные медиа-блока обновлены"
    )



@router.get("/{collection_uuid}/only_blocks")
async def get_collection_blocks(
    collection_uuid: UUID,
    media_use_case: MediaUseCaseAnnotated
) -> list[MediaBlock]:
    return await media_use_case.get_collection_media_blocks(collection_uuid)