from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Dir, File


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    # 服务器实际存储的头像文件的文件名
    avatar: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # 默认可用空间 2GB
    total_space: Mapped[int] = mapped_column(Integer, default=2**31 - 1)
    used_space: Mapped[int] = mapped_column(Integer, default=0)

    # 关系 → 关系的 foreign_keys 使用的是类名 Dir / File 而外键的 ForeignKey 使用的是表名 __tablename__
    dirs: Mapped[list["Dir"]] = relationship(back_populates="user", foreign_keys="[Dir.user_id]")
    files: Mapped[list["File"]] = relationship(back_populates="user", foreign_keys="[File.user_id]")
