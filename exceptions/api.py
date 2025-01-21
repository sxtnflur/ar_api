from fastapi import Request, HTTPException, FastAPI
from exceptions.core import EntityNotFound, ExpiredToken, InvalidToken, InvalidInitDataException
from starlette.responses import JSONResponse


async def entity_not_found_error(request: Request, exc: EntityNotFound):
    raise HTTPException(
        status_code=404,
        detail={
            "message": exc.message,
            "entity": exc.entity,
            "byField": exc.by_field
        }
    )


async def expired_token_error(request: Request, exc: ExpiredToken):
    raise HTTPException(
        status_code=403,
        detail=exc.message
    )

async def invalid_token_error(request: Request, exc: InvalidToken):
    raise HTTPException(
        status_code=403,
        detail=exc.message
    )

def invalid_init_data_error(request: Request, exc: InvalidInitDataException):
    raise HTTPException(
        status_code=403,
        detail=exc.message
    )


def register_errors(app: FastAPI):
    app.exception_handler(EntityNotFound)(entity_not_found_error)
    app.exception_handler(ExpiredToken)(expired_token_error)
    app.exception_handler(InvalidToken)(invalid_token_error)
    app.exception_handler(InvalidInitDataException)(invalid_init_data_error)
    return app