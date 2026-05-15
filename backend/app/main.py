import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.middleware import OperationLogMiddleware
from app.db.session import engine, Base
from app.utils.logger import logger
from app.utils.redis_client import RedisClient
from app.api.v1.api import api_router
from app.api.common import common_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info("系统启动中...")
    # 创建数据库表（生产环境建议使用 Alembic 迁移）
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")
    # 初始化Redis连接
    await RedisClient.get_instance()
    logger.info("Redis连接初始化完成")
    yield
    # 关闭事件
    logger.info("系统关闭中...")
    # 关闭Redis连接
    await RedisClient.close()
    logger.info("Redis连接已关闭")
def create_app() -> FastAPI:
    app = FastAPI(
        title="电话营销系统 API",
        description="通用型中小型电话营销系统后端接口文档",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 添加操作日志中间件
    app.add_middleware(OperationLogMiddleware)
    # 全局异常处理
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTP异常: {exc.status_code} - {exc.detail} - {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": None},
        )
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"参数验证异常: {exc.errors()} - {request.url}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "参数验证失败",
                "data": exc.errors(),
            },
        )
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"系统异常: {str(exc)} - {request.url}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "服务器内部错误",
                "data": None,
            },
        )
    # 注册路由
    app.include_router(common_router, prefix="/api/common", tags=["公共接口"])
    app.include_router(api_router, prefix="/api/v1", tags=["V1接口"])
    # 根路由
    @app.get("/", summary="根路径")
    async def root():
        return {
            "code": 200,
            "message": "电话营销系统 API 服务运行正常",
            "data": {
                "version": "1.0.0",
                "docs": "/docs" if settings.DEBUG else None
            }
        }
    # 健康检查接口（兼容docker健康检查）
    @app.get("/api/v1/health", summary="健康检查")
    async def health_check():
        return {"code": 200, "message": "success", "data": {"status": "ok"}}
    return app
app = create_app()
def main():
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        workers=settings.SERVER_WORKERS,
        reload=settings.DEBUG,
    )
if __name__ == "__main__":
    main()
