from typing import Sequence
from sqlalchemy import Table
from app.models import Base, User, Dir
from app.config import settings
from .session import sync_engine, SyncSessionLocal, async_engine, AsyncSessionLocal


def init_db_sync(tables: Sequence[Table] | None = None):
    # 初始化数据表
    if settings.DEBUG:
        Base.metadata.create_all(sync_engine, tables=tables, checkfirst=True)

    # 初始化 root 用户 与 根目录
    with SyncSessionLocal.begin() as db:
        db.merge(
            User(
                id=0,
                username="root",
                email="root@tsumiki.com",
                hashed_password="",
                avatar="0.jpg",
                is_active=False,  # 禁止登录
                total_space=0,
            )
        )
        db.merge(
            Dir(
                id=0,
                name="",
                path="/",
                user_id=0,  # 超级用户 root
                parent_id=0,  # 指向自己
            )
        )


async def init_db_async(tables: Sequence[Table] | None = None):
    if settings.DEBUG:
        async with async_engine.begin() as async_conn:
            # 使用 lambda 包装
            await async_conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables, checkfirst=True))

    async with AsyncSessionLocal.begin() as db:
        await db.merge(
            User(
                id=0,
                username="root",
                email="root@tsumiki.com",
                hashed_password="",
                avatar="0.jpg",
                is_active=False,
                total_space=0,
            )
        )
        await db.merge(
            Dir(
                id=0,
                name="",
                path="/",
                user_id=0,
                parent_id=0,
            )
        )
