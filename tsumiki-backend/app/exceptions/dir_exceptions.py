from fastapi import HTTPException, status

DIR_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="目录不存在",
)

DIR_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="当前目录下已存在同名目录",
)
