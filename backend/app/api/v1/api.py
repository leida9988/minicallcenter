from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, role, permission, customer, call, report, system, config
from app.api.v1.ai.router import router as ai_router
api_router = APIRouter()
# 认证相关
api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])
# 系统管理相关
api_router.include_router(user.router, prefix="/user", tags=["用户管理"])
api_router.include_router(role.router, prefix="/role", tags=["角色管理"])
api_router.include_router(permission.router, prefix="/permission", tags=["权限管理"])
api_router.include_router(system.router, prefix="/system", tags=["系统配置"])
# 业务功能
api_router.include_router(customer.router, prefix="/customer", tags=["客户管理"])
api_router.include_router(call.router, prefix="/call", tags=["呼叫中心"])
api_router.include_router(report.router, prefix="/report", tags=["统计报表"])
# AI服务
api_router.include_router(ai_router)
# 配置管理
api_router.include_router(config.router)
