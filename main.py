from depends import FileStorageAnnotated
from fastapi import FastAPI, UploadFile, HTTPException
from schemas import SaveFilesResponse

app = FastAPI()


@app.post("/send_media")
async def send_media(
    photo: UploadFile,
    video: UploadFile,
    file_storage: FileStorageAnnotated
) -> SaveFilesResponse:
    print(f'{photo=}')
    print(f'{video=}')

    if photo.content_type.split("/")[0] != "image":
        raise HTTPException(
            status_code=422, detail=f"'photo': content_type не соответствует image, ваш content_type={photo.content_type}"
        )
    if video.content_type.split("/")[0] != "video":
        raise HTTPException(
            status_code=422, detail=f"'video': content_type не соответствует image, ваш content_type={photo.content_type}"
        )

    photo_url: str = await file_storage.save_file_get_url(
        file=photo.read(), filename=photo.filename
    )
    video_url: str = await file_storage.save_file_get_url(
        file=video.read(), filename=video.filename
    )

    return SaveFilesResponse(
        photo_url=photo_url,
        video_url=video_url
    )


# if __name__ == '__main__':
#     uvicorn.run(app)