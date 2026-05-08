from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User, File


class Dir(Base):
    __tablename__ = "dir"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # 外键
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("dir.id"), nullable=False, index=True)

    # 关系
    user: Mapped["User"] = relationship(back_populates="dirs")
    files: Mapped[list["File"]] = relationship(back_populates="dir")
    # 目录层级关系（自引用）
    children: Mapped[list["Dir"]] = relationship(back_populates="parent", foreign_keys="[Dir.parent_id]")
    parent: Mapped["Dir"] = relationship(back_populates="children", remote_side=[id])
