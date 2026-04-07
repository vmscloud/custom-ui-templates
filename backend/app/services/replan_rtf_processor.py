"""
재수립 RTF 계산 엔진

C# RarReplanRtfProcessor + TypeQtyProcessor 완전 포팅.
RPT_SHIPMENT_PLAN + OPE_EXEC_ACTUAL 2개 데이터소스를 병합하고
위젯 설정 기반으로 EARLY/ON_TIME/LATE/SHORT 카테고리를 분류.
"""

from __future__ import annotations
import asyncio
import math
from datetime import date, datetime, timedelta
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.core.config import settings
from app.repositories.plan_dashboard import PlanDashboardRepository
from app.services import replan_rtf_queries as Q


class TypeQtyProcessor:
    """RTF 카테고리 분류 — C# TypeQtyProcessor 완전 포팅"""

    # Default settings (same as RTFSummaryCreator)
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

    # Maps PascalCase DB values to lowercase plan_type
    _STATUS_MAP = {
        "Early": "early",
        "OnTime": "on_time",
        "Late": "late",
        "Remain": "remain",
        "Short": "short",
    }

    def __init__(self, setting_list: list[dict] | None = None):
        self._type_dict: dict[str, dict[str, str]] = {}
        self._build_type_dict(setting_list or self.DEFAULT_SETTINGS)

    def _build_type_dict(self, setting_list: list[dict]) -> None:
        """SetCategoryDict — 위젯 설정으로 카테고리 매핑 테이블 빌드"""
        for ws_pascal, ws_lower in self._STATUS_MAP.items():
            # Find settings matching this plan_type
            matching = [s for s in setting_list if s.get("plan_type") == ws_lower]
            for setting in matching:
                category = setting.get("category", "")
                # Determine target classification
                if setting.get("apply_early"):
                    target = "early"
                elif setting.get("apply_on_time"):
                    target = "on_time"
                elif setting.get("apply_late"):
                    target = "late"
                elif setting.get("apply_short"):
                    target = "short"
                else:
                    target = "up_coming"  # excluded

                if category not in self._type_dict:
                    self._type_dict[category] = {}
                self._type_dict[category][ws_pascal] = target

    def get_type(self, category: str, warehouse_status: str | None) -> str | None:
        """GetType — 카테고리 + DB상태 → 분류 반환"""
        if not warehouse_status:
            return None
        cat_dict = self._type_dict.get(category)
        if cat_dict is None:
            return None
        return cat_dict.get(warehouse_status)

    @staticmethod
    def get_act_status(plan_date: date, cycle_start: date, cycle_end: date, due_date: date) -> str:
        """GetActStatus — 실적 데이터의 RTF 상태 결정"""
        if plan_date > due_date:
            return "late"
        if cycle_start <= due_date < cycle_end:
            return "on_time"
        if due_date >= cycle_end:
            return "early"
        return ""  # due_date < cycle_start → 무시


class ReplanRtfInfo:
    """Summary 행 — C# ReplanRtfInfo 포팅"""

    def __init__(self, due: str = "", group_key: str = ""):
        self.due = due
        self.cust_id = ""
        self.item_group_id = ""
        self.prod_type = ""
        self.region = ""
        self.qty_uom = ""
        self.demand_list: list[str] = []

        # 내부 누적값
        self._demand_qty = 0.0
        self._total_qty = 0.0
        self._early_qty = 0.0
        self._ontime_qty = 0.0
        self._late_qty = 0.0
        self._short_qty = 0.0
        self._upcoming_qty = 0.0
        self._plan_ontime_qty = 0.0
        self._plan_late_qty = 0.0

    @property
    def demand_cnt(self) -> int:
        return len(self.demand_list)

    def to_dict(self) -> dict:
        rtf = self._early_qty + self._ontime_qty + self._late_qty
        # shortQty = (short + upcoming) - (planOnTime + planLate) — C# 원본 동일
        short_qty = (self._short_qty + self._upcoming_qty) - (self._plan_ontime_qty + self._plan_late_qty)
        # totalQty = early + ontime + late + 조정된 shortQty — C# 원본 line 73
        total = self._early_qty + self._ontime_qty + self._late_qty + short_qty

        if total > 0:
            ratio_rtf = round(rtf / total * 1000) / 10
            ratio_early = round(self._early_qty / total * 1000) / 10
            ratio_ontime = round(self._ontime_qty / total * 1000) / 10
            ratio_late = ratio_rtf - ratio_ontime - ratio_early  # derived
            ratio_short = 100 - ratio_rtf
        else:
            ratio_rtf = ratio_early = ratio_ontime = ratio_late = ratio_short = 0.0

        return {
            "due": self.due,
            "custID": self.cust_id,
            "demandID": self.demand_list[0] if self.demand_list else "",
            "itemGroupID": self.item_group_id,
            "prodType": self.prod_type,
            "region": self.region,
            "qtyUom": self.qty_uom,
            "demandCnt": self.demand_cnt,
            "demandQty": round(self._demand_qty, 2),
            "totalQty": round(total, 2),
            "rtfQty": round(rtf, 2),
            "earlyQty": round(self._early_qty, 2),
            "onTimeQty": round(self._ontime_qty, 2),
            "lateQty": round(self._late_qty, 2),
            "shortQty": round(short_qty, 2),
            "upcomingQty": round(self._upcoming_qty, 2),
            "ratio_rtf": ratio_rtf,
            "ratio_early": ratio_early,
            "ratio_ontime": ratio_ontime,
            "ratio_late": ratio_late,
            "ratio_short": ratio_short,
        }


