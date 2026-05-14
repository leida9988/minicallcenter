from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 服务配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_WORKERS: int = 2
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "callcenter"
    DB_CHARSET: str = "utf8mb4"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # FreeSWITCH配置
    FS_HOST: str = "localhost"
    FS_PORT: int = 8021
    FS_PASSWORD: str = "ClueCon"
    FS_RECORDING_PATH: str = "/var/lib/freeswitch/recordings"

    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local or minio
    LOCAL_STORAGE_PATH: str = "./data/storage"
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET: str = "callcenter"
    MINIO_SECURE: bool = False

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "./logs"

    # AI服务配置
    ASR_PROVIDER: Optional[str] = None
    ASR_ACCESS_KEY: Optional[str] = None
    ASR_SECRET_KEY: Optional[str] = None
    ASR_APP_ID: Optional[str] = None

    TTS_PROVIDER: Optional[str] = None
    TTS_ACCESS_KEY: Optional[str] = None
    TTS_SECRET_KEY: Optional[str] = None
    TTS_APP_ID: Optional[str] = None

    LLM_PROVIDER: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_API_BASE: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"

    # 其他配置
    MAX_UPLOAD_SIZE: str = "100MB"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8080"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset={self.DB_CHARSET}"

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
settings = Settings()
# OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

