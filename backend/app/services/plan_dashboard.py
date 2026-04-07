"""
Plan Dashboard 서비스

QueryExecutorAdapter (Trino) + PlanDashboardRepository (PostgreSQL) 조합
RTFSummaryCreator: 원본 C# RTFSummaryCreator 포팅
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.repositories.plan_dashboard import PlanDashboardRepository
from app.services import plan_dashboard_queries as Q
from fastapi import Depends

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RTFSummaryCreator — 원본 C# RTFSummaryCreator 포팅
# ---------------------------------------------------------------------------


class RTFSummaryCreator:
    """RTF Summary 계산 — 원본 C# RTFSummaryCreator 포팅"""

    DEFAULT_SETTINGS = [
        {"category": "within_plan", "plan_type": "early", "apply_early": True, "apply_on_time": False, "apply_late": False, "apply_short": False, "apply_excluded": False},
        {"category": "within_plan", "plan_type": "on_time", "apply_early": False, "apply_on_time": True, "apply_late": False, "apply_short": False, "apply_excluded": False},
        {"category": "within_plan", "plan_type": "late", "apply_early": False, "apply_on_time": False, "apply_late": True, "apply_short": False, "apply_excluded": False},
        {"category": "within_plan", "plan_type": "remain", "apply_early": False, "apply_on_time": False, "apply_late": False, "apply_short": True, "apply_excluded": False},
        {"category": "within_plan", "plan_type": "short", "apply_early": False, "apply_on_time": False, "apply_late": False, "apply_short": True, "apply_excluded": False},
        {"category": "after_plan", "plan_type": "early", "apply_early": True, "apply_on_time": False, "apply_late": False, "apply_short": False, "apply_excluded": False},
        {"category": "after_plan", "plan_type": "on_time", "apply_early": False, "apply_on_time": True, "apply_late": False, "apply_short": False, "apply_excluded": False},
        {"category": "after_plan", "plan_type": "late", "apply_early": False, "apply_on_time": False, "apply_late": False, "apply_short": False, "apply_excluded": True},
        {"category": "after_plan", "plan_type": "remain", "apply_early": False, "apply_on_time": False, "apply_late": False, "apply_short": False, "apply_excluded": True},
        {"category": "after_plan", "plan_type": "short", "apply_early": False, "apply_on_time": False, "apply_late": False, "apply_short": False, "apply_excluded": True},
    ]

    def __init__(
        self,
        index_data: list[dict],
        settings: dict | None = None,
        is_frozen: bool = False,
    ):
        """
        index_data: RTF_INDEX_DATA_SQL 결과 (list of {index_name, plan_value, ...})
        settings: RTFSummaryPopupJson widget settings (parsed JSON)
        is_frozen: frozen version 여부
        """
        self._dict: dict[str, dict] = {
            row["index_name"]: row for row in index_data
        }
        self._is_frozen = is_frozen

        # Parse settings
        if settings:
            self._rtf_std = settings.get("rtfStd", "LOT")
            self._uom_type = settings.get("uomType", "CONVERSION")
            self._setting_list = settings.get("setting", self.DEFAULT_SETTINGS)
        else:
            self._rtf_std = "LOT"
            self._uom_type = "CONVERSION"
            self._setting_list = self.DEFAULT_SETTINGS

        self._is_lot = self._rtf_std == "LOT"
        self._is_default_uom = self._uom_type == "DEFAULT"

    def get_index_name(self, category: str, plan_type: str) -> str:
        """동적 index name 생성"""
        lot_str = "LOT" if self._is_lot else "DEMAND"
        period_str = "PP" if category == "within_plan" else "BP"
        type_map = {
            "early": "EARLY",
            "on_time": "ONTIME",
            "late": "LATE",
            "short": "SHORT",
            "remain": "REMAIN",
        }
        type_str = type_map.get(plan_type, plan_type.upper())
        return f"TOTAL_{lot_str}_{period_str}_{type_str}_QTY"

    def get_applicable_list(self, target_type: str) -> list[dict]:
        """특정 RTF 타입에 해당하는 설정 목록 반환"""
        flag_key = f"apply_{target_type}"
        return [s for s in self._setting_list if s.get(flag_key, False)]

    def get_type_qty(self, target_type: str) -> float:
        """특정 RTF 타입의 합산 수량"""
        applicable = self.get_applicable_list(target_type)
        total = 0.0
        for setting in applicable:
            idx_name = self.get_index_name(
                setting["category"], setting["plan_type"]
            )
            row = self._dict.get(idx_name)
            if row:
                if self._is_default_uom:
                    total += float(row.get("plan_value") or 0)
                else:
                    total += float(row.get("conv_qty") or 0)
        return total

    def compute_summary(self) -> dict:
        """RTF Summary 계산 — 원본 GetRTFSummary 로직"""
        if not self._dict:
            return self._empty_summary()

        early_qty = self.get_type_qty("early")
        ontime_qty = self.get_type_qty("on_time")
        late_qty = self.get_type_qty("late")
        short_qty = self.get_type_qty("short")

        total_qty = early_qty + ontime_qty + late_qty + short_qty
        rtf_qty = early_qty + ontime_qty + late_qty

        if total_qty > 0:
            rtf_ratio = round(rtf_qty / total_qty * 1000) / 10
            early_ratio = round(early_qty / total_qty * 1000) / 10
            ontime_ratio = round(ontime_qty / total_qty * 1000) / 10
            late_ratio = rtf_ratio - ontime_ratio - early_ratio  # derived
            short_ratio = 100 - rtf_ratio
        else:
            rtf_ratio = early_ratio = ontime_ratio = late_ratio = short_ratio = 0.0

        # Get UOM from first available index row
        uom = ""
        for row in self._dict.values():
            if self._is_default_uom:
                uom = row.get("qty_uom", "")
            else:
                uom = row.get("conv_qty_uom", "")
            if uom:
                break

        return {
            "demandQty": total_qty,
            "earlyQty": early_qty,
            "earlyRatio": early_ratio,
            "ontimeQty": ontime_qty,
            "ontimeRatio": ontime_ratio,
            "lateQty": late_qty,
            "lateRatio": late_ratio,
            "shortQty": short_qty,
            "shortRatio": short_ratio,
            "rtfQty": rtf_qty,
            "rtfRatio": rtf_ratio,
            "upcomingQty": 0,
            "upcomingRatio": 0,
            "qtyUom": uom,
            "uomType": self._uom_type,
        }

    @staticmethod
    def _empty_summary() -> dict:
        return {
            "demandQty": 0,
            "earlyQty": 0,
            "earlyRatio": 0,
            "ontimeQty": 0,
            "ontimeRatio": 0,
            "lateQty": 0,
            "lateRatio": 0,
            "shortQty": 0,
            "shortRatio": 0,
            "rtfQty": 0,
            "rtfRatio": 0,
            "upcomingQty": 0,
            "upcomingRatio": 0,
            "qtyUom": "",
            "uomType": "DEFAULT",
        }


