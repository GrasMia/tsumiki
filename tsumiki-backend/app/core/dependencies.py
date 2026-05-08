from fastapi import Cookie, HTTPException, Query, status
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta, timezone
import jwt

from app.config import settings
from app.exceptions import INVALID_CREDENTIALS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user_id(token: str = Security(oauth2_scheme)) -> int:
    if not token:
        raise INVALID_CREDENTIALS

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
        raise INVALID_CREDENTIALS
    except Exception:
        raise

    return int(sub)


def get_current_user_id_by_query(token: str = Query(None)) -> int:
    if not token:
        raise INVALID_CREDENTIALS
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        sub: str | None = payload.get("sub")
        if not sub:
            raise INVALID_CREDENTIALS
    except jwt.InvalidTokenError:
        raise INVALID_CREDENTIALS
    except Exception:
        raise

    return int(sub)


def get_current_user_id_by_cookie(refresh_token: str = Cookie(None)) -> int:
    if not refresh_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "证书不存在或已过期请重新登录")

    try:
        payload = jwt.decode(
            jwt=refresh_token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        sub: str | None = payload.get("sub")
        if not sub:
            raise INVALID_CREDENTIALS
    except jwt.InvalidTokenError:
        raise INVALID_CREDENTIALS
    except Exception:
        raise

    return int(sub)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def refresh_access_token(refresh_token: str) -> str:
    """使用 Refresh Token 生成新的 Access Token"""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise INVALID_CREDENTIALS
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token 无效或已过期")
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, e.args)

    return create_access_token(data={"sub": user_id})
