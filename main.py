from configuration.server import Server
from fastapi import FastAPI

def create_app(_=None) -> FastAPI:
    return Server(FastAPI(
        root_path="/api_game",
        openapi_url="/openapi"
        )
    ).get_app()