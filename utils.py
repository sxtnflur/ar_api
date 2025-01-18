import aiofiles
import os
from config import settings

BASE_DIR = os.getcwd()


async def save_file(file: bytes, filename: str) -> str:
    file_path = os.path.join(BASE_DIR, "files", filename)
    async with aiofiles.open(file_path, "w") as f:
        await f.write(file)
    return file_path



class FileStorage:

    domain: str = settings.domain
    dir_path: str = "cdn"

    def __get_url(self, filename: str) -> str:
        return f'https://{self.domain}/cdn/{filename}'

    async def __save_file_get_path(self, file: bytes, filename: str) -> str:
        file_path = os.path.join(BASE_DIR, self.dir_path, filename)
        print(f'{file_path=}')
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file)
        return file_path

    async def save_file_get_url(self, file: bytes, filename: str) -> str:
        await self.__save_file_get_path(file, filename)
        return self.__get_url(filename=filename)
