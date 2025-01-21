from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    full_name: str
    username: str | None = None