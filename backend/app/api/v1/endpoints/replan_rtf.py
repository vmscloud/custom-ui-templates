"""
재수립 RTF API 라우터

재수립계획 RTF 현황 데이터 조회 엔드포인트
"""

import logging

from app.core.config import settings
from app.schemas.replan_rtf import (
    ReplanRtfDetailRequest,
    ReplanRtfMainRequest,
    ReplanRtfProdDetailRequest,
)
from app.services.replan_rtf import ReplanRtfService, get_replan_rtf_service
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()
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


@router.post("/summary")
async def get_summary(
    params: ReplanRtfMainRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: ReplanRtfService = Depends(get_replan_rtf_service),
):
    """재수립 RTF 요약 데이터 조회"""
    try:
        return await service.get_summary(project_id, params)
    except ValueError as e:
        return _error_response(400, "RTF 요약 조회", e)
    except Exception as e:
        return _error_response(500, "RTF 요약 조회", e)


@router.post("/detail")
async def get_detail(
    params: ReplanRtfDetailRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: ReplanRtfService = Depends(get_replan_rtf_service),
):
    """재수립 RTF 상세 데이터 조회"""
    try:
        return await service.get_detail(project_id, params)
    except ValueError as e:
        return _error_response(400, "RTF 상세 조회", e)
    except Exception as e:
        return _error_response(500, "RTF 상세 조회", e)


@router.post("/prod-detail")
async def get_prod_detail(
    params: ReplanRtfProdDetailRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: ReplanRtfService = Depends(get_replan_rtf_service),
):
    """생산계획 피벗 데이터 조회"""
    try:
        return await service.get_prod_detail(project_id, params)
    except ValueError as e:
        return _error_response(400, "생산계획 조회", e)
    except Exception as e:
        return _error_response(500, "생산계획 조회", e)


@router.get("/filters/prod-types")
async def get_prod_types(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: ReplanRtfService = Depends(get_replan_rtf_service),
):
    """생산유형 필터 목록 조회"""
    try:
        return await service.get_prod_types(project_id, plan_ver)
    except Exception as e:
        return _error_response(500, "생산유형 목록 조회", e)
