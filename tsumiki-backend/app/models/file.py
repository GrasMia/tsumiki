from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Dir


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 虚拟的文件名
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    # SHA-256 唯一哈希(建立索引(可重复) → 多用户指向内容相同的文件时 SHA-256 相同)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    # 外键
    dir_id: Mapped[int] = mapped_column(ForeignKey("dirs.id"), nullable=False)  # 子表检查走 (dir_id, name) 最左前缀
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    storage_id: Mapped[str] = mapped_column(ForeignKey("storages.id"), nullable=False, index=True)

    # 复合唯一约束 → 同一目录下，不能有两个同名文件
    __table_args__ = (UniqueConstraint("dir_id", "name", name="uq_dir_filename_status"),)

    dir: Mapped["Dir"] = relationship(back_populates="files")
