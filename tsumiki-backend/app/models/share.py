from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models import Base
from typing import TYPE_CHECKING
import secrets

if TYPE_CHECKING:
    from app.models import User


class Share(Base):
    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pwd: Mapped[str | None] = mapped_column(String(6), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    token: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, default=lambda: secrets.token_urlsafe(16)
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    storage_id: Mapped[str] = mapped_column(ForeignKey("storages.id", ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped["User"] = relationship(back_populates="shares")
