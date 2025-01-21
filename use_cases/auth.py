from db.repositories import UsersRepositoryProtocol
from db.unit_of_work import UnitOfWorkProtocol
from schemas.auth import TokensResponse, TokenData
from services import AuthServiceProtocol, TelegramUtilsServiceProtocol
from typing_extensions import Protocol


class AuthUseCaseProtocol(Protocol):
    async def create_tokens_by_telegram_init_data(self, telegram_init_data: str) -> TokensResponse:
        ...

class AuthUseCase:

    def __init__(self, auth_service: AuthServiceProtocol,
                 uof: UnitOfWorkProtocol,
                 telegram_utils_service: TelegramUtilsServiceProtocol,
                 ):
        self.auth_service = auth_service
        self.telegram_utils_service = telegram_utils_service
        self.uof = uof

    async def create_tokens_by_telegram_init_data(self, telegram_init_data: str) -> TokensResponse:
        # Верификация init_data
        user = await self.telegram_utils_service.verify_telegram_init_data(
            init_data=telegram_init_data
        )
        # Создание поля full_name
        full_name = " ".join([user.first_name or "", user.last_name or ""])
        # Добавление или обновление пользователя, получаем его id
        async with self.uof as uof:
            user_id: int = await uof.users.upsert_user(
                telegram_id=user.id, full_name=full_name,
                username=user.username
            )
        # Создаем токены
        tokens = await self.auth_service.create_tokens(token_data=TokenData(
            telegram_id=user.id, user_id=user_id
        ))
        return tokens