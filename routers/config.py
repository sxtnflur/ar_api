from fastapi import FastAPI, APIRouter
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Routes:
    routers: tuple

    def register_routes(self, app: FastAPI):
        for router in self.routers:
            app.include_router(router)