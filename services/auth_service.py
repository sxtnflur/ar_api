from typing import Protocol

from exceptions.core import ExpiredToken, InvalidToken
from schemas.auth import TokenData, TokensResponse
from datetime import datetime, timedelta
import jwt
import json
from config import settings



class AuthServiceProtocol(Protocol):
    async def create_tokens(self, token_data: TokenData) -> TokensResponse:
        ...

    async def validate_token(self, access_token: str) -> TokenData:
        ...

    async def refresh_token(self, refresh_token: str) -> TokensResponse:
        ...


class AuthService(AuthServiceProtocol):
    async def __create_access_token(self, sub: str):
        token_payload = {'sub': sub,
                         'exp': datetime.utcnow() + timedelta(days=30),
                         'iat': datetime.utcnow(),
                         'scope': 'access_token'
                         }
        return jwt.encode(token_payload, settings.auth_secret_key, algorithm='HS256')


    async def __create_refresh_token(self, sub: str):
        token_payload = {'sub': sub,
                         'exp': datetime.utcnow() + timedelta(days=30),
                         'iat': datetime.utcnow(),
                         'scope': 'refresh_token'
                         }
        return jwt.encode(token_payload, settings.auth_secret_key, algorithm='HS256')

    async def create_tokens(self, token_data: TokenData) -> TokensResponse:
        access_token: str = await self.__create_access_token(sub=token_data.model_dump_json())
        refresh_token: str = await self.__create_refresh_token(sub=token_data.model_dump_json())
        return TokensResponse(
            access_token=access_token, refresh_token=refresh_token
        )

    async def validate_token(self, access_token: str) -> TokenData:
        try:
            payload = jwt.decode(access_token, settings.auth_secret_key, algorithms=['HS256'])
            print(f'{payload=}')
            sub = json.loads(payload.get("sub"))
            return TokenData(**sub)
        except jwt.ExpiredSignatureError:
            raise ExpiredToken
        except jwt.InvalidTokenError:
            raise InvalidToken

    async def refresh_token(self, refresh_token: str) -> TokensResponse:
        try:
            payload = jwt.decode(refresh_token, settings.auth_secret_key, algorithms=['HS256'])
            if (payload['scope'] == 'refresh_token'):
                new_tokens = await self.create_tokens(payload['sub'])
                return new_tokens
            raise InvalidToken
        except jwt.ExpiredSignatureError:
            raise ExpiredToken
        except jwt.InvalidTokenError:
            raise InvalidToken