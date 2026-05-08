from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "tsumiki"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    SECRET_KEY: str = "default_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 15

    DATABASE_URL: str = "postgresql://postgres@localhost/postgres"

    LOCAL_STORAGE_PATH: str = "./wwwroot/files"
    LOCAL_AVATAR_PATH: str = "./wwwroot/avatars"

    UPLOAD_FILE_CHUNK_SIZE: int = 5

    # pydantic_settings 类属性上的默认值（如 DEBUG: bool = True）是备用默认值
    model_config = SettingsConfigDict(
        env_file=".env",  # 服务器根目录的 .env 文件中的值会覆盖这些默认值（若该文件存在）
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()


# 运行此文件测试 .env 是否加载成功
if __name__ == "__main__":
    from pprint import pprint

    pprint(settings.model_dump())
