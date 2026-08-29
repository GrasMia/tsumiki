from fastapi import HTTPException, status
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta, timezone
import jwt

from app.config import settings
from app.exceptions import INVALID_CREDENTIALS, USER_INCONSISTENT

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_access_token(access_token: str = Security(oauth2_scheme)) -> str:
    if not access_token:
        raise INVALID_CREDENTIALS

    return access_token


def get_current_user_id(token: str = Security(oauth2_scheme)) -> int:
    if not token:
        raise INVALID_CREDENTIALS
    if token.startswith(f"{settings.ACCESS_TOKEN_TYPE} "):
        token = token.replace(f"{settings.ACCESS_TOKEN_TYPE} ", "")

    try:
        """jwt.decode() 参数说明：
        参数	        作用	            是否必须
        token	    JWT 字符串	            ✅ 必须
        key	            密钥	            ✅ 必须
        algorithms	允许的算法列表	         ✅ 必须
        subject	    要求 sub 字段等于此值	 ❌ 可选
        audience	要求 aud 字段等于此值	 ❌ 可选
        issuer	    要求 iss 字段等于此值	 ❌ 可选
        leeway	    时间误差容忍度（秒）	  ❌ 可选
        """
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        sub: str | None = payload.get("sub")
        if not sub:
            raise INVALID_CREDENTIALS
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token 无效或已过期")

    return int(sub)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return f"{settings.ACCESS_TOKEN_TYPE} {jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)}"


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def refresh_access_token(current_user_id: str, access_token: str) -> str:
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise INVALID_CREDENTIALS
        if user_id != current_user_id:
            raise USER_INCONSISTENT
        else:
            return access_token  # 返回未过期的 access_token
    except jwt.InvalidTokenError as e:
        if str(e) == "Signature has expired":
            return create_access_token(data={"sub": current_user_id})  # access_token 已过期 → 返回新的 access_token
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
