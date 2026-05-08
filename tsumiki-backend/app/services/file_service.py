from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Sequence
from pathlib import Path

from app.exceptions import USER_NOT_FOUND, FILE_NOT_FOUND, FILE_ALREADY_EXISTS, FILE_NOT_FOUND
from app.models import File, Dir, User, Storage
from app.schemas import FileMetadata
from app.config import settings

# 存储配置
STORAGE_PATH = Path(settings.LOCAL_STORAGE_PATH)  # 物理文件存储根目录
STORAGE_PATH.mkdir(exist_ok=True)  # 确保目录存在


class FileService:
    @staticmethod
    async def create_file(current_dir: Dir, file_metadata: FileMetadata, storage_id: str, db: AsyncSession):
        stmt = select(File).where(File.dir_id == current_dir.id, File.name == file_metadata.name)
        existing_file = await db.scalar(stmt)
        if existing_file:
            raise FILE_ALREADY_EXISTS

        current_user = await db.scalar(select(User).where(User.id == current_dir.user_id).with_for_update())
        if not current_user:
            raise USER_NOT_FOUND
        if current_user.used_space + file_metadata.size > current_user.total_space:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "空间不足")

        # 更新用户空间
        current_user.used_space += file_metadata.size
        # 创建新的文件记录
        await db.execute(
            insert(File).values(
                size=file_metadata.size,
                name=file_metadata.name,
                sha256=file_metadata.sha256,
                dir_id=current_dir.id,
                user_id=current_user.id,
                storage_id=storage_id,
            )
        )
        # 更新引用计数
        await db.execute(update(Storage).where(Storage.id == storage_id).values(ref_count=Storage.ref_count + 1))

        await db.commit()

    @staticmethod
    async def download_file(current_dir: Dir, file_name: str, db: AsyncSession) -> tuple[Path, str]:
        file = await db.scalar(select(File).where(File.dir_id == current_dir.id, File.name == file_name))
        if not file:
            raise FILE_NOT_FOUND

        storage = await db.scalar(select(Storage).where(Storage.id == file.storage_id))
        if not storage:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="未找到文件的储存位置")

        # 构建物理文件路径
        physical_path = STORAGE_PATH / str(storage.id)
        # 检查物理文件是否存在
        if not physical_path.exists():
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="物理文件丢失")

        await db.commit()

        return physical_path, file.name

    @staticmethod
    async def delete_files(files: Sequence[File], user_id: int, db: AsyncSession) -> list[Path]:
        if not files:
            return []

        total_size = sum(file.size for file in files)
        files_id = [file.id for file in files]
        storages_id: list[str] = []
        physical_paths: list[Path] = []

        # 更新 Storage 引用计数
        for file in files:
            stmt = (
                update(Storage)
                .where(Storage.id == file.storage_id)
                .values(ref_count=Storage.ref_count - 1)
                .returning(Storage)
            )
            storage = await db.scalar(stmt)
            # 引用计数归零 → 记录要删除的 Storage 记录和物理文件路径
            if storage and storage.ref_count <= 0:
                # 记录要删除 Storage 记录
                storages_id.append(storage.id)
                # 记录要删除的物理文件
                physical_paths.append(STORAGE_PATH / storage.id)

        # 更新用户空间（原子操作）
        await db.execute(update(User).where(User.id == user_id).values(used_space=User.used_space - total_size))

        # 删除文件记录
        await db.execute(delete(File).where(File.id.in_(files_id)))

        # 删除所有 ref_count 归零的 Storage 记录
        await db.execute(delete(Storage).where(Storage.id.in_(storages_id)))

        return physical_paths

    @staticmethod
    async def delete_file(current_dir: Dir, file_name: str, db: AsyncSession):
        stmt = delete(File).where(File.dir_id == current_dir.id, File.name == file_name).returning(File)
        deleted_file = await db.scalar(stmt)
        if not deleted_file:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "删除失败: 文件不存在")

        stmt = update(User).where(User.id == current_dir.user_id).values(used_space=User.used_space - deleted_file.size)
        await db.execute(stmt)

        stmt = (
            update(Storage)
            .where(Storage.id == deleted_file.storage_id)
            .values(ref_count=Storage.ref_count - 1)
            .returning(Storage)
        )
        storage = await db.scalar(stmt)
        if storage and storage.ref_count <= 0:
            await db.execute(delete(Storage).where(Storage.id == storage.id))

            physical_path = STORAGE_PATH / storage.id
            if physical_path.exists():
                physical_path.unlink()

        await db.commit()

    @staticmethod
    async def rename_file(current_dir: Dir, file_name: str, new_name: str, db: AsyncSession):
        try:
            stmt = (
                update(File)
                .where(File.dir_id == current_dir.id, File.name == file_name)
                .values(name=new_name)
                .returning(File)
            )
            renamed_file = await db.scalar(stmt)
            if not renamed_file:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "重命名失败: 文件不存在")
        except IntegrityError:
            raise FILE_ALREADY_EXISTS
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"重命名失败: {e.args}")

        await db.commit()
