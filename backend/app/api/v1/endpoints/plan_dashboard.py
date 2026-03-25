"""
Plan Dashboard API 라우터

계획 대시보드 데이터 조회/설정 API 엔드포인트
"""

import logging

from app.core.config import settings
from app.schemas.plan_dashboard import (
    DashboardRequest,
    ProdReportRequest,
    ResGroupRequest,
    RtfDetailRequest,
    SettingsSaveRequest,
)
from app.services.plan_dashboard import PlanDashboardService, get_plan_dashboard_service
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _error_response(status_code: int, label: str, exc: Exception) -> JSONResponse:
    """에러 응답 생성 — DEBUG 모드에서만 상세 에러 노출"""
    logger.exception(f"[{label}] {exc}")
    detail = str(exc) if settings.DEBUG else None
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": f"{label} 중 오류가 발생했습니다.",
            **({"detail": detail} if detail else {}),
        },
    )


# ============================================================================
# 메인 대시보드 (1회 호출로 전체 패널 로드)
# ============================================================================


@router.post("/dashboard")
async def get_dashboard(
    params: DashboardRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """메인 대시보드 전체 데이터 조회"""
    try:
        return await service.get_dashboard(project_id, params)
    except ValueError as e:
        return _error_response(400, "대시보드 조회", e)
    except Exception as e:
        return _error_response(500, "대시보드 조회", e)


# ============================================================================
# 개별 패널 리프레시
# ============================================================================


@router.post("/rtf-detail")
async def get_rtf_detail(
    params: RtfDetailRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """RTF 세부 통계 (차트 드릴다운)"""
    try:
        return await service.get_rtf_detail(project_id, params)
    except ValueError as e:
        return _error_response(400, "RTF 상세 조회", e)
    except Exception as e:
        return _error_response(500, "RTF 상세 조회", e)


@router.post("/res-group-report")
async def get_res_group_report(
    params: ResGroupRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """설비 가동 현황 (설정 변경 후 단독 리프레시)"""
    try:
        return await service.get_res_group_report(project_id, params)
    except ValueError as e:
        return _error_response(400, "설비 가동 현황 조회", e)
    except Exception as e:
        return _error_response(500, "설비 가동 현황 조회", e)


@router.post("/prod-report")
async def get_prod_report(
    params: ProdReportRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """생산 현황 (집계 기준 변경 시 단독 리프레시)"""
    try:
        return await service.get_prod_report(project_id, params)
    except ValueError as e:
        return _error_response(400, "생산 현황 조회", e)
    except Exception as e:
        return _error_response(500, "생산 현황 조회", e)


# ============================================================================
# 위젯 설정 API
# ============================================================================


@router.get("/settings")
async def get_settings(
    project_id: str = Path(..., description="프로젝트 ID"),
    user_id: str = Query(..., alias="userId", description="사용자 ID"),
    menu_id: str = Query(
        default="/pa/PlanDashboard2", alias="menuId", description="메뉴 ID"
    ),
    plan_ver: str = Query(default="", alias="planVer", description="Plan version"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """전체 위젯 설정 일괄 조회"""
    try:
        return service.get_settings(project_id, user_id, menu_id, plan_ver)
    except Exception as e:
        return _error_response(500, "설정 조회", e)


@router.put("/settings")
async def save_settings(
    params: SettingsSaveRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """위젯 설정 저장"""
    try:
        return service.save_setting(project_id, params)
    except Exception as e:
        return _error_response(500, "설정 저장", e)


# ============================================================================
# Frozen Version
# ============================================================================


@router.get("/frozen-ver")
async def get_frozen_ver(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: PlanDashboardService = Depends(get_plan_dashboard_service),
):
    """현재 planVer의 frozen 버전 조회"""
    try:
        frozen_ver = service.repo.get_frozen_ver(project_id, plan_ver)
        return {"success": True, "data": {"frozenVer": frozen_ver}}
    except Exception as e:
        return _error_response(500, "Frozen 버전 조회", e)
