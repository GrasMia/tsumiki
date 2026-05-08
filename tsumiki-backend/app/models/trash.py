# from sqlalchemy import ForeignKey, String, Integer, DateTime
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from datetime import datetime, timezone
# from app.models import Base
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from app.models import User, Storage


# class Trash(Base):
#     __tablename__ = "trash"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
#     size: Mapped[int] = mapped_column(Integer, nullable=False)
#     original_path: Mapped[str] = mapped_column(String(255), nullable=False)
#     deleted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)
#     expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

#     # 外键
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
#     storage_id: Mapped[int] = mapped_column(ForeignKey("storage.id"), nullable=False, index=True)

#     # 关系
#     user: Mapped["User"] = relationship(back_populates="trashes")
#     storage: Mapped["Storage"] = relationship(back_populates="trashes")
