from sqlalchemy import BigInteger, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from app.config import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Trash, Share

DEFAULT_TOTAL_SPACE = settings.AVAILABLE_GB_SPACE * 1024**3


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    # 服务器实际存储的头像文件的文件名
    avatar: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_space: Mapped[int] = mapped_column(BigInteger, nullable=False, default=DEFAULT_TOTAL_SPACE)
    used_space: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    trashes: Mapped[list["Trash"]] = relationship(back_populates="user")
    shares: Mapped[list["Share"]] = relationship(back_populates="user")
