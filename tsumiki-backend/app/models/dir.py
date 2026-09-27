from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import File


class Dir(Base):
    __tablename__ = "dirs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("dirs.id"), nullable=False, index=True)

    files: Mapped[list["File"]] = relationship(back_populates="dir")
    # 目录层级关系（自关联属性）
    children: Mapped[list["Dir"]] = relationship(back_populates="parent")
    parent: Mapped["Dir"] = relationship(back_populates="children", remote_side=[id])
