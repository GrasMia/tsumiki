from fastapi import HTTPException, status

FILE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="文件不存在",
)

FILE_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="当前目录下已存在同名文件",
)

INVALID_FILE_NAME = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="无效的文件名",
)

FILE_ALREADY_DELETED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="文件已被删除",
)
