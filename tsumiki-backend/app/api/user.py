from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.db import get_db_async, get_db_async_auto
from app.services import UserService
from app.core.dependencies import get_current_user_id
from app.schemas import UpdatePasswordParams, UserProfile
from app.utils import validate_password, validate_username
from app.core.security import verify_password, get_password_hash
from app.exceptions import user_exceptions, email_exceptions, pwd_exceptions

router = APIRouter(tags=["users"])


@router.get("/{user_id}/info", response_model=UserProfile)
async def get_user_info(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async_auto),
):
    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT

    current_user = await db.scalar(select(User).where(User.id == current_user_id))
    if not current_user:
        raise user_exceptions.USER_NOT_FOUND

    return current_user


@router.patch("/{user_id}/username")
async def modify_user_name(
    user_id: int,
    new_name: str,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    new_name = validate_username(new_name)

    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT
    current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
    if not current_user:
        raise user_exceptions.USER_NOT_FOUND
    if current_user.username == new_name:
        raise user_exceptions.SAME_USERNAME

    # 检查用户名是否已被占用
    existing_user = await db.scalar(select(User).where(User.username == new_name, User.id != current_user.id))
    if existing_user:
        raise user_exceptions.USERNAME_ALREADY_EXISTS

    current_user.username = new_name
    await db.commit()

    return {"detail": "用户名更新成功"}


@router.patch("/{user_id}/email")
async def modify_user_email(
    user_id: int,
    new_email: EmailStr,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT
    current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
    if not current_user:
        raise user_exceptions.USER_NOT_FOUND
    if current_user.email == new_email:
        raise email_exceptions.SAME_EMAIL

    # 检查邮箱是否已被占用
    existing_user = await db.scalar(select(User).where(User.email == new_email, User.id != current_user.id))
    if existing_user:
        raise email_exceptions.EMAIL_ALREADY_EXISTS

    current_user.email = new_email
    await db.commit()

    return {"detail": "邮箱已修改"}


@router.patch("/{user_id}/password")
async def modify_password(
    user_id: int,
    password_data: UpdatePasswordParams,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    password_data.old_password = validate_password(password_data.old_password)
    password_data.new_password = validate_password(password_data.new_password)

    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT
    # 新旧密码不能相同
    if password_data.old_password == password_data.new_password:
        raise pwd_exceptions.SAME_PASSWORD
    current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
    if not current_user:
        raise user_exceptions.USER_NOT_FOUND
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise pwd_exceptions.INVALID_PASSWORD

    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    return {"detail": "密码修改成功"}


@router.put("/{user_id}/avatar")
async def modify_avatar(
    user_id: int,
    upload_file: UploadFile,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT

    await UserService.upload_avatar(current_user_id, upload_file, db)

    return {"detail": "头像已更换"}


@router.get("/{user_id}/avatar")
async def get_avatar(
    user_id: int,
    current_user_id: User = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async_auto),
):
    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT
    current_user = await db.scalar(select(User).where(User.id == current_user_id))
    if not current_user:
        raise user_exceptions.USER_NOT_FOUND

    avatar_path = await UserService.get_avatar_path(current_user.avatar, db)

    return FileResponse(avatar_path)


@router.put("/{user_id}/inactive")
async def user_inactive(
    user_id: int,
    password: str,
    db: AsyncSession = Depends(get_db_async),
    current_user_id: User = Depends(get_current_user_id),
):
    if user_id != current_user_id:
        raise user_exceptions.USER_INCONSISTENT
    current_user = await db.scalar(select(User).where(User.id == current_user_id).with_for_update())
    if not current_user:
        raise user_exceptions.USER_NOT_FOUND
    if not verify_password(password, current_user.hashed_password):
        raise pwd_exceptions.INVALID_PASSWORD

    current_user.is_active = not current_user.is_active
    await db.commit()

    return {"detail": "账户注销成功"}
