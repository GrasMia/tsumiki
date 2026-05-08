from fastapi import HTTPException, status

SHARE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="分享链接不存在",
)

SHARE_EXPIRED = HTTPException(
    status_code=status.HTTP_410_GONE,
    detail="分享链接已过期",
)

INVALID_SHARE_PASSWORD = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="分享密码错误",
)
