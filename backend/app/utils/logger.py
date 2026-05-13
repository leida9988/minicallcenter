import os
import sys
from loguru import logger
from app.core.config import settings
# 确保日志目录存在
os.makedirs(settings.LOG_PATH, exist_ok=True)
# 移除默认处理器
logger.remove()
# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    enqueue=True,
)
# 错误日志文件
logger.add(
    os.path.join(settings.LOG_PATH, "error.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
)
# 访问日志文件
logger.add(
    os.path.join(settings.LOG_PATH, "access.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="INFO",
    filter=lambda record: record["extra"].get("type") == "access",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
)
# 应用日志文件
logger.add(
    os.path.join(settings.LOG_PATH, "app.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    filter=lambda record: record["extra"].get("type") != "access",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
)
# 导出logger实例
__all__ = ["logger"]
