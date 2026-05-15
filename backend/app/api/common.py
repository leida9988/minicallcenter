from fastapi import APIRouter
router = APIRouter(tags=["公共接口"])
@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查接口"""
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
# 兼容docker健康检查路径
@router.get("/v1/health", summary="健康检查（兼容路径）")
async def health_check_v1():
    return await health_check()
