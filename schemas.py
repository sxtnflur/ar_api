from pydantic import BaseModel


class SaveFilesResponse(BaseModel):
    photo_url: str
    video_url: str