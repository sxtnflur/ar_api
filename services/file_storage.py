import datetime
from typing import Protocol

import aiofiles
import os
from config import settings


class FileStorageServiceProtocol(Protocol):
    async def save_file_get_url(self, file: bytes, filename: str | None = None) -> str:
        ...

    async def delete_file(self, filename: str) -> None:
        ...

    async def delete_file_by_url(self, url: str) -> None:
        ...



class FileStorageService(FileStorageServiceProtocol):
    domain: str = settings.domain
    dir_path: str = settings.media_path
    media_url: str = "cdn"

    def __get_url(self, filename: str) -> str:
        return f'https://{self.domain}/{self.media_url}/{filename}'

    async def __save_file_get_path(self, file: bytes, filename: str | None = None) -> str:
        filename_ = str(round(datetime.datetime.now().timestamp()))
        if filename:
            filename_ += filename

        file_path = os.path.join(self.dir_path, filename_)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file)
        return filename_

    async def save_file_get_url(self, file: bytes, filename: str | None = None) -> str:
        filename_ = await self.__save_file_get_path(file, filename)
        return self.__get_url(filename=filename_)

    async def delete_file(self, filename: str) -> None:
        os.remove(path=os.path.join(self.dir_path, filename))

    async def delete_file_by_url(self, url: str) -> None:
        filename = url.split("/")[-1]
        return await self.delete_file(filename=filename)