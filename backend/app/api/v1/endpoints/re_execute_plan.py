"""
재실행 계획 (ReExecutePlan) API 라우터

재실행 계획 데이터 조회 엔드포인트
"""

import logging

from app.core.config import settings
from app.schemas.re_execute_plan import ReExecuteMainRequest
from app.services.re_execute_plan import ReExecutePlanService, get_re_execute_plan_service
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.aps_proxy import router as aps_proxy_router

router = APIRouter()
router.include_router(aps_proxy_router)
logger = logging.getLogger(__name__)


def _error_response(status_code: int, label: str, exc: Exception) -> JSONResponse:
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


@router.get("/regions")
async def get_regions(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """지역 목록 조회"""
    try:
        data = await service.get_regions(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "지역 목록 조회", e)


@router.get("/oper-groups")
async def get_oper_groups(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """공정 그룹 목록 조회"""
    try:
        data = await service.get_oper_groups(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "공정 그룹 목록 조회", e)


@router.get("/buffers")
async def get_buffers(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """버퍼 목록 조회"""
    try:
        data = await service.get_buffers(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "버퍼 목록 조회", e)


@router.get("/opers")
async def get_opers(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """공정 목록 조회"""
    try:
        data = await service.get_opers(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "공정 목록 조회", e)


@router.get("/customers")
async def get_customers(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """고객 목록 조회"""
    try:
        data = await service.get_customers(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "고객 목록 조회", e)


@router.get("/item-groups")
async def get_item_groups(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """품목그룹 목록 조회"""
    try:
        data = await service.get_item_groups(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "품목그룹 목록 조회", e)


@router.get("/demand-types")
async def get_demand_types(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """수요유형 목록 조회"""
    try:
        data = await service.get_demand_types(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "수요유형 목록 조회", e)


@router.get("/plan-cycle-info")
async def get_plan_cycle_info(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """계획 재실행 '버전 정보' 팝업용 — cycle id + frozen plan ver."""
    try:
        data = service.get_plan_cycle_info(project_id, plan_ver)
        return {"success": True, "data": data}
    except Exception as e:
        return _error_response(500, "플랜 사이클 정보 조회", e)


@router.get("/demand-vers")
async def get_demand_vers(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_cycle_id: str = Query(..., alias="planCycleID", description="Plan cycle ID"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """수요 버전 목록 — 원본 ComDemandVer 동등."""
    try:
        data = service.get_demand_vers(project_id, plan_cycle_id)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "수요 버전 목록 조회", e)


@router.post("/main")
async def get_main(
    params: ReExecuteMainRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: ReExecutePlanService = Depends(get_re_execute_plan_service),
):
    """재실행 계획 메인 데이터 조회 (피벗 + 수요 목록)"""
    try:
        return await service.get_main(project_id, params)
    except ValueError as e:
        return _error_response(400, "재실행 계획 메인 조회", e)
    except Exception as e:
        return _error_response(500, "재실행 계획 메인 조회", e)
