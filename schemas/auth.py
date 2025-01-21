from pydantic import BaseModel, Field





class TokenData(BaseModel):
    user_id: int
    telegram_id: int


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserDataFromInitData(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str
    is_premium: bool = Field(default=False)
    allows_write_to_pm: bool