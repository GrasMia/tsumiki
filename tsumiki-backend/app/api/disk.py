from fastapi import APIRouter, Body, HTTPException, status, UploadFile, Depends, Query, File
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_async, get_db_async_auto
from app.models import Dir, Status
from app.schemas import DirInfo, FileInfo, FileMetadata, ChunkInfo, ChunkMetadata
from app.services import DirService, FileService, StorageService
from app.core.dependencies import get_current_user_id, get_current_user_id_by_query
from app.exceptions import DIR_NOT_FOUND, USER_INCONSISTENT
from app.utils import validate_dir_name, validate_dir_path, validate_file_name

router = APIRouter(tags=["disk"])


@router.get("/{dir_path:path}/")  # :path → 多级路径匹配
async def get_list(
    dir_path: str,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async_auto),
):
    dir_path = validate_dir_path(dir_path)

    stmt = (
        select(Dir)
        .where(Dir.path == ("/" + dir_path + "/"))
        .options(selectinload(Dir.children), selectinload(Dir.files))
        # selectinload(A.B,A.B.C)/selectinload(A.B).selectinload(A.B.C) = 嵌套预加载 B 和 C
        # selectinload(A.B), selectinload(A.C) = 独立预加载 B 和 C
        # selectinload(A.B.C) = 只预加载 C（A 和 B 不预加载）
    )
    current_dir = await db.scalar(stmt)
    if not current_dir:
        raise DIR_NOT_FOUND
    if current_dir.user_id != current_user_id:
        raise USER_INCONSISTENT

    dirs = [DirInfo.model_validate(dir) for dir in current_dir.children]
    files = [FileInfo.model_validate(file) for file in current_dir.files]

    return dirs + files


@router.get("/{dir_path:path}/{file_name}")  # 尾部不跟 / 表示参数 {file_name} 是文件而不是目录
async def download_file(
    dir_path: str,
    file_name: str,
    current_user_id: int = Depends(get_current_user_id_by_query),
    db: AsyncSession = Depends(get_db_async),
):
    dir_path = validate_dir_path(dir_path)
    file_name = validate_file_name(file_name)

    current_dir = await db.scalar(select(Dir).where(Dir.path == ("/" + dir_path + "/")))
    if not current_dir:
        raise DIR_NOT_FOUND
    if current_dir.user_id != current_user_id:
        raise USER_INCONSISTENT

    physical_path, file_name = await FileService.download_file(current_dir=current_dir, file_name=file_name, db=db)
    # 返回文件响应
    return FileResponse(path=physical_path, filename=file_name, media_type="application/octet-stream")


@router.patch("/{user_id}/", response_model=ChunkInfo)
async def chunk_upload(
    user_id: int,
    chunk_metadata: ChunkMetadata = Depends(ChunkMetadata.init_by_form),
    upload_file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    if user_id != current_user_id:
        raise USER_INCONSISTENT

    return await StorageService.chunk_upload(chunk_metadata, upload_file, db)


@router.post("/{dir_path:path}/")
async def create(
    dir_path: str,
    new_dir_name: str | None = Query(None),
    file_metadata: FileMetadata | None = Body(None),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    dir_path = validate_dir_path(dir_path)

    # 上传的是目录
    if new_dir_name and not file_metadata:
        new_dir_name = validate_dir_name(new_dir_name)

        current_dir = await db.scalar(select(Dir).where(Dir.path == ("/" + dir_path + "/")).with_for_update())
        if not current_dir:
            raise DIR_NOT_FOUND
        if current_dir.user_id != current_user_id:
            raise USER_INCONSISTENT

        await DirService.create_dir(current_dir=current_dir, dir_name=new_dir_name, db=db)
        return {"detail": f"路径 {new_dir_name} 创建成功"}

    # 上传的是文件
    elif file_metadata and not new_dir_name:
        file_metadata.name = validate_file_name(file_metadata.name)
        if file_metadata.size > 200 * 1024 * 1024:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "文件过大，最大支持 200MB")

        existing_storage = await StorageService.verify_storage(file_metadata, db)

        # 新任务
        if not existing_storage:
            return await StorageService.create_storage(file_metadata, db)

        # 上传完成 / 秒传
        if existing_storage.status == Status.FINISHED:
            current_dir = await db.scalar(select(Dir).where(Dir.path == ("/" + dir_path + "/")).with_for_update())
            if not current_dir:
                raise DIR_NOT_FOUND
            if current_dir.user_id != current_user_id:
                raise USER_INCONSISTENT

            await FileService.create_file(current_dir, file_metadata, existing_storage.id, db)
            return {"detail": f"文件 {file_metadata.name} 上传成功"}

        # 断点续传 → 多用户同时上传同一文件时允许并发上传(会导致客户端冲突)
        else:
            return await StorageService.refresh_storage_status(existing_storage, db)

    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "操作失败: 存在缺失或多余的参数")


