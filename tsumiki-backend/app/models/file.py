from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User, Dir, Storage


class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 虚拟的文件名
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # SHA-256 唯一哈希(建立索引(可重复) → 多用户指向内容相同的文件时 SHA-256 相同)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # 外键
    dir_id: Mapped[int] = mapped_column(ForeignKey("dir.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    storage_id: Mapped[str] = mapped_column(ForeignKey("storage.id"), nullable=False, index=True)

    # 联合唯一约束 → 同一目录下，不能有两个同名文件
    __table_args__ = (UniqueConstraint("dir_id", "name", name="uq_dir_filename_status"),)

    # 关系
    dir: Mapped["Dir"] = relationship(back_populates="files")
    user: Mapped["User"] = relationship(back_populates="files")
    storage: Mapped["Storage"] = relationship(back_populates="files")
