"""
API 라우터 통합

모든 엔드포인트 라우터를 하나로 통합합니다.
"""

from app.api.v1.endpoints import (
    health,
    plan_cycle,
    proxy,
    rtf_report,
)
from fastapi import APIRouter

# 통합 라우터 생성
api_router = APIRouter()

# API 라우터 등록 (도메인별 prefix 적용)
api_router.include_router(health.router, prefix="/api/custom/backend", tags=["health"])
api_router.include_router(
    plan_cycle.router,
    prefix="/api/custom/backend/{project_id}",
    tags=["plan-cycle-api"],
)
api_router.include_router(
    rtf_report.router,
    prefix="/api/custom/backend/{project_id}",
    tags=["rtf-report-api"],
)
api_router.include_router(
    proxy.router,
    prefix="/api/custom/backend/{project_id}",
    tags=["aps-proxy"],
)
