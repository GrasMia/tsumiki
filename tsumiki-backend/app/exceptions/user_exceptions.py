from fastapi import HTTPException, status

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无法验证凭证",
    headers={"WWW-Authenticate": "Bearer"},
)

USER_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="未授权",
    headers={"WWW-Authenticate": "Bearer"},
)

USER_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="用户名或邮箱已存在",
)

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="用户不存在",
)

USER_INACTIVE = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="用户账户已被禁用",
)

SAME_USERNAME = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="用户名未变更",
)

USER_INCONSISTENT = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="用户信息不匹配",
)

USERNAME_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="用户名已被使用",
)

