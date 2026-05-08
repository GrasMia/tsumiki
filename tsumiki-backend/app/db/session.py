from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

SYNC_DATABASE_URL = settings.DATABASE_URL
sync_engine = create_engine(SYNC_DATABASE_URL, echo=settings.DEBUG)
SyncSessionLocal = sessionmaker(sync_engine, autobegin=True, autoflush=False)

ASYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql", "postgresql+asyncpg")
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=settings.DEBUG, pool_recycle=3600, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
# 在异步环境中 expire_on_commit=True 会导致 commit 后访问已过期对象时触发惰性加载，但异步无法在同步上下文中执行查询，从而抛出 MissingGreenlet 错误
# 注意：异步懒加载 与 expire_on_commit=True 还会引起访问 关系属性 时 MissingGreenlet 错误 → 解决方法：⑴关闭 expire_on_commit ⑵使用 selectinload 预加载关系属性


async def get_db():
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_db_auto():
    with SyncSessionLocal.begin() as session:
        yield session


async def get_db_async():
    async with AsyncSessionLocal() as session:
        yield session


async def get_db_async_auto():
    """与 get_db_async 的唯一区别 → commit() 是否自动执行"""
    async with AsyncSessionLocal.begin() as session:
        yield session
