from configuration.server import Server
from fastapi import FastAPI

def create_app(_=None):
    return Server(FastAPI(
        title="DinoCarbone",
        version="0.1",
        root_path="/api",
        max_request_body_size=10 * 1024 * 1024)
    ).get_app()