from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

import uuid
import enum

from app.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import File


class Status(enum.Enum):
    UPLOADING = "uploading"
    FINISHED = "finished"
    FAILED = "failed"


class Storage(Base):
    __tablename__ = "storages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    ref_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.UPLOADING, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_chunk_size: Mapped[int] = mapped_column(Integer, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, nullable=False)
