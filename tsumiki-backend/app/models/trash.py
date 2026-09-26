from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta, timezone
from app.models import Base
from app.config import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User


def _trash_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.TRASHES_EXPIRES_DAYS)


class Trash(Base):
    __tablename__ = "trashes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    original_path: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_trash_expires_at, index=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    storage_id: Mapped[str] = mapped_column(ForeignKey("storages.id"), nullable=False, index=True)

    user: Mapped["User"] = relationship(back_populates="trashes")
