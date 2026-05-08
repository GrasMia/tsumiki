from fastapi import HTTPException, status

SAME_EMAIL = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="邮箱未变更",
)

EMAIL_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="邮箱不存在",
)

EMAIL_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="邮箱已被使用",
)
