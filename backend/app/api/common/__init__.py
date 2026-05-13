from fastapi import APIRouter
common_router = APIRouter()
@common_router.get("/health", summary="健康检查")
async def health_check():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
