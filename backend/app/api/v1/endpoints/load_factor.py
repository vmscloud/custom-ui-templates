"""
부하율 (LoadFactor) API 라우터

공정 그룹별 부하율 데이터 조회 엔드포인트
"""

import logging

from app.core.config import settings
from app.schemas.load_factor import (
    LoadFactorDetailRequest,
    LoadFactorGroupRequest,
    LoadFactorMainRequest,
)
from app.services.load_factor import LoadFactorService, get_load_factor_service
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


@router.get("/oper-groups")
async def get_oper_groups(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., alias="planVer", description="Plan version"),
    service: LoadFactorService = Depends(get_load_factor_service),
):
    """공정 그룹 목록 조회"""
    try:
        data = await service.get_oper_groups(project_id, plan_ver)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        return _error_response(500, "공정 그룹 목록 조회", e)


@router.post("/main")
async def get_main(
    params: LoadFactorMainRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: LoadFactorService = Depends(get_load_factor_service),
):
    """공정 그룹별 총 부하율 조회"""
    try:
        return await service.get_main(project_id, params)
    except ValueError as e:
        return _error_response(400, "부하율 메인 조회", e)
    except Exception as e:
        return _error_response(500, "부하율 메인 조회", e)


@router.post("/group")
async def get_group(
    params: LoadFactorGroupRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: LoadFactorService = Depends(get_load_factor_service),
):
    """공정 그룹별 일간 item_group 분해 조회"""
    try:
        return await service.get_group(project_id, params)
    except ValueError as e:
        return _error_response(400, "부하율 그룹 조회", e)
    except Exception as e:
        return _error_response(500, "부하율 그룹 조회", e)


@router.post("/detail")
async def get_detail(
    params: LoadFactorDetailRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: LoadFactorService = Depends(get_load_factor_service),
):
    """공정 그룹별 수요별 상세 조회"""
    try:
        return await service.get_detail(project_id, params)
    except ValueError as e:
        return _error_response(400, "부하율 상세 조회", e)
    except Exception as e:
        return _error_response(500, "부하율 상세 조회", e)
