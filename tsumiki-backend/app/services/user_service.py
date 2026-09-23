from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
import aiofiles
import asyncio
import io

from app.models import User
from app.config import settings
from app.exceptions import USER_NOT_FOUND

# 头像存储根目录
AVATAR_PATH = Path(settings.LOCAL_AVATAR_PATH)
AVATAR_PATH.mkdir(exist_ok=True)

# 线程池
executor = ThreadPoolExecutor(max_workers=4)


class UserService:
    @staticmethod
    async def upload_avatar(current_user_id: int, upload_file: UploadFile, db: AsyncSession):
        """上传用户头像"""
        if not upload_file.filename:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "头像名必须存在且不能为空")
        if not upload_file.size or upload_file.size <= 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "错误的头像文件")
        if upload_file.size > 2 * 1024 * 1024:  # 2MB
            raise HTTPException(status_code=400, detail="头像过大，最大支持 2MB")

        current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
        if not current_user:
            raise USER_NOT_FOUND

        physical_path = AVATAR_PATH

        try:
            avatar_data = await asyncio.wait_for(upload_file.read(), timeout=30)

            if len(avatar_data) != upload_file.size:
                raise Exception("文件读取不完整")

            # 压缩图片
            loop = asyncio.get_event_loop()  # uvloop 下返回的是 uvloop 的 loop
            avatar_data, img_format = await loop.run_in_executor(executor, UserService.compress_image, avatar_data)

            avatar_filename = f"{current_user.id}{img_format}"
            physical_path = AVATAR_PATH / avatar_filename

            async with aiofiles.open(physical_path, "wb") as f:
                await f.write(avatar_data)
        except asyncio.TimeoutError:
            if physical_path.is_file():  # is_file 会判断 存在 and 是否是文件 两个条件
                physical_path.unlink()
            raise HTTPException(status.HTTP_408_REQUEST_TIMEOUT, "上传超时")
        except Exception as e:
            if physical_path.is_file():
                physical_path.unlink()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"上传失败: {e}")

        # 保存成功后删除旧头像
        if current_user.avatar:
            old_physical_path = AVATAR_PATH / current_user.avatar
            if old_physical_path.exists() and old_physical_path != physical_path:
                old_physical_path.unlink()

        # 更新数据库
        current_user.avatar = avatar_filename
        await db.commit()

    @staticmethod
    def compress_image(avatar_data: bytes, max_size: int = 512) -> tuple[bytes, str]:
        # 验证文件类型
        img = Image.open(io.BytesIO(avatar_data))
        if not img.format:
            raise Exception("未知的图片格式")
        if img.format not in ["JPEG", "PNG", "WEBP"]:
            raise Exception("头像只支持 JPEG、PNG、WEBP 格式")

        # 缩放（所有格式通用）
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        output = io.BytesIO()

        if img.format == "JPEG":
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")  # JPEG 必须转 RGB（去掉透明通道）
            img.save(output, format="JPEG", quality=85, optimize=True)
            ext = ".jpg"

        elif img.format == "PNG":
            img.save(output, format="PNG", optimize=True)
            ext = ".png"

        else:
            img.save(output, format="WEBP", quality=85)
            ext = ".webp"

        return output.getvalue(), ext

    @staticmethod
    async def get_avatar_path(avatar: str | None, db: AsyncSession) -> Path:
        """获取用户头像路径"""
        if not avatar:
            root_user = await db.get(User, 0)
            if not root_user:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "root 用户不存在，无法获取默认头像")
            return AVATAR_PATH / f"{root_user.avatar}"

        avatar_path = AVATAR_PATH / f"{avatar}"
        if not avatar_path.exists():
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "物理头像丢失")
        return avatar_path

    @staticmethod
    async def reset_avatar_path(current_user_id: int, db: AsyncSession):
        current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
        if not current_user:
            raise USER_NOT_FOUND
        if not current_user.avatar:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "无头像上传记录")

        physical_path = AVATAR_PATH / current_user.avatar
        if physical_path.exists():
            physical_path.unlink()

        current_user.avatar = None
        await db.commit()
