import os
import dotenv
from pydantic.v1 import BaseSettings

dotenv.load_dotenv()

class Settings(BaseSettings):
    domain: str

settings = Settings(
    domain=os.getenv("DOMAIN")
)