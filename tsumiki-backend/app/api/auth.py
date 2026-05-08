from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from app.config import settings
from app.models import User, Dir
from app.db import get_db_async, get_db_async_auto
from app.schemas import RegisterParams, AuthResponse
from app.schemas.user import UserProfile
from app.utils import validate_password, validate_username
from app.core.security import verify_password, get_password_hash
from app.exceptions import EMAIL_ALREADY_EXISTS, USERNAME_ALREADY_EXISTS, USER_NOT_FOUND
from app.core.dependencies import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    get_current_user_id_by_cookie,
)

router = APIRouter(tags=["authentication"])


@router.post("/register")
async def register(user_data: RegisterParams, db: AsyncSession = Depends(get_db_async)):
    user_data.username = validate_username(user_data.username)
    user_data.password = validate_password(user_data.password)

    stmt = select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    existing_user = await db.scalar(stmt)
    if existing_user:
        if existing_user.username == user_data.username:
            raise USERNAME_ALREADY_EXISTS
        else:
            raise EMAIL_ALREADY_EXISTS

    new_user = await db.scalar(
        insert(User)
        .values(**user_data.model_dump(exclude={"password"}), hashed_password=get_password_hash(user_data.password))
        .returning(User)
    )
    if not new_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请求异常，账户创建失败")

    user_root_dir = await db.scalar(
        insert(Dir)
        .values(
            name=str(new_user.id),
            path=f"/{new_user.id}/",
            user_id=new_user.id,
            parent_id=0,  # 固定为根目录 ID
        )
        .returning(Dir)
    )
    if user_root_dir is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请求异常，账户创建失败(无法获取根目录)")

    await db.commit()

    return {"detail": "账户注册成功"}


@router.post("/login", response_model=AuthResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_async_auto),
):
    form_data.username = validate_username(form_data.username)
    form_data.password = validate_password(form_data.password)

    # 支持 username 或 email 登录
    stmt = select(User).where((User.username == form_data.username) | (User.email == form_data.username))
    user = await db.scalar(stmt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请检查用户名或邮箱")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已注销的账户")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="错误的密码")

    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=create_refresh_token(data={"sub": str(user.id)}),
        httponly=True,  # JS 无法读取
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/auth/refresh",  # 只在访问 /auth/refresh 这个路径时才会被发送到服务器
    )

    return AuthResponse(user=UserProfile.model_validate(user), access_token=access_token)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"detail": "已注销登录"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str = Cookie(None),
    current_user_id: int = Depends(get_current_user_id_by_cookie),
    db: AsyncSession = Depends(get_db_async_auto),
):
    current_user = await db.scalar(select(User).where(User.id == current_user_id))
    if not current_user:
        raise USER_NOT_FOUND

    new_access_token = refresh_access_token(refresh_token)

    return AuthResponse(user=UserProfile.model_validate(current_user), access_token=new_access_token)
