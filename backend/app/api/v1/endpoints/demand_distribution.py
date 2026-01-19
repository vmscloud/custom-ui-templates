"""
Demand Distribution API 라우터

Demand Distribution 데이터 조회 API 엔드포인트
"""

from typing import Optional

from app.services.demand_distribution import DemandDistributionService
from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class DemandDistributionQuery(BaseModel):
    """Demand Distribution 조회 요청 파라미터"""

    demandVer: str = Field(..., description="Demand Version ID")
    aggregateType: str = Field(
        default="month", description="집계 타입: day/week/month"
    )
    summary: str = Field(default="sum", description="집계 방식: sum/count")
    uomType: str = Field(default="QTY", description="UOM 타입")
    columns: list[str] = Field(default=[], description="표시할 컬럼 목록")


@router.get("/{project_id}/demand-versions")
async def get_demand_versions(
    project_id: str = Path(..., description="프로젝트 ID"),
):
    """
    Demand Version 목록 조회

    - **project_id**: 프로젝트 ID (필수)

    Returns:
        Demand Version 목록 (TreeSelect용)
    """
    try:
        service = DemandDistributionService()
        return service.get_demand_versions(project_id)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred: {str(e)}"},
        )


@router.post("/{project_id}/demand-distribution")
async def get_demand_distribution(
    project_id: str = Path(..., description="프로젝트 ID"),
    param: DemandDistributionQuery = None,
):
    """
    Demand Distribution 데이터 조회

    - **project_id**: 프로젝트 ID (필수)
    - **demandVer**: Demand Version ID (필수)
    - **aggregateType**: 집계 타입 (day/week/month, 기본: month)
    - **summary**: 집계 방식 (sum/count, 기본: sum)
    - **uomType**: UOM 타입 (기본: QTY)
    - **columns**: 표시할 컬럼 목록

    Sample request:
    ```json
    {
        "demandVer": "2024-01",
        "aggregateType": "month",
        "summary": "sum",
        "uomType": "QTY",
        "columns": ["cust_id", "item_group_id"]
    }
    ```

    Returns:
        Demand Distribution 데이터 및 헤더
    """
    try:
        if param is None:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Request body is required"},
            )

        service = DemandDistributionService()
        return service.get_demand_distribution(
            project_id=project_id,
            demand_ver=param.demandVer,
            aggregate_type=param.aggregateType,
            summary=param.summary,
            uom_type=param.uomType,
            columns=param.columns,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred: {str(e)}"},
        )


@router.get("/{project_id}/demand-distribution-columns")
async def get_demand_distribution_columns(
    project_id: str = Path(..., description="프로젝트 ID"),
):
    """
    Demand Distribution 컬럼 메타데이터 조회

    - **project_id**: 프로젝트 ID (필수)

    Returns:
        컬럼 메타데이터 목록 (MultiSelect용)
    """
    try:
        service = DemandDistributionService()
        return service.get_demand_distribution_columns(project_id)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred: {str(e)}"},
        )


@router.get("/{project_id}/uom-preference")
async def get_uom_preference(
    project_id: str = Path(..., description="프로젝트 ID"),
    user_id: str = Query(..., description="사용자 ID"),
    menu_id: Optional[str] = Query(default=None, description="메뉴 ID"),
):
    """
    UOM Type 사용자 설정 조회

    우선순위: user_setting_value > project_setting_value > default_value

    - **project_id**: 프로젝트 ID (필수)
    - **user_id**: 사용자 ID (필수)
    - **menu_id**: 메뉴 ID (선택)

    Returns:
        UOM 타입 설정
    """
    try:
        service = DemandDistributionService()
        return service.get_uom_preference(project_id, user_id, menu_id)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred: {str(e)}"},
        )
