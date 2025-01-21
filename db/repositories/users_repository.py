from db.main import async_session
from db.models import User
from schemas.users import UserResponse
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Protocol


class UsersRepositoryProtocol(Protocol):

    async def upsert_user(self, telegram_id: int,
                          username: str,
                          full_name: str) -> int:
        ...

    async def get_user(self, telegram_id: int) -> UserResponse:
        ...


class UsersRepository(UsersRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_user(self, telegram_id: int,
                          username: str,
                          full_name: str) -> int:
        stmt = """
            INSERT INTO users (telegram_id, username, full_name)
            VALUES (:telegram_id, :username, :full_name)
            ON CONFLICT (telegram_id) DO UPDATE SET
            username = EXCLUDED.username,
            full_name = EXCLUDED.full_name
            RETURNING id
        """
        user_id: int = await self.session.scalar(text(stmt).bindparams(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name
                ))
        return user_id

    async def get_user(self, telegram_id: int) -> UserResponse:
        stmt = (
            select(User)
            .where(User.telegram_id == telegram_id)
        )
        user: User = await self.session.scalar(stmt)
        return UserResponse.from_orm(user)