class ReplanRtfDetail:
    """Detail 행 — C# ReplanRtfDetail 포팅"""

    def __init__(self):
        self.demand_id = ""
        self.demand_priority = 0
        self.cust_id = ""
        self.item_group_id = ""
        self.item_id = ""
        self.item_name = ""
        self.item_label = ""
        self.site_id = ""
        self.site_name = ""
        self.due_date = ""
        self.due_week = ""
        self.due_month = ""
        self.max_earliness_day = None
        self.max_lateness_day = None
        self.qty_uom = ""
        self.demand_type = ""
        self.item_type = ""
        self.prod_type = ""
        self.item_size_type = ""
        self.item_spec = ""
        self._demand_qty = 0.0
        self._early_qty = 0.0
        self._ontime_qty = 0.0
        self._late_qty = 0.0
        self._short_qty = 0.0
        self._upcoming_qty = 0.0
        self._total_qty = 0.0

    def to_dict(self) -> dict:
        total = self._early_qty + self._ontime_qty + self._late_qty + self._short_qty
        rtf = self._early_qty + self._ontime_qty + self._late_qty

        if total > 0:
            ratio_rtf = math.floor(rtf / total * 1000) / 10
            ratio_early = math.ceil(self._early_qty / total * 1000) / 10
            ratio_ontime = math.floor(self._ontime_qty / total * 1000) / 10
            ratio_late = math.floor(self._late_qty / total * 1000) / 10
            ratio_short = math.floor(self._short_qty / total * 1000) / 10
        else:
            ratio_rtf = ratio_early = ratio_ontime = ratio_late = ratio_short = 0.0

        # dueDate formatting: "yyyy-MM-dd (-earlinessDay, +latenessDay)"
        due_display = self.due_date
        if self.max_earliness_day is not None or self.max_lateness_day is not None:
            e = self.max_earliness_day or 0
            l = self.max_lateness_day or 0
            due_display = f"{self.due_date} (-{e}, +{l})"

        return {
            "demandID": self.demand_id,
            "demandPriority": self.demand_priority,
            "custID": self.cust_id,
            "itemGroupID": self.item_group_id,
            "itemID": self.item_id,
            "itemName": self.item_name,
            "itemLabel": self.item_label,
            "siteID": self.site_id,
            "siteName": self.site_name,
            "demandQty": round(self._demand_qty, 2),
            "dueDate": due_display,
            "dueWeek": self.due_week,
            "dueMonth": self.due_month,
            "maxEarlinessDay": self.max_earliness_day,
            "maxLatenessDay": self.max_lateness_day,
            "totalQty": round(total, 2),
            "rtfQty": round(rtf, 2),
            "earlyQty": round(self._early_qty, 2),
            "onTimeQty": round(self._ontime_qty, 2),
            "lateQty": round(self._late_qty, 2),
            "shortQty": round(self._short_qty, 2),
            "upcomingQty": round(self._upcoming_qty, 2),
            "ratio_rtf": ratio_rtf,
            "ratio_early": ratio_early,
            "ratio_ontime": ratio_ontime,
            "ratio_late": ratio_late,
            "ratio_short": ratio_short,
            "qtyUom": self.qty_uom,
            "demand_type": self.demand_type,
            "item_type": self.item_type,
            "prod_type": self.prod_type,
            "item_size_type": self.item_size_type,
            "item_spec": self.item_spec,
        }


