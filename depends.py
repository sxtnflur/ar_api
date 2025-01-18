from typing import Annotated

from fastapi import Depends
from utils import FileStorage



def get_file_storage():
    return FileStorage()

FileStorageAnnotated = Annotated[FileStorage, Depends(get_file_storage)]