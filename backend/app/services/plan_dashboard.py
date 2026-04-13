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
        production_area: str = "",
    ) -> dict:
        """
        현재 planVer 기준 RTF Summary (Plan).
        C# 원본: GetRTFSummary(!isFrozenVer 분기)
        1. 먼저 실적(actual) 기반 short/upcoming 계산
        2. plan index에서 early/ontime/late 가져옴
        3. shortQty = (actShort + actUpcoming) - (planOntime + planLate)
        """
        # Step 1: 실적 기반 summary (short/upcoming)
        act_summary = await self._get_rtf_summary_on_frozen_and_act(
            project_id, plan_ver, frozen_ver, rtf_settings, category_name,
            production_area=production_area,
        )
        act_short = act_summary.get("shortQty", 0)
        act_upcoming = act_summary.get("upcomingQty", 0)

        # Step 2: plan index에서 early/ontime/late
        partition_key = f"{project_id}@{plan_ver[:6]}"
        category_filter = self._build_category_filter(rtf_settings, category_name)
        index_data = await self._get_rtf_index_data(
            project_id, partition_key, plan_ver, category_filter
        )
        creator = RTFSummaryCreator(
            index_data, settings=rtf_settings, is_frozen=False
        )
        plan = creator.compute_summary()

        plan_early = plan.get("earlyQty", 0)
        plan_ontime = plan.get("ontimeQty", 0)
        plan_late = plan.get("lateQty", 0)

        # Step 3: C# 로직 — short = (actShort + actUpcoming) - (planOntime + planLate)
        adjusted_short = (act_short + act_upcoming) - (plan_ontime + plan_late)
        if adjusted_short < 0:
            adjusted_short = 0

        total = plan_early + plan_ontime + plan_late + adjusted_short
        rtf_qty = plan_early + plan_ontime + plan_late

        if total > 0:
            rtf_ratio = round(rtf_qty / total * 1000) / 10
            early_ratio = round(plan_early / total * 1000) / 10
            ontime_ratio = round(plan_ontime / total * 1000) / 10
            late_ratio = rtf_ratio - ontime_ratio - early_ratio
            short_ratio = 100 - rtf_ratio
        else:
            rtf_ratio = early_ratio = ontime_ratio = late_ratio = short_ratio = 0.0

        return {
            "demandQty": round(total, 2),
            "earlyQty": round(plan_early, 2),
            "earlyRatio": early_ratio,
            "ontimeQty": round(plan_ontime, 2),
            "ontimeRatio": ontime_ratio,
            "lateQty": round(plan_late, 2),
            "lateRatio": late_ratio,
            "shortQty": round(adjusted_short, 2),
            "shortRatio": short_ratio,
            "rtfQty": round(rtf_qty, 2),
            "rtfRatio": rtf_ratio,
            "upcomingQty": round(act_upcoming, 2),
            "upcomingRatio": round(act_upcoming / (total + act_upcoming) * 1000) / 10 if (total + act_upcoming) > 0 else 0,
            "qtyUom": plan.get("qtyUom", ""),
            "uomType": plan.get("uomType", "CONVERSION"),
        }

    async def _get_rtf_summary_on_frozen_and_act(
        self,
        project_id: str,
        plan_ver: str,
        frozen_ver: str,
        rtf_settings: dict | None,
        category_name: str = "",
        production_area: str = "",
    ) -> dict:
        """
        실적(Actual) 기반 RTF Summary.
        C# GetRTFSummaryFromAct 포팅:
        1. ope_exec_actual에서 실적 데이터 조회
        2. rpt_shipment_plan에서 demand 데이터 조회
        3. 실적 기반 early/ontime/late/short 집계
        """
        import json as _json
        from datetime import datetime, timedelta

        try:
            partition_key = f"{project_id}@{plan_ver[:6]}"

            # 계획 시작/종료일 조회
            cycle_dates = self._get_cycle_dates(project_id, plan_ver)
            cycle_start = cycle_dates.get("cycle_start", "")
            cycle_end = cycle_dates.get("cycle_end", "")
            plan_start = cycle_start  # plan_start_datetime

            # Final item buffer IDs 조회
            buffer_sql = Q.FINAL_ITEM_BUFFER_SQL.format(
                partition_key=partition_key, plan_ver=plan_ver
            )
            buffer_result = await self._trino_safe(project_id, buffer_sql)
            buffer_ids = [r.get("buffer_id", "") for r in buffer_result if r.get("buffer_id")]

            if not buffer_ids:
                return RTFSummaryCreator._empty_summary()

            buffer_ids_str = ", ".join(f"'{b}'" for b in buffer_ids)

            # 실적 데이터 조회 (ope_exec_actual)
            # actEndDate: 과거 사이클이면 cycle_end, 아니면 plan_start - 1day
            act_end = plan_start  # 간략화: plan_start를 기준으로 실적 범위
            act_sql = Q.OTD_EXEC_ACTUAL_SQL.format(
                project_id=project_id,
                buffer_ids=buffer_ids_str,
                start_date=cycle_start,
                end_date=act_end,
                production_area_filter="",
            )
            act_rows = await self._trino_safe(project_id, act_sql)

            # 실적 집계: demand별 rtf_qty / status
            summary = {
                "earlyQty": 0.0, "ontimeQty": 0.0, "lateQty": 0.0,
                "shortQty": 0.0, "demandQty": 0.0, "upcomingQty": 0.0,
            }
            rtf_demand_dict: dict[str, float] = {}
            qty_uoms: set[str] = set()

            try:
                cycle_start_dt = datetime.strptime(cycle_start[:10], "%Y-%m-%d")
                cycle_end_dt = datetime.strptime(cycle_end[:10], "%Y-%m-%d")
            except (ValueError, TypeError):
                cycle_start_dt = cycle_end_dt = datetime.now()

            # plan_start_datetime 조회 (C# SetPlanStartEndDate)
            plan_start_dt = cycle_start_dt
            try:
                ps_sql = f"SELECT plan_start_datetime FROM postgresql.mzc_aps.cfg_plan_config WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1"
                ps_rows = await self._trino_safe(project_id, ps_sql)
                if ps_rows:
                    ps_val = str(ps_rows[0].get("plan_start_datetime", ""))[:10]
                    plan_start_dt = datetime.strptime(ps_val, "%Y-%m-%d")
            except Exception:
                pass

            # Phase 1: 실적 행 처리
            for row in act_rows:
                oper_id = row.get("oper_id") or ""
                if oper_id:
                    continue  # oper_id가 비어있는 행만 처리

                detail_json = row.get("detail_json")
                if not detail_json:
                    continue
                try:
                    detail = _json.loads(detail_json) if isinstance(detail_json, str) else detail_json
                except Exception:
                    continue

                demand_id = detail.get("demand_id", "")
                due_date_str = detail.get("due_date", "")
                plan_date_str = (row.get("plan_date") or "")[:10]

                try:
                    due_dt = datetime.strptime(due_date_str[:10], "%Y-%m-%d")
                    plan_dt = datetime.strptime(plan_date_str[:10], "%Y-%m-%d")
                except (ValueError, TypeError):
                    continue

                plan_qty = float(row.get("conv_qty") or row.get("plan_qty") or 0)
                qty_uom = row.get("conv_qty_uom") or row.get("qty_uom") or ""
                if qty_uom:
                    qty_uoms.add(qty_uom)

                # C# GetActStatus: planDate vs dueDate vs cycle 범위
                if plan_dt > due_dt:
                    status = "late"
                elif cycle_start_dt <= due_dt < cycle_end_dt:
                    status = "on_time"
                elif due_dt >= cycle_end_dt:
                    status = "early"
                else:
                    status = ""

                if status == "early":
                    summary["earlyQty"] += plan_qty
                elif status == "on_time":
                    summary["ontimeQty"] += plan_qty
                elif status == "late":
                    summary["lateQty"] += plan_qty

                rtf_demand_dict[demand_id] = rtf_demand_dict.get(demand_id, 0) + plan_qty

            # Phase 2: Demand 조회 (rpt_shipment_plan) - C# GetDemands
            # C# 원본: uomType=CONVERSION, toDate=cycleEndDate, regions→productionArea 필터
            # region prop_key로 DEMAND_REGION(PROP02) 필터 적용
            import json as _json2
            # Region (productionArea) 필터 구성
            region_filter = ""
            if production_area:
                try:
                    pc_sql = f"SELECT prop_json FROM odv_report_prop_config WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}' AND table_name = 'RPT_SHIPMENT_PLAN' LIMIT 1"
                    pc_rows = await self._trino_safe(project_id, pc_sql)
                    if pc_rows:
                        pc_cfg = _json2.loads(pc_rows[0].get("prop_json", "{}")) if isinstance(pc_rows[0].get("prop_json"), str) else pc_rows[0].get("prop_json", {})
                        for k, v in pc_cfg.items():
                            if isinstance(v, dict) and v.get("PropID", {}).get("Value") == "DEMAND_REGION":
                                # C# 원본: prop_json->>propID LIKE productionArea || '%'
                                region_filter = f"AND json_extract_scalar(prop_json, '$.{k}') LIKE '{production_area}%'"
                                break
                except Exception:
                    pass

            # C# 원본 RptShipmentPlan_Select_Prop_ISU_P_Cmd1.sql 완전 재현:
            # - SafetyStock 제외 안함 (원본에 없음)
            # - #Dummy만 제외
            # - toDate: strict < (due_date < cycleEnd)
            # - productionArea: prop_json LIKE
            cycle_end_ymd = cycle_end.replace("-", "")
            demand_sql = f"""
            SELECT demand_id,
                   MAX(CAST(demand_conv_qty AS DOUBLE)) AS demand_qty,
                   MAX(due_date) AS due_date
            FROM rpt_shipment_plan
            WHERE partition_key = '{partition_key}'
              AND plan_ver = '{plan_ver}'
              AND demand_type <> '#Dummy'
              AND due_date < '{cycle_end_ymd}'
              {region_filter}
            GROUP BY demand_id
            """
            demand_rows = await self._trino_safe(project_id, demand_sql)

            for row in demand_rows:
                did = row.get("demand_id", "")
                demand_qty = float(row.get("demand_qty") or 0)
                due_str = str(row.get("due_date", ""))[:10].replace("-", "")

                try:
                    due_dt = datetime.strptime(due_str[:8], "%Y%m%d") if len(due_str) >= 8 else plan_start_dt
                except ValueError:
                    due_dt = plan_start_dt

                # C#: _planStartDate > dueDate ? SHORT : UPCOMING
                category = "short" if plan_start_dt > due_dt else "upcoming"

                summary["demandQty"] += demand_qty

                if did in rtf_demand_dict:
                    # 실적이 있는 demand: short = demand_qty - rtf_qty
                    short_qty = demand_qty - rtf_demand_dict[did]
                    if short_qty > 0:
                        if category == "short":
                            summary["shortQty"] += short_qty
                        else:
                            summary["upcomingQty"] += short_qty
                else:
                    # 실적이 없는 demand: 전부 short 또는 upcoming
                    if category == "short":
                        summary["shortQty"] += demand_qty
                    else:
                        summary["upcomingQty"] += demand_qty

            # 비율 계산
            total = summary["earlyQty"] + summary["ontimeQty"] + summary["lateQty"] + summary["shortQty"]
            rtf_qty = summary["earlyQty"] + summary["ontimeQty"] + summary["lateQty"]

            if total > 0:
                rtf_ratio = round(rtf_qty / total * 1000) / 10
                early_ratio = round(summary["earlyQty"] / total * 1000) / 10
                ontime_ratio = round(summary["ontimeQty"] / total * 1000) / 10
                late_ratio = rtf_ratio - ontime_ratio - early_ratio
                short_ratio = 100 - rtf_ratio
            else:
                rtf_ratio = early_ratio = ontime_ratio = late_ratio = short_ratio = 0.0

            return {
                "demandQty": round(total, 2),
                "earlyQty": round(summary["earlyQty"], 2),
                "earlyRatio": early_ratio,
                "ontimeQty": round(summary["ontimeQty"], 2),
                "ontimeRatio": ontime_ratio,
                "lateQty": round(summary["lateQty"], 2),
                "lateRatio": late_ratio,
                "shortQty": round(summary["shortQty"], 2),
                "shortRatio": short_ratio,
                "rtfQty": round(rtf_qty, 2),
                "rtfRatio": rtf_ratio,
                "upcomingQty": round(summary["upcomingQty"], 2),
                "upcomingRatio": round(summary["upcomingQty"] / summary["demandQty"] * 1000) / 10 if summary["demandQty"] > 0 else 0,
                "qtyUom": ", ".join(qty_uoms) if qty_uoms else "",
                "uomType": "CONVERSION",
            }
        except Exception as e:
            logger.warning(f"Actual RTF summary failed: {e}, returning empty")
            return RTFSummaryCreator._empty_summary()

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
        # Oper Group Capa — C# uses rpt_oper_group_target + cfg_plan_config dates
        oper_group_filter = self._build_oper_group_filter(settings_map)
        try:
            plan_config = self.repo.get_plan_config_dates(project_id, params.planVer)
            oper_from_date = plan_config.get("from_date", "2026-04-01")
            capa_days = 30
            from datetime import datetime as _dt, timedelta as _td
            oper_to_date = (_dt.strptime(oper_from_date, "%Y-%m-%d") + _td(days=capa_days - 1)).strftime("%Y-%m-%d")
        except Exception:
            oper_from_date = params.planVer[:4] + "-" + params.planVer[4:6] + "-01"
            oper_to_date = oper_from_date  # fallback
            capa_days = 30

        # prop_json key 동적 조회 (OperGroupCapa, OperGroupQtyUOM)
        capa_prop_id = "PROP01"
        uom_prop_id = "PROP02"
        try:
            prop_cfg = self.repo.get_rpt_prop_config(project_id, params.planVer, "RPT_OPER_GROUP_TARGET")
            for k, v in prop_cfg.items():
                if not isinstance(v, dict):
                    continue
                display = v.get("PropID", {}).get("Value", "")
                if display == "OperGroupCapa":
                    capa_prop_id = k
                elif display == "OperGroupQtyUOM":
                    uom_prop_id = k
        except Exception:
            pass
        oper_group_sql = Q.OPER_GROUP_CAPA_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            oper_group_filter=oper_group_filter,
            from_date=oper_from_date,
            to_date=oper_to_date,
            plan_start=oper_from_date,
            capa_days=capa_days,
            capa_prop_id=capa_prop_id,
            uom_prop_id=uom_prop_id,
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
                project_id, params.planVer, frozen_ver, rtf_settings, rtf_category_name,
                production_area=params.productionArea
            ),
            self._get_rtf_summary_on_frozen_and_plan(
                project_id, params.planVer, frozen_ver, rtf_settings, rtf_category_name,
                production_area=params.productionArea
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
            # OTD summary: Sub4=FrozenAndAct (index 12), Sub6=FrozenAndPlan (index 13)
            self._get_otd_summary(
                project_id, params.planVer, frozen_ver, params.productionArea,
                otd_type="ACT",
            ),
            self._get_otd_summary(
                project_id, params.planVer, frozen_ver, params.productionArea,
                otd_type="PLAN",
            ),
            return_exceptions=True,
        )

        # RTF summaries — already dicts (or Exception)
        rtf_frozen = results[0] if not isinstance(results[0], Exception) else RTFSummaryCreator._empty_summary()
        rtf_actual = results[1] if not isinstance(results[1], Exception) else RTFSummaryCreator._empty_summary()
        rtf_plan = results[2] if not isinstance(results[2], Exception) else RTFSummaryCreator._empty_summary()

        # OTD summaries (Sub4=FrozenAndAct, Sub6=FrozenAndPlan)
        _empty_otd = {"qtyUom": "", "uomType": "CONVERSION", "periodType": "Month",
            "frozenVer": frozen_ver, "frozenQty": 0, "planQty": 0, "actQty": 0, "list": []}
        otd_act = results[12] if not isinstance(results[12], Exception) else _empty_otd
        otd_plan = results[13] if not isinstance(results[13], Exception) else _empty_otd

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
                "otdSummaryAct": otd_act,
                "otdSummaryPlan": otd_plan,
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
        otd_type: str = "ACT",
    ) -> dict[str, Any]:
        """
        OTD Summary — frozen/plan/actual 모두 조회
        C# GetOTDSummaryRowsWithFrozenAndAct + GetOTDSummaryRowsWithFrozenAndPlan 통합
        """
        partition_key = f"{project_id}@{plan_ver[:6]}"
        frozen_partition_key = f"{project_id}@{frozen_ver[:6]}"
        # production_area 필터: C# 원본은 PRODUCTION_AREA(PROP01) 사용 (rpt_buffer_plan용)
        production_area_filter = ""
        if production_area:
            try:
                bp_cfg = self.repo.get_rpt_prop_config(project_id, plan_ver, "RPT_BUFFER_PLAN")
                for k, v in bp_cfg.items():
                    if isinstance(v, dict) and v.get("PropID", {}).get("Value") == "PRODUCTION_AREA":
                        production_area_filter = f"AND json_extract_scalar(b.prop_json, '$.{k}') LIKE '{production_area}%'"
                        break
            except Exception:
                pass
        cycle_dates = self._get_cycle_dates(project_id, plan_ver)

        # dataType → SQL GROUP BY 컬럼 매핑
        # C# 원본: DEMANDTYPE → prod_type (prop_json의 PROD_TYPE 키로 추출)
        # ITEMGROUP → item_group_id
        prod_type_prop_key = "PROP03"  # 기본값
        try:
            bp_cfg2 = self.repo.get_rpt_prop_config(project_id, plan_ver, "RPT_BUFFER_PLAN")
            for k, v in bp_cfg2.items():
                if isinstance(v, dict) and v.get("PropID", {}).get("Value") == "PROD_TYPE":
                    prod_type_prop_key = k
                    break
        except Exception:
            pass

        group_by_map = {
            "ITEMGROUP": "b.item_group_id",
            "DEMANDTYPE": f"json_extract_scalar(b.prop_json, '$.{prod_type_prop_key}')",
        }
        group_by_column = group_by_map.get(data_type, "b.item_group_id")
        # actual SQL: a. prefix + actual은 demand_type 컬럼 직접 사용 (prop_json 없음)
        act_group_by_map = {
            "ITEMGROUP": "a.item_group_id",
            "DEMANDTYPE": "a.demand_type",
        }
        act_group_by_column = act_group_by_map.get(data_type, "a.item_group_id")

        common_params = {
            "production_area_filter": production_area_filter,
            "cycle_start": cycle_dates["cycle_start"],
            "cycle_end": cycle_dates["cycle_end"],
            "next_cycle_end": cycle_dates["next_cycle_end"],
            "group_by_column": group_by_column,
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
        act_common = {**common_params, "group_by_column": act_group_by_column}
        actual_sql = Q.OTD_ACTUAL_SUMMARY_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            project_id=project_id,
            **act_common,
        )

        # otd_type에 따라 필요한 쿼리만 실행
        frozen_result = await self._trino_safe(project_id, frozen_sql)
        if otd_type == "PLAN":
            plan_result = await self._trino_safe(project_id, plan_sql)
            actual_result = []
        else:  # ACT
            plan_result = []
            actual_result = await self._trino_safe(project_id, actual_sql)

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
        """위젯 설정에서 operGroupIDs 필터 빌드.
        C# 원본: widget_value는 {"015. PRESS":{"uom_type":"CONV",...},...} 형태.
        키가 operGroupID. 설정 없으면 C# DEFAULT_WIDGET_VALUE 기본값 사용.
        """
        DEFAULT_OPER_GROUPS = [
            "015. PRESS", "020. DRILL", "031. 판넬도금", "037. 패턴DOT",
            "051. 패턴PT", "060. 인쇄 JET", "061. 인쇄 SCREEN",
            "062. 인쇄 SPRAY", "065. 마킹",
        ]
        raw = settings_map.get("OperGroupUtilization", "")
        ids = DEFAULT_OPER_GROUPS
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, dict) and len(data) > 0:
                    ids = list(data.keys())
            except (json.JSONDecodeError, AttributeError):
                pass
        in_clause = ", ".join(f"'{oid}'" for oid in ids)
        return f"AND t.oper_group_id IN ({in_clause})"

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
