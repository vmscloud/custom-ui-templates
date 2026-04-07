"""
RTF Report API 라우터

프론트엔드의 apiCall이 보내는 RTF 관련 요청을 처리합니다.
프론트엔드는 { apiUrl, ...params } 형태로 POST 요청을 보냅니다.
"""

import logging
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.services.rtf_report import RtfReportService
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)


class RtfProxyRequest(BaseModel):
    """RTF 프록시 요청 모델"""

    apiUrl: str = Field(..., description="원본 APS API URL (예: RarRtfReport/Main2)")

    # 공통 파라미터
    planVer: str | None = Field(default=None, description="Plan Version")
    demandID: str | None = Field(default=None, description="Demand ID")
    demandIDs: list[str] | None = Field(default=None, description="Demand ID 목록")

    # Main/Detail 파라미터
    aggregateType: str | None = Field(default=None, description="WEEK/MONTH")
    summary: str | None = Field(default=None, description="요약 유형")
    uomType: str | None = Field(default=None, description="DEFAULT/CONVERSION")
    prodStatus: str | None = Field(default=None, description="생산 상태 필터")
    customers: list[str] | None = Field(default=None, description="고객 필터")
    itemGroupIDs: list[str] | None = Field(default=None, description="품목그룹 필터")
    regions: list[str] | None = Field(default=None, description="지역 필터")
    demandTypes: list[str] | None = Field(default=None, description="수요유형 필터")
    productionArea: str | None = Field(default=None, description="생산영역 필터")
    prodTypes: list[str] | None = Field(default=None, description="생산유형 필터")

    # Detail 추가 파라미터
    dueMonth: str | None = Field(default=None, description="월 필터")
    dueWeek: str | None = Field(default=None, description="주 필터")

    # 기타
    fromDate: str | None = Field(default=None, description="시작일")
    toDate: str | None = Field(default=None, description="종료일")
    planCycleID: str | None = Field(default=None, description="Plan Cycle ID")

    # Widget 설정
    userID: str | None = Field(default=None, description="사용자 ID")

    class Config:
        extra = "allow"  # 알 수 없는 필드 허용


async def _trino_query(adapter: QueryExecutorAdapter, project_id: str, sql: str) -> list[dict]:
    result = await adapter.execute_direct_query(
        project_id=project_id, query=sql,
        catalog=settings.TRINO_CATALOG_ICEBERG, schema=settings.TRINO_SCHEMA_APS,
    )
    return result.get("row", []) if result.get("success") else []


@router.get("/rtf-report/filters/customers")
async def get_filter_customers(
    project_id: str = Path(...),
    plan_ver: str = Query(..., alias="plan_ver"),
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> dict[str, Any]:
    """고객 필터 목록 조회 (Iceberg 직접)"""
    try:
        pk = f"{project_id}@{plan_ver[:6]}"
        sql = f"""
        SELECT DISTINCT
            a.cust_id,
            b.cust_name,
            CONCAT(a.cust_id, ' / ',
                CASE WHEN COALESCE(b.cust_name, '') = ''
                     THEN a.cust_id ELSE b.cust_name END
            ) AS cust_label
        FROM rpt_shipment_plan a
        LEFT JOIN odv_cust_master b
            ON a.partition_key = b.partition_key AND a.cust_id = b.cust_id AND a.plan_ver = b.plan_ver
        WHERE a.partition_key = '{pk}' AND a.plan_ver = '{plan_ver}'
          AND (a.demand_type != 'SafetyStock' OR a.demand_type IS NULL)
        ORDER BY a.cust_id
        """
        data = await _trino_query(adapter, project_id, sql)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        logger.exception(f"[고객 필터 조회] {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.get("/rtf-report/filters/item-groups")
async def get_filter_item_groups(
    project_id: str = Path(...),
    plan_ver: str = Query(..., alias="plan_ver"),
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> dict[str, Any]:
    """품목 그룹 필터 목록 조회 (Iceberg 직접)"""
    try:
        pk = f"{project_id}@{plan_ver[:6]}"
        sql = f"""
        SELECT DISTINCT item_group_id AS item_group
        FROM rpt_shipment_plan
        WHERE partition_key = '{pk}' AND plan_ver = '{plan_ver}'
          AND (demand_type != 'SafetyStock' OR demand_type IS NULL)
        ORDER BY item_group_id
        """
        data = await _trino_query(adapter, project_id, sql)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        logger.exception(f"[품목그룹 필터 조회] {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/rtf-report/proxy")
def rtf_report_proxy(
    project_id: str = Path(..., description="프로젝트 ID"),
    body: RtfProxyRequest = None,
) -> dict[str, Any]:
    """
    RTF Report 프록시 엔드포인트 (레거시 — body.apiUrl로 라우팅)
    """
    if body is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Request body is required"},
        )

    try:
        service = RtfReportService()
        params = body.model_dump(exclude_none=True)
        result = service.dispatch(project_id, body.apiUrl, params)
        return result

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Internal server error: {str(e)}"},
        )


@router.post("/rtf-report/{api_name:path}")
def rtf_report_named(
    project_id: str = Path(..., description="프로젝트 ID"),
    api_name: str = Path(..., description="API 이름 (예: RarRtfReport/Main2)"),
    body: dict[str, Any] = None,
) -> dict[str, Any]:
    """
    RTF Report 네임드 엔드포인트 — URL 경로에 API 이름 포함

    네트워크 탭에서 각 API 이름이 보이도록 URL 경로 기반 라우팅.
    예: POST /rtf-report/RarRtfReport/Main2
    """
    if body is None:
        body = {}

    try:
        service = RtfReportService()
        result = service.dispatch(project_id, api_name, body)
        return result

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Internal server error: {str(e)}"},
        )
