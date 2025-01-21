import os
import dotenv
from pydantic.v1 import BaseSettings

dotenv.load_dotenv()

BASE_DIR = os.getcwd()

class DatabaseSettings(BaseSettings):
    provider: str
    host: str
    port: int
    user: str
    password: str
    name: str

    @property
    def url(self):
        return f'{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class Settings(BaseSettings):
    domain: str
    telegram_bot_token: str
    auth_secret_key: str
    db: DatabaseSettings
    media_path: str

settings = Settings(
    domain=os.getenv("DOMAIN"),
    telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
    auth_secret_key=os.getenv("AUTH_SECRET_KEY"),
    db=DatabaseSettings(
        provider=os.getenv("DB_PROVIDER"), host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), name=os.getenv("DB_NAME")
    ),
    media_path=os.path.join(BASE_DIR, "cdn")
)