from fastapi import HTTPException, status

INVALID_PASSWORD = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="密码错误",
)

PASSWORD_TOO_SHORT = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="密码长度不能少于8位",
)

SAME_PASSWORD = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="新密码不能与旧密码相同",
)
