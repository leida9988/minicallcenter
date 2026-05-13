import time
import json
from typing import Optional
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.system import OperationLog
from app.utils.logger import logger
from app.utils.redis_client import RedisClient
class OperationLogMiddleware(BaseHTTPMiddleware):
    """
    操作日志中间件，自动记录用户操作
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # 需要排除的路径
        self.exclude_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/favicon.ico",
            "/static"
        ]
        # 需要排除的方法
        self.exclude_methods = ["OPTIONS", "HEAD"]
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        # 检查是否需要记录日志
        path = request.url.path
        method = request.method
        if (self._is_exclude_path(path) or
            method in self.exclude_methods or
            path.startswith("/api/common/")):
            return await call_next(request)
        # 获取请求信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        # 获取用户信息（从token中解析）
        user_id, username = await self._get_user_info(request)
        # 获取请求参数
        request_params = await self._get_request_params(request)
        # 执行请求
        try:
            response = await call_next(request)
            # 计算耗时
            cost_time = int((time.time() - start_time) * 1000)
            # 记录成功日志
            await self._save_log(
                user_id=user_id,
                username=username,
                path=path,
                method=method,
                ip=client_ip,
                user_agent=user_agent,
                request_params=request_params,
                status=1 if response.status_code < 400 else 2,
                error_msg=None,
                cost_time=cost_time
            )
            return response
        except Exception as e:
            # 计算耗时
            cost_time = int((time.time() - start_time) * 1000)
            # 记录失败日志
            await self._save_log(
                user_id=user_id,
                username=username,
                path=path,
                method=method,
                ip=client_ip,
                user_agent=user_agent,
                request_params=request_params,
                status=2,
                error_msg=str(e),
                cost_time=cost_time
            )
            raise
    def _is_exclude_path(self, path: str) -> bool:
        """
        检查是否是排除路径
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP
        """
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip
        return request.client.host if request.client else ""
    async def _get_user_info(self, request: Request) -> tuple[Optional[int], Optional[str]]:
        """
        从请求头中获取用户信息
        """
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None, None
        token = authorization.split(" ")[1]
        try:
            # 从Redis中获取用户信息
            user_info = await RedisClient.get(f"user_token:{token}")
            if user_info:
                return user_info.get("user_id"), user_info.get("username")
            # 如果Redis中没有，尝试解析token
            from app.utils.security import decode_token
            payload = decode_token(token)
            user_id = payload.get("sub")
            if user_id:
                # 这里可以从数据库查询用户名，但为了性能建议登录时将用户信息存入Redis
                return user_id, None
        except Exception as e:
            logger.warning(f"解析用户信息失败: {e}")
        return None, None
    async def _get_request_params(self, request: Request) -> dict:
        """
        获取请求参数
        """
        params = {}
        # 获取查询参数
        if request.query_params:
            params.update(dict(request.query_params))
        # 获取路径参数
        if request.path_params:
            params.update(request.path_params)
        # 获取请求体参数（只处理JSON格式）
        try:
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                content_type = request.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    body = await request.json()
                    # 过滤敏感字段
                    sensitive_fields = ["password", "old_password", "new_password", "token", "secret"]
                    for field in sensitive_fields:
                        if field in body:
                            body[field] = "***"
                    params.update(body)
        except Exception as e:
            logger.debug(f"获取请求体参数失败: {e}")
        return params
    async def _save_log(
        self,
        user_id: Optional[int],
        username: Optional[str],
        path: str,
        method: str,
        ip: str,
        user_agent: str,
        request_params: dict,
        status: int,
        error_msg: Optional[str],
        cost_time: int
    ):
        """
        保存操作日志到数据库
        """
        try:
            # 解析模块和操作
            module = self._get_module(path)
            operation = self._get_operation(method, path)
            # 创建日志记录
            async with AsyncSessionLocal() as db:
                log = OperationLog(
                    user_id=user_id,
                    username=username,
                    module=module,
                    operation=operation,
                    method=method,
                    path=path,
                    ip=ip,
                    user_agent=user_agent,
                    request_params=request_params if request_params else None,
                    status=status,
                    error_msg=error_msg,
                    cost_time=cost_time
                )
                db.add(log)
                await db.commit()
        except Exception as e:
            logger.error(f"保存操作日志失败: {e}", exc_info=True)
    def _get_module(self, path: str) -> str:
        """
        根据路径获取模块名称
        """
        path_segments = path.split("/")
        if len(path_segments) >= 4 and path_segments[1] == "api" and path_segments[2] == "v1":
            module_map = {
                "auth": "认证管理",
                "user": "用户管理",
                "role": "角色管理",
                "permission": "权限管理",
                "system": "系统配置",
                "customer": "客户管理",
                "call": "呼叫中心",
                "report": "统计报表",
                "ai": "AI服务"
            }
            return module_map.get(path_segments[3], "其他")
        return "其他"
    def _get_operation(self, method: str, path: str) -> str:
        """
        根据方法和路径获取操作类型
        """
        method_map = {
            "GET": "查询",
            "POST": "创建",
            "PUT": "更新",
            "PATCH": "更新",
            "DELETE": "删除"
        }
        base_operation = method_map.get(method, "其他")
        # 特殊路径处理
        if "/login" in path:
            return "登录"
        if "/logout" in path:
            return "登出"
        if "/import" in path:
            return "导入"
        if "/export" in path:
            return "导出"
        if "/upload" in path:
            return "上传"
        if "/download" in path:
            return "下载"
        return base_operation
