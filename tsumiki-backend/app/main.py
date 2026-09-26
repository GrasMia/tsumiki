from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
from pathlib import Path
import asyncio

from app.api import auth_router, user_router, disk_router
from app.config import settings
from app.services import StorageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(StorageService.delayed_cleanup())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

STORAGE_PATH = Path(settings.LOCAL_STATIC_PATH)
STORAGE_PATH.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="wwwroot/static"), "static")

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(disk_router, prefix="/disk")
