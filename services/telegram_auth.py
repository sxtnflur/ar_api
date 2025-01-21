from urllib.parse import unquote
import hmac
import json
import hashlib
from exceptions.core import InvalidInitDataException
from schemas.auth import UserDataFromInitData
from config import settings
from typing_extensions import Protocol


class TelegramUtilsServiceProtocol(Protocol):
    async def verify_telegram_init_data(self, init_data: str) -> UserDataFromInitData:
        ...
    async def create_startup_url(self, payload: str) -> str:
        ...

class TelegramUtilsService:
    bot_token: str = settings.telegram_bot_token

    async def verify_telegram_init_data(self, init_data: str) -> UserDataFromInitData:
        try:
            vals = {k: unquote(v) for k, v in [s.split('=', 1) for s in init_data.split('&')]}
            print(f'{vals=}')
            data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash')
            print(f'{data_check_string=}')

            secret_key = hmac.new("WebAppData".encode(), self.bot_token.encode(), hashlib.sha256).digest()
            h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
            if h.hexdigest() == vals['hash']:
                return UserDataFromInitData(**json.loads(vals.get("user")))
        except:
            raise InvalidInitDataException

        raise InvalidInitDataException


    async def create_startup_url(self, payload: str) -> str:
        url = f"https://t.me/"
        return url