"""Freeze Plan API 라우터"""
import logging
from app.core.config import settings
from app.schemas.freeze_plan import FrozenStatusRequest, FrozenPlanRequest, FrozenPeriodRequest
from app.repositories.freeze_plan import FreezePlanRepository
from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

def _error_response(status_code, label, exc):
    logger.exception(f"[{label}] {exc}")
    detail = str(exc) if settings.DEBUG else None
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": f"{label} 중 오류가 발생했습니다.", **({"detail": detail} if detail else {})},
    )

@router.get("/status")
async def get_frozen_status(
    project_id: str = Path(...),
    plan_cycle_id: str = Query(..., alias="planCycleID"),
):
    """frozen 상태 조회"""
    try:
        rows = FreezePlanRepository.get_frozen_status(project_id, plan_cycle_id)
        return {"success": True, "data": rows}
    except Exception as e:
        return _error_response(500, "Frozen 상태 조회", e)

@router.put("/description")
async def update_frozen_desc(
    params: FrozenPlanRequest,
    project_id: str = Path(...),
):
    """frozen 설명 수정"""
    try:
        rowcount = FreezePlanRepository.update_frozen_desc(project_id, params.planCycleID, params.description)
        return {"success": True, "rowcount": rowcount}
    except Exception as e:
        return _error_response(500, "Frozen 설명 수정", e)

@router.post("/execute")
async def freeze_plan(
    params: FrozenPlanRequest,
    project_id: str = Path(...),
):
    """계획 확정 실행"""
    try:
        rowcount = FreezePlanRepository.freeze_plan(
            project_id, params.planVer, params.planCycleID,
            "", params.description  # userId is empty for now
        )
        return {"success": True, "rowcount": rowcount}
    except Exception as e:
        return _error_response(500, "계획 확정 실행", e)

@router.post("/cancel")
async def cancel_freeze(
    params: FrozenPlanRequest,
    project_id: str = Path(...),
):
    """계획 확정 취소"""
    try:
        rowcount = FreezePlanRepository.unfreeze_plan(
            project_id, params.planVer, params.planCycleID, ""
        )
        return {"success": True, "rowcount": rowcount}
    except Exception as e:
        return _error_response(500, "계획 확정 취소", e)

@router.post("/period")
async def get_frozen_period(
    params: FrozenPeriodRequest,
    project_id: str = Path(...),
):
    """frozen 기간 조회"""
    try:
        rows = FreezePlanRepository.get_frozen_period(project_id, params.planVer)
        return {"success": True, "data": rows[0] if rows else None}
    except Exception as e:
        return _error_response(500, "Frozen 기간 조회", e)
