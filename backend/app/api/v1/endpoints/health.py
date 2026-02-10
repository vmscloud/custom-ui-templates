"""
Health Check API

서비스 상태 확인 엔드포인트
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)