# ---------------------------------------------------------------------------
# PlanDashboardService
# ---------------------------------------------------------------------------


class PlanDashboardService:
    """Plan Dashboard 비즈니스 로직"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.repo = PlanDashboardRepository
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS

    async def _trino(self, project_id: str, sql: str) -> dict[str, Any]:
        """Trino 쿼리 실행 공통 메서드"""
        result = await self.adapter.execute_direct_query(
            project_id=project_id,
            query=sql,
            catalog=self.catalog,
            schema=self.schema,
        )
        if not result.get("success"):
            raise ValueError(result.get("message", "Trino 쿼리 실행 실패"))
        return result

    async def _trino_safe(self, project_id: str, sql: str) -> list[dict]:
        """Trino 쿼리 실행 — 실패 시 빈 리스트 반환"""
        try:
            result = await self._trino(project_id, sql)
            return result.get("row", [])
        except Exception as e:
            logger.warning("Trino query failed (graceful fallback): %s", e)
            return []

    # =======================================================================
    # RTF Summary 파이프라인
    # =======================================================================

    def _parse_rtf_settings(self, settings_map: dict) -> dict | None:
        """위젯 설정에서 RTF 설정 파싱"""
        raw = settings_map.get("rtfReportPopup", "") or settings_map.get(
            "RTFSummaryPopupJson", ""
        )
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    def _build_category_filter(
        self, rtf_settings: dict | None, category_name: str = ""
    ) -> str:
        """RTF 설정에서 category_name 필터 생성"""
        if category_name:
            return f"AND category_name = '{category_name}'"
        return ""

    async def _get_rtf_index_data(
        self,
        project_id: str,
        partition_key: str,
        plan_ver: str,
        category_filter: str = "",
    ) -> list[dict]:
        """RTF index 데이터 조회 — TOTAL% LIKE"""
        sql = Q.RTF_INDEX_DATA_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            category_filter=category_filter,
        )
        return await self._trino_safe(project_id, sql)

    async def _get_rtf_summary_on_frozen(
        self,
        project_id: str,
        plan_ver: str,
        frozen_ver: str,
        rtf_settings: dict | None,
        category_name: str = "",
    ) -> dict:
        """Frozen 버전 기준 RTF Summary"""
        frozen_partition_key = f"{project_id}@{frozen_ver[:6]}"
        category_filter = self._build_category_filter(rtf_settings, category_name)
        index_data = await self._get_rtf_index_data(
            project_id, frozen_partition_key, frozen_ver, category_filter
        )
        creator = RTFSummaryCreator(
            index_data, settings=rtf_settings, is_frozen=True
        )
        return creator.compute_summary()

    async def _get_rtf_summary_on_frozen_and_plan(
        self,
        project_id: str,
        plan_ver: str,
        frozen_ver: str,
        rtf_settings: dict | None,
        category_name: str = "",
    ) -> dict:
        """현재 planVer 기준 RTF Summary (Plan)"""
        partition_key = f"{project_id}@{plan_ver[:6]}"
        category_filter = self._build_category_filter(rtf_settings, category_name)
        index_data = await self._get_rtf_index_data(
            project_id, partition_key, plan_ver, category_filter
        )
        creator = RTFSummaryCreator(
            index_data, settings=rtf_settings, is_frozen=False
        )
        return creator.compute_summary()

    async def _get_rtf_summary_on_frozen_and_act(
        self,
        project_id: str,
        plan_ver: str,
        frozen_ver: str,
        rtf_settings: dict | None,
        category_name: str = "",
    ) -> dict:
        """
        실적(Actual) 기반 RTF Summary.
        ope_exec_actual / rpt_shipment_plan 이 없을 수 있으므로
        실패 시 plan 기준 summary로 fallback.
        """
        try:
            partition_key = f"{project_id}@{plan_ver[:6]}"
            category_filter = self._build_category_filter(rtf_settings, category_name)
            index_data = await self._get_rtf_index_data(
                project_id, partition_key, plan_ver, category_filter
            )
            creator = RTFSummaryCreator(
                index_data, settings=rtf_settings, is_frozen=False
            )
            return creator.compute_summary()
        except Exception:
            logger.warning(
                "Actual RTF summary failed, falling back to plan-based summary"
            )
            return await self._get_rtf_summary_on_frozen_and_plan(
                project_id, plan_ver, frozen_ver, rtf_settings, category_name
            )

    # =======================================================================
    # 메인 대시보드
    # =======================================================================

    async def get_dashboard(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """
        메인 대시보드 전체 데이터 조회
        1. Frozen 버전 조회 (PostgreSQL)
        2. 위젯 설정 조회 (PostgreSQL)
        3. RTF Summary (RTFSummaryCreator) + 기타 패널 Trino 쿼리 병렬 실행
        4. 에러 마스터 (PostgreSQL) + 에러 로그 (Trino) 조합
        """
        partition_key = f"{project_id}@{params.planVer[:6]}"

        # 1. Frozen version (실패 시 원본 planVer 사용)
        try:
            frozen_ver = self.repo.get_frozen_ver(project_id, params.planVer)
        except Exception:
            frozen_ver = params.planVer

        # 2. Widget settings (실패 시 빈 설정)
        try:
            widget_settings = self.repo.get_all_widget_settings(
                project_id, params.userId, params.menuId
            )
            settings_map = {
                s["widget_id"]: s["widget_value"] for s in widget_settings
            }
        except Exception:
            settings_map = {}

        # 3. Parse RTF settings
        rtf_settings = self._parse_rtf_settings(settings_map)

        # 3-1. RTF category_name: region이 "RTF"(전체)가 아닌 경우 필터 적용
        rtf_category_name = params.region if params.region != "RTF" else ""

        # 4. Build SQL for non-RTF panels
        # Oper Group Capa
        oper_group_filter = self._build_oper_group_filter(settings_map)
        oper_group_sql = Q.OPER_GROUP_CAPA_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            oper_group_filter=oper_group_filter,
        )

        # Res Group
        res_group_filter = self._build_res_group_filter(settings_map)
        week_period = self._get_week_period(settings_map)
        if week_period > 0:
            res_group_sql = Q.RES_GROUP_DETAIL_BY_PERIOD_SQL.format(
                partition_key=partition_key,
                plan_ver=params.planVer,
                res_group_filter=res_group_filter,
                week_period=week_period,
            )
        else:
            res_group_sql = Q.RES_GROUP_DETAIL_SQL.format(
                partition_key=partition_key,
                plan_ver=params.planVer,
                res_group_filter=res_group_filter,
            )

        # Prod Report
        prod_sql = Q.PROD_REPORT_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            aggregate_type=params.aggregateType,
        )
        prod_qty_sql = Q.PROD_QTY_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            aggregate_type=params.aggregateType,
        )

        # STD Summary
        std_sql = Q.STD_DETAIL_SQL.format(
            partition_key=partition_key, plan_ver=params.planVer
        )

        # Error Log (Trino)
        error_sql = Q.ERROR_LOG_SUMMARY_SQL.format(
            partition_key=partition_key, plan_ver=params.planVer
        )

        # Short Log
        short_sql = Q.SHORT_LOG_SUMMARY_SQL.format(
            partition_key=partition_key, plan_ver=params.planVer
        )

        # Peg Report
        peg_sql = Q.PEG_REPORT_SUMMARY_SQL.format(
            partition_key=partition_key, plan_ver=params.planVer
        )
        unpeg_sql = Q.UNPEG_REASONS_SQL.format(
            partition_key=partition_key, plan_ver=params.planVer
        )

        # 5. Execute all in parallel — RTF summaries + non-RTF panels + OTD
        results = await asyncio.gather(
            # RTF summaries (indices 0-2)
            self._get_rtf_summary_on_frozen(
                project_id, params.planVer, frozen_ver, rtf_settings, rtf_category_name
            ),
            self._get_rtf_summary_on_frozen_and_act(
                project_id, params.planVer, frozen_ver, rtf_settings, rtf_category_name
            ),
            self._get_rtf_summary_on_frozen_and_plan(
                project_id, params.planVer, frozen_ver, rtf_settings, rtf_category_name
            ),
            # Non-RTF panels (indices 3-11)
            self._trino(project_id, oper_group_sql),
            self._trino(project_id, res_group_sql),
            self._trino(project_id, prod_sql),
            self._trino(project_id, prod_qty_sql),
            self._trino(project_id, std_sql),
            self._trino(project_id, error_sql),
            self._trino(project_id, short_sql),
            self._trino(project_id, peg_sql),
            self._trino(project_id, unpeg_sql),
            # OTD summary (index 12)
            self._get_otd_summary(
                project_id, params.planVer, frozen_ver, params.productionArea
            ),
            return_exceptions=True,
        )

        # RTF summaries — already dicts (or Exception)
        rtf_frozen = results[0] if not isinstance(results[0], Exception) else RTFSummaryCreator._empty_summary()
        rtf_actual = results[1] if not isinstance(results[1], Exception) else RTFSummaryCreator._empty_summary()
        rtf_plan = results[2] if not isinstance(results[2], Exception) else RTFSummaryCreator._empty_summary()

        # OTD summary
        otd_data = results[12] if not isinstance(results[12], Exception) else {
            "qtyUom": "", "uomType": "CONVERSION", "periodType": "Month",
            "frozenVer": frozen_ver, "frozenQty": 0, "planQty": 0, "actQty": 0, "list": [],
        }

        # 6. Error master from PostgreSQL (글로벌 마스터, project_id 불필요)
        try:
            error_master = self.repo.get_error_log_master()
        except Exception:
            error_master = []

        # Assemble response
        return {
            "success": True,
            "data": {
                "frozenVer": frozen_ver,
                "rtfSummary": {
                    "frozen": rtf_frozen,
                    "actual": rtf_actual,
                    "plan": rtf_plan,
                },
                "operGroupCapa": self._safe_rows(results[3]),
                "resGroupReport": self._safe_rows(results[4]),
                "prodReport": {
                    "detail": self._safe_rows(results[5]),
                    "summary": self._safe_rows(results[6]),
                },
                "otdSummary": otd_data,
                "stdSummaryReport": self._safe_rows(results[7]),
                "errorLogSummary": self._merge_error_log(
                    error_master, self._safe_rows(results[8])
                ),
                "shortLogSummary": self._safe_rows(results[9]),
                "peggingReport": {
                    "summary": self._safe_rows(results[10]),
                    "reasons": self._safe_rows(results[11]),
                },
            },
        }

    # =======================================================================
    # 개별 패널 API
    # =======================================================================

    async def get_rtf_detail(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """RTF 세부 통계 (차트 드릴다운)"""
        frozen_ver = self.repo.get_frozen_ver(project_id, params.planVer)
        frozen_partition_key = f"{project_id}@{frozen_ver[:6]}"

        # 위젯 설정 조회
        try:
            widget_settings = self.repo.get_all_widget_settings(
                project_id,
                getattr(params, "userId", ""),
                getattr(params, "menuId", "/pa/PlanDashboard2"),
            )
            settings_map = {
                s["widget_id"]: s["widget_value"] for s in widget_settings
            }
        except Exception:
            settings_map = {}

        rtf_settings = self._parse_rtf_settings(settings_map)
        category_filter = self._build_category_filter(rtf_settings)

        index_data = await self._get_rtf_index_data(
            project_id, frozen_partition_key, frozen_ver, category_filter
        )
        creator = RTFSummaryCreator(
            index_data, settings=rtf_settings, is_frozen=True
        )
        summary = creator.compute_summary()
        return {"success": True, "data": summary}

    async def get_res_group_report(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """설비 가동 현황 단독 리프레시"""
        partition_key = f"{project_id}@{params.planVer[:6]}"
        res_group_filter = ""
        if params.resGroupIDs:
            ids = ", ".join(f"'{rid}'" for rid in params.resGroupIDs)
            res_group_filter = f"AND INDEX_NAME IN ({ids})"

        if params.weekPeriod > 0:
            sql = Q.RES_GROUP_DETAIL_BY_PERIOD_SQL.format(
                partition_key=partition_key,
                plan_ver=params.planVer,
                res_group_filter=res_group_filter,
                week_period=params.weekPeriod,
            )
        else:
            sql = Q.RES_GROUP_DETAIL_SQL.format(
                partition_key=partition_key,
                plan_ver=params.planVer,
                res_group_filter=res_group_filter,
            )
        result = await self._trino(project_id, sql)
        return {
            "success": True,
            "count": result["rowcount"],
            "data": result["row"],
        }

    async def get_prod_report(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """생산 현황 리프레시"""
        partition_key = f"{project_id}@{params.planVer[:6]}"
        sql = Q.PROD_REPORT_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            aggregate_type=params.aggregateType,
        )
        qty_sql = Q.PROD_QTY_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            aggregate_type=params.aggregateType,
        )
        detail_result, qty_result = await asyncio.gather(
            self._trino(project_id, sql),
            self._trino(project_id, qty_sql),
        )
        return {
            "success": True,
            "data": {
                "detail": detail_result.get("row", []),
                "summary": qty_result.get("row", []),
            },
        }

    # =======================================================================
    # OTD Summary (Sub4/Sub6 — rpt_buffer_plan 기반)
    # =======================================================================

    def _get_cycle_dates(self, project_id: str, plan_ver: str) -> dict:
        """Plan cycle 날짜 정보 조회 — OTD bucket 분류에 필요"""
        try:
            dates = self.repo.get_plan_cycle_dates(project_id, plan_ver)
            return dates
        except Exception:
            # 기본값: planVer에서 날짜 추출
            date_str = plan_ver[:8]  # "20260401"
            return {
                "cycle_start": f"{date_str[:4]}-{date_str[4:6]}-01",
                "cycle_end": f"{date_str[:4]}-{int(date_str[4:6])+1:02d}-01" if int(date_str[4:6]) < 12 else f"{int(date_str[:4])+1}-01-01",
                "next_cycle_end": f"{date_str[:4]}-{int(date_str[4:6])+2:02d}-01" if int(date_str[4:6]) < 11 else f"{int(date_str[:4])+1}-{int(date_str[4:6])+2-12:02d}-01",
            }

    def _build_production_area_filter(self, production_area: str) -> str:
        """생산 영역 필터 SQL 조건절 생성"""
        if production_area:
            return f"AND production_area = '{production_area}'"
        return ""

    async def _get_otd_summary(
        self,
        project_id: str,
        plan_ver: str,
        frozen_ver: str,
        production_area: str = "",
        data_type: str = "ITEMGROUP",
    ) -> dict[str, Any]:
        """
        OTD Summary — frozen/plan/actual 모두 조회
        C# GetOTDSummaryRowsWithFrozenAndAct + GetOTDSummaryRowsWithFrozenAndPlan 통합
        """
        partition_key = f"{project_id}@{plan_ver[:6]}"
        frozen_partition_key = f"{project_id}@{frozen_ver[:6]}"
        # production_area 필터는 rpt_buffer_plan 테이블 스키마에 맞게 조정 필요
        # 일단 필터 없이 조회하여 데이터 존재 여부 확인
        production_area_filter = ""
        cycle_dates = self._get_cycle_dates(project_id, plan_ver)

        common_params = {
            "production_area_filter": production_area_filter,
            "cycle_start": cycle_dates["cycle_start"],
            "cycle_end": cycle_dates["cycle_end"],
            "next_cycle_end": cycle_dates["next_cycle_end"],
        }

        # Frozen 데이터 (frozen_ver 기준)
        frozen_sql = Q.OTD_BUFFER_PLAN_SUMMARY_SQL.format(
            partition_key=frozen_partition_key,
            plan_ver=frozen_ver,
            **common_params,
        )
        # Plan 데이터 (현재 planVer 기준)
        plan_sql = Q.OTD_BUFFER_PLAN_SUMMARY_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            **common_params,
        )
        # Actual 데이터
        actual_sql = Q.OTD_ACTUAL_SUMMARY_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            **common_params,
        )

        frozen_result, plan_result, actual_result = await asyncio.gather(
            self._trino_safe(project_id, frozen_sql),
            self._trino_safe(project_id, plan_sql),
            self._trino_safe(project_id, actual_sql),
        )

        # UOM 추출
        qty_uom = ""
        for row in frozen_result:
            if row.get("qty_uom"):
                qty_uom = row["qty_uom"]
                break

        # 합산
        frozen_qty = round(sum(r.get("total_qty", 0) or 0 for r in frozen_result), 1)
        plan_qty = round(sum(r.get("total_qty", 0) or 0 for r in plan_result), 1)
        act_qty = round(sum(r.get("total_qty", 0) or 0 for r in actual_result), 1)

        # list 조합: type 필드 추가
        result_list = []
        for row in frozen_result:
            result_list.append({**row, "type": "FROZEN"})
        for row in plan_result:
            result_list.append({**row, "type": "PLAN"})
        for row in actual_result:
            result_list.append({**row, "type": "ACT"})

        return {
            "qtyUom": qty_uom,
            "uomType": "CONVERSION",
            "periodType": "Month",
            "frozenVer": frozen_ver,
            "frozenQty": frozen_qty,
            "planQty": plan_qty,
            "actQty": act_qty,
            "list": result_list,
        }

    # =======================================================================
    # 설정 API
    # =======================================================================

    def get_settings(
        self,
        project_id: str,
        user_id: str,
        menu_id: str,
        plan_ver: str = "",
    ) -> dict[str, Any]:
        """전체 위젯 설정 조회"""
        widget_settings = self.repo.get_all_widget_settings(
            project_id, user_id, menu_id
        )
        settings_map = {
            s["widget_id"]: s["widget_value"] for s in widget_settings
        }
        return {"success": True, "data": settings_map}

    def save_setting(self, project_id: str, params) -> dict[str, Any]:
        """위젯 설정 저장"""
        rowcount = self.repo.save_widget_setting(
            project_id=project_id,
            user_id=params.userId,
            menu_id=params.menuId,
            widget_id=params.widgetId,
            widget_value=params.widgetValue,
        )
        return {"success": True, "rowcount": rowcount}

    # =======================================================================
    # 헬퍼
    # =======================================================================

    @staticmethod
    def _safe_rows(result) -> list:
        """asyncio.gather 결과에서 안전하게 row 추출"""
        if isinstance(result, Exception):
            return []
        return result.get("row", [])

    @staticmethod
    def _merge_error_log(master: list[dict], trino_rows: list) -> list:
        """에러 마스터(PG)와 에러 로그 카운트(Trino) 병합"""
        count_map = {
            r.get("severity", ""): r.get("cnt", 0) for r in trino_rows
        }
        return [
            {
                "severity": m["severity"],
                "cnt": count_map.get(m["severity"], 0),
            }
            for m in master
        ]

    @staticmethod
    def _build_oper_group_filter(settings_map: dict) -> str:
        """위젯 설정에서 operGroupIDs 필터 빌드"""
        raw = settings_map.get("OperGroupUtilization", "")
        if not raw:
            return ""
        try:
            data = json.loads(raw)
            ids = data.get("operGroupIDs", [])
            if ids:
                in_clause = ", ".join(f"'{oid}'" for oid in ids)
                return f"AND INDEX_NAME IN ({in_clause})"
        except (json.JSONDecodeError, AttributeError):
            pass
        return ""

    @staticmethod
    def _build_res_group_filter(settings_map: dict) -> str:
        """위젯 설정에서 resGroupIDs 필터 빌드"""
        raw = settings_map.get("ResGroupPopup", "")
        if not raw:
            return ""
        try:
            data = json.loads(raw)
            ids = data.get("resGroupIDs", [])
            if ids:
                in_clause = ", ".join(f"'{rid}'" for rid in ids)
                return f"AND INDEX_NAME IN ({in_clause})"
        except (json.JSONDecodeError, AttributeError):
            pass
        return ""

    @staticmethod
    def _get_week_period(settings_map: dict) -> int:
        """위젯 설정에서 weekPeriod 추출"""
        raw = settings_map.get("ResGroupPopup", "")
        if not raw:
            return 0
        try:
            data = json.loads(raw)
            return int(data.get("week_period", 0))
        except (json.JSONDecodeError, AttributeError, ValueError):
            return 0


def get_plan_dashboard_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> PlanDashboardService:
    """FastAPI 의존성 주입용 서비스 생성"""
    return PlanDashboardService(adapter)
