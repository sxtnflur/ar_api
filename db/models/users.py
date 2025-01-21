from datetime import datetime

from db.models.base import Base, bigInt, createdAt
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[bigInt] = mapped_column(unique=True)
    full_name: Mapped[str]
    created_at: Mapped[createdAt]