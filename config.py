from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    domain: str

settings = Settings(
    domain="dinocarbone.ru"
)