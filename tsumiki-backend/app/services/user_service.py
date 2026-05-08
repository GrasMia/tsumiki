from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pathlib import Path
import aiofiles
import asyncio
import os

from app.models import User
from app.config import settings
from app.exceptions import USER_NOT_FOUND

# 头像存储根目录
AVATAR_PATH = Path(settings.LOCAL_AVATAR_PATH)
AVATAR_PATH.mkdir(exist_ok=True)


class UserService:

    @staticmethod
    async def upload_avatar(current_user_id: int, upload_file: UploadFile, db: AsyncSession):
        """上传用户头像"""
        if not upload_file.filename:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "头像名必须存在且不能为空")
        if not upload_file.size or upload_file.size <= 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "错误的头像文件")
        if upload_file.size > 2 * 1024 * 1024:  # 1MB
            raise HTTPException(status_code=400, detail="头像过大，最大支持 2MB")

        current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
        if not current_user:
            raise USER_NOT_FOUND

        # 验证文件类型
        allowed_types = ["image/jpg", "image/jpeg", "image/png", "image/webp"]
        if upload_file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="头像只支持 JPG、JEPG、PNG、WEBP 格式")

        # 确定文件名
        file_ext = os.path.splitext(upload_file.filename)[1].lower()
        if file_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            file_ext = ".png"
        avatar_filename = f"{current_user.id}{file_ext}"
        physical_path = AVATAR_PATH / avatar_filename

        # 读取并保存文件
        try:
            avatar_data = await asyncio.wait_for(upload_file.read(), timeout=30)
            # 验证实际读取大小
            if len(avatar_data) != upload_file.size:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "文件读取不完整")
            # 写入文件
            async with aiofiles.open(physical_path, "wb") as f:
                await f.write(avatar_data)
        except asyncio.TimeoutError:
            if physical_path.exists():
                physical_path.unlink()
            raise HTTPException(status.HTTP_408_REQUEST_TIMEOUT, "上传超时")
        except Exception as e:
            if physical_path.exists():
                physical_path.unlink()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"上传失败: {e.args}")

        # 保存成功后删除旧头像
        if current_user.avatar:
            old_physical_path = AVATAR_PATH / current_user.avatar
            if old_physical_path.exists() and old_physical_path != physical_path:
                old_physical_path.unlink()

        # 更新数据库
        current_user.avatar = avatar_filename
        await db.commit()

    @staticmethod
    async def get_avatar_path(avatar: str | None, db: AsyncSession) -> Path:
        """获取用户头像路径"""
        if not avatar:
            root_user = await db.get(User, 0)
            if not root_user:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "根用户不存在")
            return AVATAR_PATH / f"{root_user.avatar}"

        avatar_path = AVATAR_PATH / f"{avatar}"
        if not avatar_path.exists():
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "物理头像丢失")
        return avatar_path
