from typing import Annotated
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from services import FileStorageServiceProtocol, FileStorageService
from services import AuthServiceProtocol, AuthService
from services import TelegramUtilsService, TelegramUtilsServiceProtocol
from services import QrCodeService, QrCodeServiceProtocol

from use_cases import MediaUseCase, MediaUseCaseProtocol
from use_cases import AuthUseCase, AuthUseCaseProtocol
from db.repositories import MediaCollectionRepository
from db.repositories import UsersRepository
from db.unit_of_work import UnitOfWork, UnitOfWorkProtocol
from db.main import async_session


# -- unit of work --
def get_unit_of_work() -> UnitOfWorkProtocol:
    return UnitOfWork(
        session_factory=async_session,
        users_repository=UsersRepository,
        media_collections_repository=MediaCollectionRepository
    )

UnitOfWorkAnnotated = Annotated[UnitOfWorkProtocol, Depends(get_unit_of_work)]


# -- services --
def get_qr_code_service() -> QrCodeServiceProtocol:
    return QrCodeService()

QrCodeServiceAnnotated = Annotated[QrCodeServiceProtocol, Depends(get_qr_code_service)]

def get_file_storage_service() -> FileStorageService:
    return FileStorageService()

FileStorageServiceAnnotated = Annotated[FileStorageServiceProtocol, Depends(get_file_storage_service)]

def get_telegram_utils_service() -> TelegramUtilsServiceProtocol:
    return TelegramUtilsService()

TelegramUtilsServiceAnnotated = Annotated[TelegramUtilsServiceProtocol, Depends(get_telegram_utils_service)]

def get_auth_service() -> AuthServiceProtocol:
    return AuthService()

AuthServiceAnnotated = Annotated[AuthServiceProtocol, Depends(get_auth_service)]



# -- use_cases --
def get_media_use_case(
        file_storage_service: FileStorageServiceAnnotated,
        uof: UnitOfWorkAnnotated,
        qr_code_service: QrCodeServiceAnnotated,
        telegram_utils_service: TelegramUtilsServiceAnnotated
) -> MediaUseCaseProtocol:
    return MediaUseCase(
        file_storage_service, uof, telegram_utils_service, qr_code_service
    )

MediaUseCaseAnnotated = Annotated[MediaUseCaseProtocol, Depends(get_media_use_case)]

def get_auth_use_case(
    auth_service: AuthServiceAnnotated,
    telegram_utils_service: TelegramUtilsServiceAnnotated,
    uof: UnitOfWorkAnnotated
) -> AuthUseCaseProtocol:
    return AuthUseCase(
        auth_service, uof, telegram_utils_service
    )

AuthUseCaseAnnotated = Annotated[AuthUseCaseProtocol, Depends(get_auth_use_case)]


# AUTH
class CurrentUser(BaseModel):
    id: int
    telegram_id: int

async def get_current_user(
    auth_service: AuthServiceAnnotated,
    token: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> CurrentUser:
    print(f'{token.credentials=}')
    token_data = await auth_service.validate_token(access_token=token.credentials)
    print(f'{token_data=}')
    # return CurrentUser(
    #     id=0, telegram_id=0
    # )
    return CurrentUser(
        id=token_data.user_id, telegram_id=token_data.telegram_id
    )

CurrentUserAnnotated = Annotated[CurrentUser, Depends(get_current_user)]