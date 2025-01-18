from depends import FileStorageAnnotated
from fastapi import FastAPI, UploadFile, HTTPException
from schemas import SaveFilesResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api")

origins = [
            "http://localhost",
            "http://127.0.0.1",
            "http://127.0.0.1:4000",
            "http://localhost:4000",
            "http://185.87.192.139:4000",
            "https://dinocarbone.ru"
        ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
    ],
)




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