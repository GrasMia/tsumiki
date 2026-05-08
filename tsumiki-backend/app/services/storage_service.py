from fastapi import UploadFile, HTTPException, status
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from pathlib import Path
import aiofiles
import hashlib
import asyncio
import math

from app.schemas import FileMetadata, ChunkMetadata, ChunkInfo
from app.db import AsyncSessionLocal
from app.models import Storage, Status
from app.config import settings

STORAGE_PATH = Path(settings.LOCAL_STORAGE_PATH)
STORAGE_PATH.mkdir(exist_ok=True)
CHUNK_SIZE = settings.UPLOAD_FILE_CHUNK_SIZE * 1024 * 1024


class StorageService:
    @staticmethod
    async def verify_storage(file_metadata: FileMetadata, db: AsyncSession):
        stmt = select(Storage).where(Storage.sha256 == file_metadata.sha256).with_for_update()
        existing_storage = await db.scalar(stmt)

        if not existing_storage:
            return None

        if existing_storage.status == Status.FINISHED and existing_storage.size != file_metadata.size:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "上传的文件有误，文件指纹与尺寸不匹配")
        return existing_storage

    @staticmethod
    async def create_storage(file_metadata: FileMetadata, db: AsyncSession):
        total_chunks = math.ceil(file_metadata.size / CHUNK_SIZE)
        last_chunk_size = file_metadata.size % CHUNK_SIZE or CHUNK_SIZE

        try:
            new_storage = await db.scalar(
                (
                    insert(Storage)
                    .values(
                        size=file_metadata.size,
                        sha256=file_metadata.sha256,
                        total_chunks=total_chunks,
                        last_chunk_size=last_chunk_size,
                    )
                    .returning(Storage)
                )
            )
            if not new_storage:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "存储记录创建失败")

            asyncio.create_task(StorageService.delayed_cleanup(new_storage.id))
            await db.commit()

            return ChunkInfo(
                id=new_storage.id,
                chunk_index=new_storage.chunk_index,
                total_chunks=new_storage.total_chunks,
                status=new_storage.status,
            )

        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "已存在相同的存储记录，请稍后重新上传")

    @staticmethod
    async def delayed_cleanup(storage_id: str, delay: int = 1800):
        """定时清理创建后未在规定时间内 FINISHED / FINISHED 但是 ref_count = 0 的 Storage 记录 以及 磁盘存储"""

        await asyncio.sleep(delay)

        async with AsyncSessionLocal.begin() as db:
            deleted_storage = await db.scalar(
                delete(Storage)
                .where(
                    Storage.id == storage_id,
                    (Storage.status != Status.FINISHED)
                    | ((Storage.status == Status.FINISHED) & (Storage.ref_count == 0)),
                )
                .returning(Storage)
            )

            if deleted_storage:
                physical_path = STORAGE_PATH / storage_id
                if physical_path.exists():
                    physical_path.unlink()

    @staticmethod
    async def refresh_storage_status(storage: Storage, db: AsyncSession):
        if storage.status != Status.UPLOADING:
            storage.status = Status.UPLOADING
        await db.commit()
        return ChunkInfo(
            id=storage.id,
            chunk_index=storage.chunk_index,
            total_chunks=storage.total_chunks,
            status=storage.status,
        )

    @staticmethod
    async def chunk_upload(chunk_metadata: ChunkMetadata, upload_file: UploadFile, db: AsyncSession):
        stmt = (
            select(Storage).where(Storage.id == chunk_metadata.id, Storage.status == Status.UPLOADING).with_for_update()
        )
        storage = await db.scalar(stmt)
        if not storage:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "上传队列中不存在该任务")

        try:
            if chunk_metadata.chunk_index != storage.chunk_index:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "上传的分片索引与要求的分片索引不符，请重新上传")
            if not upload_file.size or upload_file.size > CHUNK_SIZE:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "预期外的分片大小")
            if chunk_metadata.chunk_index + 1 == storage.total_chunks:
                if upload_file.size != storage.last_chunk_size:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "预期外的分片大小")
            else:
                if upload_file.size != CHUNK_SIZE:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "预期外的分片大小")

            try:
                read_bytes = upload_file.read(upload_file.size)
                chunk = await asyncio.wait_for(read_bytes, timeout=30)  # 30秒超时

            except asyncio.TimeoutError as e:
                # 连接断开/任务取消/超时
                raise HTTPException(status.HTTP_408_REQUEST_TIMEOUT, f"上传超时: {e.args}")
            except Exception as e:
                # 其他异常
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"上传失败: {e.args}")

        except:
            storage.status = Status.FAILED
            await db.commit()
            raise

        if hashlib.md5(chunk).hexdigest() != chunk_metadata.md5:
            storage.status = Status.FAILED
            await db.commit()
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "错误的 MD5 哈希值，请重试")

        async with aiofiles.open(physical_path := STORAGE_PATH / chunk_metadata.id, "ab") as f:
            await f.write(chunk)

        if (chunk_index := storage.chunk_index + 1) == storage.total_chunks:
            # 重新计算完整文件的 SHA256
            sha256 = hashlib.sha256()
            file_size = 0
            async with aiofiles.open(physical_path, "rb") as f:
                while c := await f.read(8192):
                    sha256.update(c)
                    file_size += len(c)
            # 验证 SHA256
            if sha256.hexdigest() != storage.sha256 or file_size != storage.size:
                await db.execute(delete(Storage).where(Storage.id == storage.id))
                if physical_path.exists():
                    physical_path.unlink()
                await db.commit()
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "文件已损坏请重新上传")

            storage.status = Status.FINISHED

        storage.chunk_index = chunk_index

        await db.commit()

        return storage
