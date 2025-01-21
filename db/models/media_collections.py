from db.models.base import Base, uuid_pk, bigInt, createdAt
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship




class Collection(Base):
    __tablename__ = "collections"

    uuid: Mapped[uuid_pk]
    name: Mapped[str]
    startup_url: Mapped[str | None]
    qr_code_url: Mapped[str | None]
    telegram_user_id: Mapped[bigInt]
    created_at: Mapped[createdAt]

    blocks = relationship("MediaBlock", back_populates="collection", order_by="desc(MediaBlock.created_at)")


class MediaBlock(Base):
    __tablename__ = "media_blocks"

    uuid: Mapped[uuid_pk]
    photo_url: Mapped[str]
    video_url: Mapped[str]
    collection_uuid: Mapped[str] = mapped_column(ForeignKey(Collection.uuid))
    created_at: Mapped[createdAt]

    collection = relationship(Collection, foreign_keys=collection_uuid)