def _parse_date(s: str | None) -> date | None:
    """날짜 문자열 → date. yyyyMMdd 또는 yyyy-MM-dd 형식 지원"""
    if not s:
        return None
    s = s.strip()
    try:
        if len(s) == 8:
            return datetime.strptime(s, "%Y%m%d").date()
        if len(s) >= 10:
            return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        pass
    return None


class ReplanRtfProcessor:
    """재수립 RTF 계산 — C# RarReplanRtfProcessor 완전 포팅"""

    def __init__(
        self,
        adapter: QueryExecutorAdapter,
        type_proc: TypeQtyProcessor,
        is_lot_type: bool = True,
        is_default_uom: bool = True,
    ):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS
        self.type_proc = type_proc
        self._is_lot_type = is_lot_type
        self._is_default_uom = is_default_uom

        # Plan dates (set by _load_plan_dates)
        self._plan_start: date | None = None
        self._plan_end: date | None = None
        self._cycle_start: date | None = None
        self._cycle_end: date | None = None

        # Prop keys (set by _load_prop_keys)
        self._prop_keys: dict[str, str] = {
            "prod_type_prop_key": "PROP03",
            "production_area_prop_key": "PROP01",
        }

    async def _trino(self, project_id: str, sql: str) -> dict[str, Any]:
        result = await self.adapter.execute_direct_query(
            project_id=project_id,
            query=sql,
            catalog=self.catalog,
            schema=self.schema,
        )
        return result

    def _partition_key(self, project_id: str, plan_ver: str) -> str:
        return f"{project_id}@{plan_ver[:6]}"

    async def _load_prop_keys(self, project_id: str, partition_key: str, plan_ver: str) -> None:
        """odv_report_prop_config에서 RPT_SHIPMENT_PLAN의 prop_json 키 매핑 조회"""
        import json as _json
        import logging
        logger = logging.getLogger(__name__)
        try:
            sql = Q.PROP_CONFIG_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
            result = await self._trino(project_id, sql)
            rows = result.get("row", []) if result.get("success") else []
            if not rows:
                logger.warning("[ReplanRtf] prop config not found, using defaults")
                return
            prop_json_str = rows[0].get("prop_json", "{}")
            prop_config = _json.loads(prop_json_str) if isinstance(prop_json_str, str) else prop_json_str
            for key, val in prop_config.items():
                display_name = val.get("PropID", {}).get("Value", "")
                if display_name == "PROD_TYPE":
                    self._prop_keys["prod_type_prop_key"] = key
                elif display_name == "PRODUCTION_AREA":
                    self._prop_keys["production_area_prop_key"] = key
        except Exception as e:
            logger.warning(f"[ReplanRtf] prop config lookup failed: {e}, using defaults")

    def _build_list_filter(self, column: str, values: list[str] | None) -> str:
        """리스트 필터 → SQL IN 절"""
        if not values:
            return ""
        escaped = ", ".join(f"'{v}'" for v in values)
        return f"AND {column} IN ({escaped})"

    def _build_like_filter(self, column: str, value: str | None) -> str:
        """LIKE 필터 → SQL LIKE 절"""
        if not value:
            return ""
        return f"AND {column} LIKE '{value}%'"

    def _load_plan_dates(self, project_id: str, plan_ver: str) -> None:
        """cfg_plan_config + cfg_plan_cycle_info에서 계획/사이클 날짜 로드 (Trino)"""
        from app.core.database import execute_query
        rows = execute_query(
            f"""SELECT c.plan_start_datetime, c.plan_period,
                      ci.start_datetime AS cycle_start_date, ci.end_datetime AS cycle_end_date
               FROM cfg_plan_config c
               INNER JOIN cfg_plan_cycle_info ci
                   ON c.project_id = ci.project_id AND c.plan_cycle_id = ci.plan_cycle_id
               WHERE c.project_id = '{project_id}' AND c.plan_ver = '{plan_ver}' LIMIT 1""",
        )
        if not rows:
            return
        row = rows[0]
        start = row.get("plan_start_datetime")
        if isinstance(start, datetime):
            self._plan_start = start.date()
        elif isinstance(start, date):
            self._plan_start = start
        period = int(row.get("plan_period") or 1)
        if self._plan_start:
            self._plan_end = self._plan_start + timedelta(days=period)
        cs = row.get("cycle_start_date")
        ce = row.get("cycle_end_date")
        if isinstance(cs, datetime):
            self._cycle_start = cs.date()
        elif isinstance(cs, date):
            self._cycle_start = cs
        else:
            self._cycle_start = _parse_date(str(cs)) if cs else None
        if isinstance(ce, datetime):
            self._cycle_end = ce.date()
        elif isinstance(ce, date):
            self._cycle_end = ce
        else:
            self._cycle_end = _parse_date(str(ce)) if ce else None

    def _build_prod_status_filter(self, prod_status: str | None) -> str:
        """prodStatus → SQL WHERE 절"""
        if not prod_status or prod_status == "default":
            return ""
        mapping = {
            "late": "Late",
            "on_time": "OnTime",
            "short": "Remain",
            "early": "Early",
        }
        ws = mapping.get(prod_status)
        if ws:
            return f"AND WAREHOUSE_STATUS = '{ws}'"
        return ""

    def _get_qty(self, row: dict, field: str) -> float:
        """UOM에 따라 적절한 수량 필드 반환"""
        if self._is_default_uom:
            return float(row.get(field, 0) or 0)
        conv_field = field.replace("_qty", "_conv_qty")
        return float(row.get(conv_field, row.get(field, 0)) or 0)

    def _get_key_summary(self, summary_type: str, row: dict, agg_type: str) -> tuple[str, str]:
        """집계 키 생성 (due + sub_key)"""
        due = row.get("due_month", "") if agg_type == "MONTH" else row.get("due_week", "")
        due = due or ""

        sub_key = ""
        if summary_type.upper() == "CUST":
            sub_key = row.get("cust_id", "") or ""
        elif summary_type.upper() == "ITEMGROUP":
            sub_key = row.get("item_group_id", "") or ""
        elif summary_type.upper() == "PRODTYPE":
            sub_key = row.get("prod_type", "") or ""
        elif summary_type.upper() == "REGION":
            sub_key = row.get("production_area", row.get("region", "")) or ""

        return f"{due}|{sub_key}", due

    def _is_valid_info(self, row: dict, act_demand_set: set) -> bool:
        """IsValidInfo — Remain 상태 필터링"""
        ws = row.get("warehouse_status", "")
        if ws != "Remain":
            return True
        due = _parse_date(str(row.get("due_date", "")))
        if due and self._cycle_end and due < self._cycle_end:
            return True
        demand_id = row.get("demand_id", "")
        if demand_id in act_demand_set:
            return True
        return False

    # ─── GetSummary (Main) ───

    async def get_summary(
        self, project_id: str, params
    ) -> list[dict]:
        pk = self._partition_key(project_id, params.planVer)
        self._load_plan_dates(project_id, params.planVer)
        if not self._plan_start or not self._cycle_start or not self._cycle_end:
            return []

        await self._load_prop_keys(project_id, pk, params.planVer)

        # 1. 출하계획 조회
        ship_sql = Q.SHIPMENT_PLAN_SQL.format(
            partition_key=pk,
            plan_ver=params.planVer,
            prod_status_filter=self._build_prod_status_filter(params.prodStatus),
            due_filter="",
            demand_id_filter="",
            production_area_filter=self._build_like_filter("production_area", getattr(params, "productionArea", None)),
            item_group_filter=self._build_list_filter("item_group_id", getattr(params, "itemGroupIDs", None)),
            customer_filter=self._build_list_filter("cust_id", getattr(params, "customers", None)),
            prod_type_filter=self._build_list_filter("prod_type", getattr(params, "prodTypes", None)),
            **self._prop_keys,
        )
        ship_result = await self._trino(project_id, ship_sql)
        ship_rows = ship_result.get("row", []) if ship_result.get("success") else []

        # 2. 계획 종료일
        end_sql = Q.PLAN_END_DATE_SQL.format(project_id=project_id, plan_ver=params.planVer)
        end_result = await self._trino(project_id, end_sql)
        plan_end = self._plan_end
        if end_result.get("success") and end_result.get("row"):
            pe = end_result["row"][0].get("plan_end_date")
            if pe:
                plan_end = _parse_date(str(pe)) or self._plan_end

        # 3. DEMAND 모드 전처리
        demand_dict: dict[str, float] = {}
        if not self._is_lot_type:
            for row in ship_rows:
                due = _parse_date(str(row.get("due_date", "")))
                if not due:
                    continue
                category = "after_plan" if (plan_end and due >= plan_end) else "within_plan"
                ws = row.get("warehouse_status", "")
                rtype = self.type_proc.get_type(category, ws)
                if not rtype:
                    continue
                did = row.get("demand_id", "")
                rtf_qty = self._get_rtf_qty_ship(row, rtype)
                demand_dict[did] = demand_dict.get(did, 0) + rtf_qty

        # 4. 최종품 버퍼 + 실적 조회
        buf_sql = Q.FINAL_ITEM_BUFFER_SQL.format(partition_key=pk, plan_ver=params.planVer)
        buf_result = await self._trino(project_id, buf_sql)
        buffer_ids = [r["buffer_id"] for r in (buf_result.get("row", []) if buf_result.get("success") else [])]

        act_rows = []
        if buffer_ids:
            act_end = (self._plan_start - timedelta(days=1)).isoformat()
            bid_str = ", ".join(f"'{b}'" for b in buffer_ids)
            act_sql = Q.EXEC_ACTUAL_SQL.format(
                partition_key=pk,
                plan_ver=params.planVer,
                cycle_start_date=self._cycle_start.isoformat(),
                act_end_date=act_end,
                buffer_filter=f"AND buffer_id IN ({bid_str})",
                demand_id_filter="",
            )
            act_result = await self._trino(project_id, act_sql)
            act_rows = act_result.get("row", []) if act_result.get("success") else []

        act_demand_set = {r.get("demand_id", "") for r in act_rows if r.get("demand_id")}

        # 5. 메인 루프 — 출하계획
        infos: dict[str, ReplanRtfInfo] = {}
        total_info = ReplanRtfInfo(due="[TOTAL]")
        seen_demands: set[str] = set()

        for row in ship_rows:
            due = _parse_date(str(row.get("due_date", "")))
            if not due:
                continue
            if not self._is_valid_info(row, act_demand_set):
                continue

            category = "after_plan" if (plan_end and due >= plan_end) else "within_plan"
            ws = row.get("warehouse_status", "")
            rtype = self.type_proc.get_type(category, ws)
            if not rtype:
                continue

            key, due_str = self._get_key_summary(params.summary, row, params.aggregateType)
            if key not in infos:
                info = ReplanRtfInfo(due=due_str)
                info.cust_id = row.get("cust_id", "")
                info.item_group_id = row.get("item_group_id", "")
                info.prod_type = row.get("prod_type", "")
                info.region = row.get("production_area", "")
                info.qty_uom = row.get("qty_uom", "")
                infos[key] = info
            else:
                info = infos[key]

            demand_id = row.get("demand_id", "")

            # First-time demand processing
            if demand_id not in seen_demands:
                seen_demands.add(demand_id)
                demand_type = "short" if (self._plan_start and self._plan_start > due) else "up_coming"
                d_qty = self._get_qty(row, "demand_qty")
                self._update_demand_info(info, demand_id, d_qty, demand_type, due)
                self._update_demand_info(total_info, demand_id, d_qty, demand_type, due)

            # DEMAND mode skip
            if not self._is_lot_type:
                d_rtf = round(demand_dict.get(demand_id, 0), 6)
                d_qty = self._get_qty(row, "demand_qty")
                if d_qty > d_rtf:
                    continue

            # Update quantities
            self._update_ship_qty(info, row, rtype)
            self._update_ship_qty(total_info, row, rtype)

        # 6. 실적 병합
        self._add_act_result(params, act_rows, infos, demand_dict, total_info)

        # 7. 결과 조합
        infos["__total__"] = total_info
        result = [v.to_dict() for v in infos.values()]
        # Sort: TOTAL last, then by due
        result.sort(key=lambda x: (x["due"] == "[TOTAL]", x.get("itemGroupID", ""), x["due"]))
        return result

    # ─── GetDetail ───

    async def get_detail(
        self, project_id: str, params
    ) -> list[dict]:
        pk = self._partition_key(project_id, params.planVer)
        self._load_plan_dates(project_id, params.planVer)
        if not self._plan_start or not self._cycle_start or not self._cycle_end:
            return []

        await self._load_prop_keys(project_id, pk, params.planVer)

        # Due filter
        due_filter = ""
        if params.dueMonth:
            dm = params.dueMonth.replace("-", "")
            due_filter = f"AND DUE_MONTH = '{dm}'"
        elif params.dueWeek:
            dw = params.dueWeek.replace("-", "")
            due_filter = f"AND DUE_WEEK = '{dw}'"

        ship_sql = Q.SHIPMENT_PLAN_SQL.format(
            partition_key=pk,
            plan_ver=params.planVer,
            prod_status_filter=self._build_prod_status_filter(params.prodStatus),
            due_filter=due_filter,
            demand_id_filter="",
            production_area_filter=self._build_like_filter("production_area", getattr(params, "productionArea", None)),
            item_group_filter=self._build_list_filter("item_group_id", getattr(params, "itemGroupIDs", None)),
            customer_filter=self._build_list_filter("cust_id", getattr(params, "customers", None)),
            prod_type_filter=self._build_list_filter("prod_type", getattr(params, "prodTypes", None)),
            **self._prop_keys,
        )
        ship_result = await self._trino(project_id, ship_sql)
        ship_rows = ship_result.get("row", []) if ship_result.get("success") else []

        end_sql = Q.PLAN_END_DATE_SQL.format(project_id=project_id, plan_ver=params.planVer)
        end_result = await self._trino(project_id, end_sql)
        plan_end = self._plan_end
        if end_result.get("success") and end_result.get("row"):
            pe = end_result["row"][0].get("plan_end_date")
            if pe:
                plan_end = _parse_date(str(pe)) or self._plan_end

        # DEMAND pre-pass
        demand_dict: dict[str, float] = {}
        if not self._is_lot_type:
            for row in ship_rows:
                due = _parse_date(str(row.get("due_date", "")))
                if not due:
                    continue
                category = "after_plan" if (plan_end and due >= plan_end) else "within_plan"
                ws = row.get("warehouse_status", "")
                rtype = self.type_proc.get_type(category, ws)
                if not rtype:
                    continue
                did = row.get("demand_id", "")
                demand_dict[did] = demand_dict.get(did, 0) + self._get_rtf_qty_ship(row, rtype)

        # Actuals
        buf_sql = Q.FINAL_ITEM_BUFFER_SQL.format(partition_key=pk, plan_ver=params.planVer)
        buf_result = await self._trino(project_id, buf_sql)
        buffer_ids = [r["buffer_id"] for r in (buf_result.get("row", []) if buf_result.get("success") else [])]

        act_rows = []
        if buffer_ids:
            act_end = (self._plan_start - timedelta(days=1)).isoformat()
            bid_str = ", ".join(f"'{b}'" for b in buffer_ids)
            act_sql = Q.EXEC_ACTUAL_SQL.format(
                partition_key=pk, plan_ver=params.planVer,
                cycle_start_date=self._cycle_start.isoformat(), act_end_date=act_end,
                buffer_filter=f"AND buffer_id IN ({bid_str})", demand_id_filter="",
            )
            act_result = await self._trino(project_id, act_sql)
            act_rows = act_result.get("row", []) if act_result.get("success") else []

        act_demand_set = {r.get("demand_id", "") for r in act_rows if r.get("demand_id")}

        # Main loop — one entry per demandID
        details: dict[str, ReplanRtfDetail] = {}

        for row in ship_rows:
            due = _parse_date(str(row.get("due_date", "")))
            if not due:
                continue
            if not self._is_valid_info(row, act_demand_set):
                continue

            category = "after_plan" if (plan_end and due >= plan_end) else "within_plan"
            ws = row.get("warehouse_status", "")
            rtype = self.type_proc.get_type(category, ws)
            if not rtype:
                continue

            demand_id = row.get("demand_id", "")
            if demand_id not in details:
                d = ReplanRtfDetail()
                d.demand_id = demand_id
                d.cust_id = row.get("cust_id", "")
                d.item_group_id = row.get("item_group_id", "")
                d.item_id = row.get("item_id", "")
                d.item_name = row.get("item_name", "")
                d.item_label = f"{d.item_id} / {d.item_name or d.item_id}"
                d.site_id = row.get("site_id", "")
                d.site_name = row.get("site_name", "")
                d.due_date = due.isoformat()
                d.due_week = row.get("due_week", "")
                d.due_month = row.get("due_month", "")
                d.max_earliness_day = row.get("max_earliness_day")
                d.max_lateness_day = row.get("max_lateness_day")
                d.qty_uom = row.get("qty_uom", "")
                d.demand_type = row.get("demand_type", "")
                d.item_type = row.get("item_type", "")
                d.prod_type = row.get("prod_type", "")
                d.item_size_type = row.get("item_size_type", "")
                d.item_spec = row.get("item_spec", "")
                d._demand_qty = self._get_qty(row, "demand_qty")
                try:
                    d.demand_priority = int(row.get("demand_priority", 0) or 0)
                except (ValueError, TypeError):
                    d.demand_priority = 0
                details[demand_id] = d
            else:
                d = details[demand_id]

            if not self._is_lot_type:
                d_rtf = round(demand_dict.get(demand_id, 0), 4)
                if self._get_qty(row, "demand_qty") > d_rtf:
                    continue

            self._update_ship_qty_detail(d, row, rtype)

        # Add actuals to detail
        self._add_act_detail(params, act_rows, details, demand_dict)

        result = [v.to_dict() for v in details.values()]
        result.sort(key=lambda x: (x["ratio_rtf"], x["ratio_late"] if x["ratio_late"] != 0 else float('inf'), x["dueDate"], x["demandID"]))
        return result

    # ─── ProdDetail ───

    async def get_prod_detail(self, project_id: str, params) -> dict:
        qty_col = "plan_conv_qty" if params.uomType == "CONVERSION" else "plan_qty"
        qty_uom_col = "conv_qty_uom" if params.uomType == "CONVERSION" else "qty_uom"

        detail_sql = Q.PROD_DETAIL_SQL.format(
            project_id=project_id,
            demand_id=params.demandID,
            qty_col=qty_col, qty_uom_col=qty_uom_col,
        )
        section_sql = Q.SECTION_SQL.format(
            project_id=project_id,
            demand_id=params.demandID,
        )
        detail_result, section_result = await asyncio.gather(
            self._trino(project_id, detail_sql),
            self._trino(project_id, section_sql),
        )
        return {
            "detail": detail_result.get("row", []) if detail_result.get("success") else [],
            "period": section_result.get("row", []) if section_result.get("success") else [],
        }

    # ─── GetProdTypes ───

    async def get_prod_types(self, project_id: str, plan_ver: str) -> list[dict]:
        pk = self._partition_key(project_id, plan_ver)
        await self._load_prop_keys(project_id, pk, plan_ver)
        sql = Q.PROD_TYPES_SQL.format(partition_key=pk, plan_ver=plan_ver, **self._prop_keys)
        result = await self._trino(project_id, sql)
        return result.get("row", []) if result.get("success") else []

    # ─── Helpers ───

    def _get_rtf_qty_ship(self, row: dict, rtype: str) -> float:
        """출하계획 RTF 수량 (DEMAND 모드용)"""
        if rtype == "short":
            return 0
        return (
            self._get_qty(row, "early_qty")
            + self._get_qty(row, "ontime_qty")
            + self._get_qty(row, "late_qty")
        )

    def _update_demand_info(
        self, info: ReplanRtfInfo, demand_id: str, demand_qty: float,
        demand_type: str, due: date,
    ) -> None:
        """첫 수요 등록 — demandQty + short/upcoming"""
        info.demand_list.append(demand_id)
        info._demand_qty += demand_qty
        if self._cycle_end and due >= self._cycle_end:
            return
        if demand_type == "short":
            info._short_qty += demand_qty
            info._total_qty += demand_qty
        elif demand_type == "up_coming":
            info._upcoming_qty += demand_qty

    def _update_ship_qty(self, info: ReplanRtfInfo, row: dict, rtype: str) -> None:
        """출하계획 수량 누적"""
        early = self._get_qty(row, "early_qty")
        ontime = self._get_qty(row, "ontime_qty")
        late = self._get_qty(row, "late_qty")
        info._early_qty += early
        info._total_qty += early
        info._ontime_qty += ontime
        info._plan_ontime_qty += ontime
        info._total_qty += ontime
        info._late_qty += late
        info._plan_late_qty += late
        info._total_qty += late

    def _update_ship_qty_detail(self, d: ReplanRtfDetail, row: dict, rtype: str) -> None:
        """출하계획 수량 누적 (Detail)"""
        early = self._get_qty(row, "early_qty")
        ontime = self._get_qty(row, "ontime_qty")
        late = self._get_qty(row, "late_qty")
        short = self._get_qty(row, "short_qty")
        d._early_qty += early
        d._ontime_qty += ontime
        d._late_qty += late
        d._short_qty += short
        d._total_qty += early + ontime + late + short

    def _add_act_result(
        self, params, act_rows: list, infos: dict[str, ReplanRtfInfo],
        demand_dict: dict[str, float], total_info: ReplanRtfInfo,
    ) -> None:
        """실적 데이터를 Summary에 병합"""
        for row in act_rows:
            plan_date = _parse_date(str(row.get("plan_date", "")))
            due_date = _parse_date(str(row.get("due_date", "")))
            if not plan_date or not due_date:
                continue

            status = self.type_proc.get_act_status(plan_date, self._cycle_start, self._cycle_end, due_date)

            # prodStatus validation
            if params.prodStatus and params.prodStatus != "default":
                if status != params.prodStatus:
                    continue

            key, due_str = self._get_key_summary(params.summary, row, params.aggregateType)
            if key not in infos:
                info = ReplanRtfInfo(due=due_str)
                info.cust_id = row.get("cust_id", "")
                info.item_group_id = row.get("item_group_id", "")
                info.prod_type = row.get("prod_type", "")
                info.region = row.get("production_area", "")
                info.qty_uom = row.get("qty_uom", "")
                infos[key] = info
            else:
                info = infos[key]

            demand_id = row.get("demand_id", "")
            plan_qty = float(row.get("plan_qty", 0) or 0)
            if not self._is_default_uom:
                plan_qty = float(row.get("plan_conv_qty", row.get("plan_qty", 0)) or 0)

            # DEMAND mode check
            if not self._is_lot_type:
                if demand_id not in demand_dict:
                    demand_dict[demand_id] = 0
                demand_dict[demand_id] += self._get_act_rtf_qty(plan_qty, status)
                if plan_qty > round(demand_dict[demand_id], 4):
                    continue

            if status:
                self._update_act_qty(info, plan_qty, status)
                self._update_act_qty(total_info, plan_qty, status)

    def _add_act_detail(
        self, params, act_rows: list, details: dict[str, ReplanRtfDetail],
        demand_dict: dict[str, float],
    ) -> None:
        """실적 데이터를 Detail에 병합"""
        for row in act_rows:
            plan_date = _parse_date(str(row.get("plan_date", "")))
            due_date = _parse_date(str(row.get("due_date", "")))
            if not plan_date or not due_date:
                continue

            status = self.type_proc.get_act_status(plan_date, self._cycle_start, self._cycle_end, due_date)
            if params.prodStatus and params.prodStatus != "default":
                if status != params.prodStatus:
                    continue

            demand_id = row.get("demand_id", "")
            plan_qty = float(row.get("plan_qty", 0) or 0)
            if not self._is_default_uom:
                plan_qty = float(row.get("plan_conv_qty", row.get("plan_qty", 0)) or 0)

            if demand_id not in details:
                d = ReplanRtfDetail()
                d.demand_id = demand_id
                d.item_id = row.get("item_id", "")
                d.item_group_id = row.get("item_group_id", "")
                d.cust_id = row.get("cust_id", "")
                d.prod_type = row.get("prod_type", "")
                d.due_date = due_date.isoformat()
                d.qty_uom = row.get("qty_uom", "")
                try:
                    d.demand_priority = int(row.get("demand_priority", 0) or 0)
                except (ValueError, TypeError):
                    d.demand_priority = 0
                details[demand_id] = d
            else:
                d = details[demand_id]

            if not self._is_lot_type:
                if demand_id not in demand_dict:
                    demand_dict[demand_id] = 0
                demand_dict[demand_id] += self._get_act_rtf_qty(plan_qty, status)
                if plan_qty > round(demand_dict[demand_id], 4):
                    continue

            if status:
                self._update_act_qty_detail(d, plan_qty, status)

    @staticmethod
    def _get_act_rtf_qty(plan_qty: float, status: str) -> float:
        if status in ("early", "on_time", "late"):
            return plan_qty
        return 0

    @staticmethod
    def _update_act_qty(info: ReplanRtfInfo, plan_qty: float, status: str) -> None:
        if status == "early":
            info._early_qty += plan_qty
            info._total_qty += plan_qty
        elif status == "on_time":
            info._ontime_qty += plan_qty
            info._total_qty += plan_qty
        elif status == "late":
            info._late_qty += plan_qty
            info._total_qty += plan_qty

    @staticmethod
    def _update_act_qty_detail(d: ReplanRtfDetail, plan_qty: float, status: str) -> None:
        if status == "early":
            d._early_qty += plan_qty
            d._total_qty += plan_qty
        elif status == "on_time":
            d._ontime_qty += plan_qty
            d._total_qty += plan_qty
        elif status == "late":
            d._late_qty += plan_qty
            d._total_qty += plan_qty
