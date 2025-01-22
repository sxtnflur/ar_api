from exceptions.api import register_errors
from fastapi import FastAPI
from routers import __routes__
from starlette.middleware.cors import CORSMiddleware



class Server:
    __app: FastAPI

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_middlewares(app)
        self.__register_routers(app)
        self.__register_exceptions(app)
        self.__register_openapi_json(app)

    def get_app(self):
        return self.__app

    @staticmethod
    def __register_routers(app):
        __routes__.register_routes(app)

    @staticmethod
    def __register_middlewares(app):
        origins = [
            "http://localhost",
            "http://127.0.0.1",
            "http://127.0.0.1:8080",
            "http://localhost:8080",

            "http://95.183.9.238:8080",
            "https://dinocarbone.ru"
        ]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "Set-Cookie",
                "Access-Control-Allow-Credentials",
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Methods",
            ],
        )

    @staticmethod
    def __register_exceptions(app):
        register_errors(app)


    @staticmethod
    def __register_openapi_json(app: FastAPI):
        def get_open_api() -> dict:
            print("OK")
            schema = app.openapi()
            print(f'{schema=}')
            return schema

        app.get("/api_game/openapi.json")(get_open_api)