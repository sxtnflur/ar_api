from typing import Annotated

from fastapi import APIRouter, Body
from schemas.auth import TokensResponse
from depends import AuthUseCaseAnnotated

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/create_tokens")
async def create_token(
    init_data: Annotated[str, Body(embed=True)],
    auth_use_case: AuthUseCaseAnnotated
) -> TokensResponse:
    return await auth_use_case.create_tokens_by_telegram_init_data(
        telegram_init_data=init_data
    )


@router.put("/refresh_token")
async def refresh_token(
    refresh_token: Annotated[str, Body(embed=True)],
    auth_use_case: AuthUseCaseAnnotated
) -> TokensResponse:
    return await auth_use_case.refresh_token(refresh_token=refresh_token)

