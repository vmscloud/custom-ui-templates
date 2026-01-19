"""
API 라우터 통합

모든 엔드포인트 라우터를 하나로 통합합니다.
"""

from app.api.v1.endpoints import item_master, plan_cycle
from fastapi import APIRouter

# 통합 라우터 생성
api_router = APIRouter()

# API 라우터 등록 (도메인별 prefix 적용)
api_router.include_router(
    item_master.router, prefix="/api/item-master", tags=["item-master-api"]
)
api_router.include_router(
    plan_cycle.router, prefix="/api", tags=["plan-cycle-api"]
)
