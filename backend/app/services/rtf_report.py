"""
RTF Report 서비스

QueryExecutorAdapter를 통해 Query Manager에 등록된 쿼리를 실행합니다.
"""

from __future__ import annotations

from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.schemas.rtf_report import (
    RtfBomMapRequest,
    RtfBufferPlanTargetRequest,
    RtfDemandRecordRequest,
    RtfDemandRequest,
    RtfDemandSummaryRequest,
    RtfDetailRequest,
    RtfItemPropsRequest,
    RtfSummaryRequest,
)
from fastapi import Depends


class RtfReportService:
    """RTF Report 비즈니스 로직"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter

    async def _execute(
        self,
        project_id: str,
        query_id: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """쿼리 실행 공통 메서드"""
        result = await self.adapter.execute_query(
            project_id=project_id,
            query_id=query_id,
            parameters=parameters,
        )
        if not result.get("success"):
            raise ValueError(result.get("message", "쿼리 실행 실패"))
        return {
            "success": True,
            "count": result["rowcount"],
            "data": result["row"],
        }

    @staticmethod
    def _join_list(items: list[str]) -> str:
        """배열을 comma-separated 문자열로 변환"""
        return ",".join(items) if items else ""

    # === 핵심 데이터 API ===

    async def get_summary(
        self, project_id: str, params: RtfSummaryRequest
    ) -> dict[str, Any]:
        """RTF 요약 그리드 데이터 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_report_summary",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "aggregate_type": params.aggregateType,
                "summary": params.summary,
                "customers": self._join_list(params.customers),
                "item_group_ids": self._join_list(params.itemGroupIDs),
                "regions": self._join_list(params.regions),
                "demand_types": self._join_list(params.demandTypes),
                "prod_status": params.prodStatus,
                "uom_type": params.uomType,
            },
        )

    async def get_detail(
        self, project_id: str, params: RtfDetailRequest
    ) -> dict[str, Any]:
        """RTF 상세 그리드 데이터 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_report_detail",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "aggregate_type": params.aggregateType,
                "summary": params.summary,
                "group_key": params.groupKey or "",
                "due_month": params.dueMonth or "",
                "due_week": params.dueWeek or "",
                "customers": self._join_list(params.customers),
                "item_group_ids": self._join_list(params.itemGroupIDs),
                "regions": self._join_list(params.regions),
                "demand_types": self._join_list(params.demandTypes),
                "prod_status": params.prodStatus,
                "uom_type": params.uomType,
            },
        )

    async def get_short(
        self, project_id: str, params: RtfDemandRequest
    ) -> dict[str, Any]:
        """부족(Short) 사유 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_report_short",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
                "uom_type": params.uomType,
            },
        )

    async def get_prod_detail(
        self, project_id: str, params: RtfDemandRequest
    ) -> dict[str, Any]:
        """생산계획 피벗 데이터 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_prod_detail",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
                "uom_type": params.uomType,
            },
        )

    async def get_buffer_plan_target(
        self, project_id: str, params: RtfBufferPlanTargetRequest
    ) -> dict[str, Any]:
        """버퍼 계획 Target vs 실적 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_buffer_plan_target",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
            },
        )

    async def get_demand_summary(
        self, project_id: str, params: RtfDemandSummaryRequest
    ) -> dict[str, Any]:
        """수요 요약 메트릭 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_demand_summary",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_ids": self._join_list(params.demandIDs),
                "uom_type": params.uomType,
            },
        )

    async def get_demand_info(
        self, project_id: str, params: RtfDemandRequest
    ) -> dict[str, Any]:
        """수요 상세 정보 조회 (모달)"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_demand_info",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
                "uom_type": params.uomType,
            },
        )

    async def get_peg_info(
        self, project_id: str, params: RtfDemandRequest
    ) -> dict[str, Any]:
        """Peg 정보 상세 조회 (모달)"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_peg_info_detail",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
                "uom_type": params.uomType,
            },
        )

    async def get_bom_map(
        self, project_id: str, params: RtfBomMapRequest
    ) -> dict[str, Any]:
        """BOM 구조 조회 (모달)"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_bom_map",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
                "only_target_bom": str(params.onlyTargetBom).lower(),
                "uom_type": params.uomType,
            },
        )

    async def get_item_props(
        self, project_id: str, params: RtfItemPropsRequest
    ) -> dict[str, Any]:
        """품목 속성 조회 (모달)"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_item_props",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "item_id": params.itemID,
            },
        )

    async def get_demand_record(
        self, project_id: str, params: RtfDemandRecordRequest
    ) -> dict[str, Any]:
        """수요 레코드 상세 조회 (모달)"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_demand_record",
            parameters={
                "project_id": project_id,
                "plan_ver": params.planVer,
                "demand_id": params.demandID,
            },
        )

    # === 필터 API ===

    async def get_filter_customers(
        self, project_id: str, plan_ver: str
    ) -> dict[str, Any]:
        """고객 필터 목록 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_filter_customers",
            parameters={"project_id": project_id, "plan_ver": plan_ver},
        )

    async def get_filter_item_groups(
        self, project_id: str, plan_ver: str
    ) -> dict[str, Any]:
        """품목 그룹 필터 목록 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_filter_item_groups",
            parameters={"project_id": project_id, "plan_ver": plan_ver},
        )

    async def get_filter_regions(
        self, project_id: str, plan_ver: str
    ) -> dict[str, Any]:
        """지역 필터 목록 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_filter_regions",
            parameters={"project_id": project_id, "plan_ver": plan_ver},
        )

    async def get_filter_demand_types(
        self, project_id: str, plan_ver: str
    ) -> dict[str, Any]:
        """수요 유형 필터 목록 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_filter_demand_types",
            parameters={"project_id": project_id, "plan_ver": plan_ver},
        )

    async def get_filter_prop_columns(
        self, project_id: str, plan_ver: str
    ) -> dict[str, Any]:
        """동적 속성 컬럼 정의 조회"""
        return await self._execute(
            project_id=project_id,
            query_id="rtf_filter_prop_columns",
            parameters={"project_id": project_id, "plan_ver": plan_ver},
        )


def get_rtf_report_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> RtfReportService:
    """FastAPI 의존성 주입용 서비스 생성"""
    return RtfReportService(adapter)
