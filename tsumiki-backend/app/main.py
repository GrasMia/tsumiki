from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path

from app.api import auth_router, user_router, disk_router
from app.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

STORAGE_PATH = Path(settings.LOCAL_STATIC_PATH)  # 物理文件存储根目录
STORAGE_PATH.mkdir(exist_ok=True)  # 确保目录存在
app.mount("/static", StaticFiles(directory="wwwroot/static"), "static")

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(disk_router, prefix="/disk")
