from uuid import UUID

from pydantic import BaseModel, Field


class MediaBlock(BaseModel):
    id: UUID = Field(alias="uuid")
    photo_url: str
    video_url: str


    class Config:
        from_attributes = True



class CreatedCollectionResponse(BaseModel):
    id: UUID = Field(alias="uuid")
    name: str
    startup_url: str
    qr_code_url: str

    class Config:
        from_attributes = True


class CollectionResponse(CreatedCollectionResponse):
    blocks: list[MediaBlock] = []

    class Config:
        from_attributes = True


class CreatedMediaBlockResponse(BaseModel):
    photo_url: str
    video_url: str
    id: str



class MediaBlockPatches(BaseModel):
    photo_url: str
    video_url: str
