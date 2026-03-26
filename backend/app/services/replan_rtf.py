"""
재수립 RTF 서비스

ReplanRtfProcessor를 통해 RPT_SHIPMENT_PLAN + OPE_EXEC_ACTUAL 데이터를 병합하여
재수립 RTF 현황을 계산합니다.
"""

from __future__ import annotations

import json
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.repositories.plan_dashboard import PlanDashboardRepository
from app.services.replan_rtf_processor import ReplanRtfProcessor, TypeQtyProcessor
from fastapi import Depends


class ReplanRtfService:
    """재수립 RTF 비즈니스 로직"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.repo = PlanDashboardRepository

    def _parse_widget_settings(self, project_id: str, user_id: str) -> dict:
        """위젯 설정에서 RTF 설정 파싱"""
        try:
            settings = self.repo.get_all_widget_settings(
                project_id, user_id, "/pa/PlanDashboard"
            )
            settings_map = {s["widget_id"]: s["widget_value"] for s in settings}
            raw = settings_map.get("rtfSummaryPopup", "")
            if raw:
                return json.loads(raw)
        except Exception:
            pass
        return {}

    def _build_processor(self, project_id: str, params) -> ReplanRtfProcessor:
        """Processor 생성 — 위젯 설정 로드 + TypeQtyProcessor 초기화"""
        widget = self._parse_widget_settings(project_id, params.userId)
        setting_list = widget.get("setting", TypeQtyProcessor.DEFAULT_SETTINGS)
        rtf_std = widget.get("rtfStd", "LOT")
        uom_type = params.uomType or widget.get("uomType", "DEFAULT")

        type_proc = TypeQtyProcessor(setting_list)
        return ReplanRtfProcessor(
            adapter=self.adapter,
            type_proc=type_proc,
            is_lot_type=(rtf_std == "LOT"),
            is_default_uom=(uom_type == "DEFAULT"),
        )

    async def get_summary(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """재수립 RTF 요약"""
        processor = self._build_processor(project_id, params)
        result = await processor.get_summary(project_id, params)
        return {"success": True, "count": len(result), "data": result}

    async def get_detail(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """재수립 RTF 상세"""
        processor = self._build_processor(project_id, params)
        result = await processor.get_detail(project_id, params)
        return {"success": True, "count": len(result), "data": result}

    async def get_prod_detail(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """생산계획 피벗 {detail, period}"""
        processor = self._build_processor(project_id, params)
        result = await processor.get_prod_detail(project_id, params)
        return {"success": True, "data": result}

    async def get_prod_types(
        self, project_id: str, plan_ver: str
    ) -> dict[str, Any]:
        """생산유형 필터 목록"""
        processor = ReplanRtfProcessor(
            adapter=self.adapter,
            type_proc=TypeQtyProcessor(),
        )
        result = await processor.get_prod_types(project_id, plan_ver)
        return {"success": True, "count": len(result), "data": result}


def get_replan_rtf_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> ReplanRtfService:
    """FastAPI 의존성 주입"""
    return ReplanRtfService(adapter)
