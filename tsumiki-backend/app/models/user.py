from sqlalchemy import BigInteger, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    # 服务器实际存储的头像文件的文件名
    avatar: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_space: Mapped[int] = mapped_column(BigInteger, nullable=False, default=2**31 - 1)
    used_space: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
