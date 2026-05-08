from datetime import datetime
from sqlalchemy import func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())