@router.delete("/{dir_path:path}/")
async def delete(
    dir_path: str,
    dir_name: str | None = Query(default=None),
    file_name: str | None = Query(default=None),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    dir_path = validate_dir_path(dir_path)

    if dir_name and not file_name:
        dir_name = validate_dir_name(dir_name)

        delete_dir = await db.scalar(select(Dir).where(Dir.path == (f"/{dir_path}/{dir_name}/")).with_for_update())
        if not delete_dir:
            raise DIR_NOT_FOUND
        if delete_dir.user_id != current_user_id:
            raise USER_INCONSISTENT

        deleted_file_names = await DirService.delete_dir(delete_dir, db)
        if not deleted_file_names:
            return {"detail": f"目录 {dir_name} 已删除"}
        return {"detail": f"目录 {dir_name} 已删除, 包含文件: {'、'.join(deleted_file_names)}"}

    elif file_name and not dir_name:
        file_name = validate_file_name(file_name)

        current_dir = await db.scalar(select(Dir).where(Dir.path == ("/" + dir_path + "/")).with_for_update())
        if not current_dir:
            raise DIR_NOT_FOUND
        if current_dir.user_id != current_user_id:
            raise USER_INCONSISTENT

        await FileService.delete_file(current_dir, file_name, db)
        return {"detail": f"文件 {file_name} 已删除"}

    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "删除失败: 存在缺失或多余的参数")


@router.put("/{dir_path:path}/")
async def rename(
    dir_path: str,
    dir_name: str | None = Query(default=None),
    file_name: str | None = Query(default=None),
    new_name: str = Query(...),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    dir_path = validate_dir_path(dir_path)

    if dir_name and not file_name:
        dir_name = validate_dir_name(dir_name)
        new_name = validate_dir_name(new_name)

        rename_dir = await db.scalar(select(Dir).where(Dir.path == (f"/{dir_path}/{dir_name}/")).with_for_update())
        if not rename_dir:
            raise DIR_NOT_FOUND
        if rename_dir.user_id != current_user_id:
            raise USER_INCONSISTENT

        await DirService.rename_dir(rename_dir=rename_dir, new_name=new_name, db=db)
        return {"detail": f"目录 {dir_name} 已重命名为 {new_name}"}

    elif file_name and not dir_name:
        file_name = validate_file_name(file_name)
        new_name = validate_file_name(new_name)

        current_dir = await db.scalar(select(Dir).where(Dir.path == ("/" + dir_path + "/")).with_for_update())
        if not current_dir:
            raise DIR_NOT_FOUND
        if current_dir.user_id != current_user_id:
            raise USER_INCONSISTENT

        await FileService.rename_file(current_dir=current_dir, file_name=file_name, new_name=new_name, db=db)
        return {"detail": f"文件 {file_name} 已重命名为 {new_name}"}

    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "重命名失败: 存在缺失或多余的参数")
