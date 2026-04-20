"""
재실행 계획 (ReExecutePlan) 서비스

rpt_oper_group_plan, rpt_buffer_plan 테이블에서 재실행 계획 데이터를 조회합니다.
원본: AleatorikUI.DP/Services/rar/RarReExecutePlanService.cs
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.core.database import execute_query
from app.services import re_execute_plan_queries as Q
from fastapi import Depends

# aggregateType → 컬럼 매핑 (원본 GetAggrValue / SetAggregateColumn)
AGGR_COLUMN_MAP = {
    "itemGroup": "item_group_id",
    "cust": "cust_id",
    "region": "region",
    "demandType": "demand_type",
    "PERIOD": "due_month",
}

# aggregateType → region 필터 필드 (WHERE 절에 들어갈 실제 SQL 표현)
REGION_FIELD_EXPR = "json_extract_scalar(prop_json, '$.production_area')"


class ReExecutePlanService:
    """재실행 계획 비즈니스 로직"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS

    async def _trino(self, project_id: str, sql: str) -> dict[str, Any]:
        return await self.adapter.execute_direct_query(
            project_id=project_id,
            query=sql,
            catalog=self.catalog,
            schema=self.schema,
        )

    async def _trino_all(
        self, project_id: str, sql: str, page_size: int = 50000, max_pages: int = 500
    ) -> dict[str, Any]:
        """
        Trino 결과가 페이지당 최대 50,000건이라 has_next가 True인 동안 모든 페이지를 모은다.
        원본 PostgreSQL 직결은 페이지네이션 없이 전체를 반환하므로, 값 누락 없이 동일한 집합을
        얻으려면 모든 페이지를 fetch해야 한다.
        """
        all_rows: list[dict] = []
        columns: list[str] = []
        page = 1
        while page <= max_pages:
            result = await self.adapter.execute_direct_query(
                project_id=project_id,
                query=sql,
                catalog=self.catalog,
                schema=self.schema,
                page=page,
                limit=page_size,
            )
            if not result.get("success"):
                return result
            rows = result.get("row", []) or []
            all_rows.extend(rows)
            if not columns:
                columns = result.get("columns", []) or []
            if not result.get("has_next") or not rows:
                break
            page += 1
        return {
            "success": True,
            "row": all_rows,
            "columns": columns,
            "rowcount": len(all_rows),
        }

    def _safe_rows(self, result: dict[str, Any]) -> list[dict]:
        return result.get("row", []) if result.get("success") else []

    def _partition_key(self, project_id: str, plan_ver: str) -> str:
        return f"{project_id}@{plan_ver[:6]}"

    def _build_filter(self, field: str, values: list) -> str:
        """범용 IN 필터 빌더 (null/빈값 자동 제거)"""
        filtered = [v for v in values if v is not None and v != ""]
        if not filtered:
            return ""
        escaped = ", ".join(f"'{str(v).replace(chr(39), chr(39) * 2)}'" for v in filtered)
        return f"AND {field} IN ({escaped})"

    async def get_regions(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.REGIONS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_oper_groups(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.OPER_GROUPS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_buffers(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.BUFFERS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_opers(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.OPERS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_customers(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.CUSTOMERS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_item_groups(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.ITEM_GROUPS_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_demand_types(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.DEMAND_TYPES_SQL.format(partition_key=partition_key, plan_ver=plan_ver)
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    def _get_plan_start_date(self, project_id: str, plan_ver: str) -> str:
        rows = execute_query(
            f"SELECT plan_start_datetime FROM cfg_plan_config "
            f"WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1"
        )
        if not rows:
            return "2000-01-01"
        start = rows[0].get("plan_start_datetime")
        if isinstance(start, datetime):
            return str(start.date())
        if isinstance(start, date):
            return str(start)
        return str(start)[:10] if start else "2000-01-01"

    def _get_plan_range(self, project_id: str, plan_ver: str) -> tuple[str, str]:
        """
        원본 SetPlanStartEndDate:
          _startDatetime = plan_start_datetime
          _endDatetime   = _startDatetime + plan_period
        AddReExecutePlanInfo에서 이 범위 밖 date는 drop.
        반환: (plan_start_iso, plan_end_iso_exclusive)
        """
        rows = execute_query(
            f"SELECT plan_start_datetime, plan_period FROM cfg_plan_config "
            f"WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1"
        )
        if not rows:
            return "", ""
        start = rows[0].get("plan_start_datetime")
        period = rows[0].get("plan_period") or 1
        try:
            if isinstance(start, datetime):
                start_obj = start.date()
            elif isinstance(start, date):
                start_obj = start
            else:
                start_obj = datetime.strptime(str(start)[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return "", ""
        end_obj = start_obj + timedelta(days=int(period))
        return str(start_obj), str(end_obj)

    def _get_frozen_ver(self, project_id: str, plan_ver: str) -> str:
        """
        원본 GetFrozenPlanVer 포팅.
        찾지 못하면 빈 문자열 반환 — 호출자는 frozen 쿼리를 스킵해야 한다.
        원본: if (string.IsNullOrEmpty(frozenPlanVer) == true) return; (SetFrozenData)
        """
        try:
            cycle_rows = execute_query(
                f"SELECT plan_cycle_id FROM cfg_plan_config "
                f"WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1"
            )
            if not cycle_rows:
                return ""
            plan_cycle_id = cycle_rows[0].get("plan_cycle_id", "")
            if not plan_cycle_id:
                return ""

            frozen_rows = execute_query(
                f"""SELECT plan_ver FROM cfg_plan_config
                    WHERE project_id = '{project_id}'
                      AND plan_cycle_id = '{plan_cycle_id}'
                      AND plan_status = 'FROZEN'
                      AND plan_ver <> '{plan_ver}'
                    ORDER BY plan_ver DESC LIMIT 1"""
            )
            if frozen_rows and frozen_rows[0].get("plan_ver"):
                return frozen_rows[0]["plan_ver"]

            fallback_rows = execute_query(
                f"""SELECT frozen_plan_ver FROM cfg_plan_cycle_info
                    WHERE project_id = '{project_id}' AND plan_cycle_id = '{plan_cycle_id}'
                    LIMIT 1"""
            )
            if fallback_rows and fallback_rows[0].get("frozen_plan_ver"):
                fv = fallback_rows[0]["frozen_plan_ver"]
                if fv and fv != plan_ver:
                    return fv
        except Exception:
            pass
        return ""

    def _get_cycle_dates(self, project_id: str, plan_ver: str) -> tuple[str, str]:
        """plan cycle start/end 조회"""
        try:
            rows = execute_query(
                f"""SELECT ci.start_datetime AS cycle_start, ci.end_datetime AS cycle_end
                    FROM cfg_plan_config c
                    INNER JOIN cfg_plan_cycle_info ci
                        ON c.project_id = ci.project_id AND c.plan_cycle_id = ci.plan_cycle_id
                    WHERE c.project_id = '{project_id}' AND c.plan_ver = '{plan_ver}'
                    LIMIT 1"""
            )
            if rows:
                cs = str(rows[0].get("cycle_start", ""))[:10]
                ce = str(rows[0].get("cycle_end", ""))[:10]
                if cs and ce:
                    return cs, ce
        except Exception:
            pass
        return (
            plan_ver[:4] + "-" + plan_ver[4:6] + "-01",
            plan_ver[:4] + "-" + plan_ver[4:6] + "-30",
        )

    @staticmethod
    def _to_yyyymmdd(iso_date: str) -> str:
        """'YYYY-MM-DD' → 'YYYYMMDD'. plan_date 컬럼이 하이픈 없는 문자열이라 SQL 비교용."""
        return (iso_date or "").replace("-", "")

    def _build_pivot_sql(
        self,
        partition_key: str,
        plan_ver: str,
        params,
        qty_col: str,
        start_date: str,
        end_date: str,
        summary_type: str,
    ) -> str:
        """summaryType에 따라 피벗 SQL 생성 (raw row)."""
        start_yyyymmdd = self._to_yyyymmdd(start_date)
        end_yyyymmdd = self._to_yyyymmdd(end_date)
        demand_type_filter = self._build_filter("demand_type", params.demandTypes)
        item_group_filter = self._build_filter("item_group_id", params.itemGroupIDs)
        customer_filter = self._build_filter("cust_id", params.customers)
        region_filter = self._build_filter(REGION_FIELD_EXPR, params.regions)

        if summary_type == "BUFFER":
            buffer_filter = self._build_filter("std_buffer_id", params.bufferIDs)
            return Q.PIVOT_BUFFER_SQL.format(
                partition_key=partition_key,
                plan_ver=plan_ver,
                qty_col=qty_col,
                start_date=start_yyyymmdd,
                end_date=end_yyyymmdd,
                buffer_filter=buffer_filter,
                customer_filter=customer_filter,
                demand_type_filter=demand_type_filter,
                item_group_filter=item_group_filter,
                region_filter=region_filter,
            )

        oper_group_filter = self._build_filter("oper_group_id", params.operGroupIDs)
        oper_filter = self._build_filter("oper_id", params.operIDs)
        return Q.PIVOT_OPER_GROUP_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            qty_col=qty_col,
            start_date=start_yyyymmdd,
            end_date=end_yyyymmdd,
            oper_group_filter=oper_group_filter,
            oper_filter=oper_filter,
            demand_type_filter=demand_type_filter,
            item_group_filter=item_group_filter,
            customer_filter=customer_filter,
            region_filter=region_filter,
        )

    @staticmethod
    def _extract_aggr_value(row: dict, aggregate_type: str) -> str:
        col = AGGR_COLUMN_MAP.get(aggregate_type, "")
        if not col:
            return ""
        val = row.get(col)
        return str(val) if val not in (None, "") else ""

    @staticmethod
    def _format_month_week(date_str: str) -> tuple[str, str]:
        try:
            dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return "", ""
        month_str = dt_obj.strftime("%Y-%m")
        iso = dt_obj.isocalendar()
        week_str = f"{iso[0]}-{iso[1]:02d}"
        return month_str, week_str

    async def get_main(self, project_id: str, params) -> dict[str, Any]:
        """
        메인 데이터 조회 — 원본 GetReExecutePlanDatas 포팅.
        1. plan / frozen / demand 병렬 조회
        2. row 단위로 aggr_value 추출 후 (key, date) 누적
        3. FillEmptyCell → CalculateDiff → TOTAL row 생성
        4. plan/frozen/diff 3종 flat list 반환 (각 셀에 demandIDs 포함)
        """
        summary_type = (getattr(params, "summaryType", "OPERGROUP") or "OPERGROUP").upper()
        aggregate_type = getattr(params, "aggregateType", "") or ""

        partition_key = self._partition_key(project_id, params.planVer)
        if summary_type == "BUFFER":
            qty_col = "in_plan_conv_qty" if params.uomType == "CONVERSION" else "in_plan_qty"
        else:
            qty_col = "out_plan_conv_qty" if params.uomType == "CONVERSION" else "out_plan_qty"

        frozen_ver = self._get_frozen_ver(project_id, params.planVer)
        cycle_start, cycle_end = self._get_cycle_dates(project_id, params.planVer)
        plan_start_iso, plan_end_iso = self._get_plan_range(project_id, params.planVer)

        plan_sql = self._build_pivot_sql(
            partition_key, params.planVer, params, qty_col, cycle_start, cycle_end, summary_type
        )

        demand_type_filter = self._build_filter("demand_type", params.demandTypes)
        customer_filter = self._build_filter("cust_id", params.customers)
        demand_sql = Q.DEMAND_LIST_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            demand_type_filter=demand_type_filter,
            customer_filter=customer_filter,
        )

        # 원본 SetFrozenData: frozen_ver 없으면 frozen 쿼리 스킵 (FROZEN 값은 0으로 유지)
        if frozen_ver and frozen_ver != params.planVer:
            frozen_pk = self._partition_key(project_id, frozen_ver)
            frozen_sql = self._build_pivot_sql(
                frozen_pk, frozen_ver, params, qty_col, cycle_start, cycle_end, summary_type
            )
            plan_result, frozen_result, demand_result = await asyncio.gather(
                self._trino_all(project_id, plan_sql),
                self._trino_all(project_id, frozen_sql),
                self._trino_all(project_id, demand_sql),
            )
            frozen_rows = self._safe_rows(frozen_result)
        else:
            frozen_pk = ""
            plan_result, demand_result = await asyncio.gather(
                self._trino_all(project_id, plan_sql),
                self._trino_all(project_id, demand_sql),
            )
            frozen_result = {"success": True, "row": []}
            frozen_rows = []

        plan_rows = self._safe_rows(plan_result)
        demand_data = self._safe_rows(demand_result)

        # 집계 구조: {key: {oper_group_id, oper_id, buffer_id, due_month, aggr_value, dates: {date: {plan_qty, frozen_qty, demand_ids}}}}
        data_dict: dict[str, dict[str, Any]] = {}
        min_date: str = ""
        max_date: str = ""

        def in_plan_range(d: str) -> bool:
            if not plan_start_iso or not plan_end_iso:
                return True
            return plan_start_iso <= d < plan_end_iso

        def process(rows: list[dict], plan_type: str) -> None:
            nonlocal min_date, max_date
            for row in rows:
                aggr_value = self._extract_aggr_value(row, aggregate_type)
                if aggregate_type and not aggr_value:
                    continue

                d = str(row.get("date") or "")[:10]
                if not d or not in_plan_range(d):
                    continue

                ogid = str(row.get("oper_group_id") or "")
                oid = str(row.get("oper_id") or "")
                bid = str(row.get("buffer_id") or "")
                due_month = str(row.get("due_month") or "")
                key = f"{ogid}|{oid}|{bid}|{aggr_value}|{due_month}"

                if not min_date or d < min_date:
                    min_date = d
                if d > max_date:
                    max_date = d

                info = data_dict.get(key)
                if info is None:
                    info = {
                        "oper_group_id": ogid,
                        "oper_id": oid,
                        "buffer_id": bid,
                        "due_month": due_month,
                        "aggr_value": aggr_value,
                        "dates": {},
                    }
                    data_dict[key] = info

                cell = info["dates"].get(d)
                if cell is None:
                    cell = {"plan_qty": 0.0, "frozen_qty": 0.0, "demand_ids": set()}
                    info["dates"][d] = cell

                try:
                    qty = float(row.get("qty") or 0)
                except (TypeError, ValueError):
                    qty = 0.0

                if plan_type == "PLAN":
                    cell["plan_qty"] += qty
                else:
                    cell["frozen_qty"] += qty

                demand_id = row.get("demand_id")
                if demand_id:
                    cell["demand_ids"].add(str(demand_id))

        process(plan_rows, "PLAN")
        process(frozen_rows, "FROZEN")

        # FillEmptyCell: min~max 구간 빈 날짜 채우기
        if min_date and max_date and min_date <= max_date:
            try:
                min_dt = datetime.strptime(min_date, "%Y-%m-%d")
                max_dt = datetime.strptime(max_date, "%Y-%m-%d")
                for info in data_dict.values():
                    dt_cur = min_dt
                    while dt_cur <= max_dt:
                        ds = dt_cur.strftime("%Y-%m-%d")
                        if ds not in info["dates"]:
                            info["dates"][ds] = {
                                "plan_qty": 0.0,
                                "frozen_qty": 0.0,
                                "demand_ids": set(),
                            }
                        dt_cur += timedelta(days=1)
            except ValueError:
                pass

        # CalculateDiff + TOTAL + flat emit
        result_data: list[dict] = []
        for info in data_dict.values():
            base = {
                "oper_group_id": info["oper_group_id"],
                "oper_id": info["oper_id"],
                "buffer_id": info["buffer_id"],
                "due_month": info["due_month"],
                "aggr_value": info["aggr_value"],
            }

            accum_diff = 0.0
            total_plan = 0.0
            total_frozen = 0.0
            total_demand_ids: set[str] = set()

            for d in sorted(info["dates"].keys()):
                cell = info["dates"][d]
                plan_qty = round(cell["plan_qty"], 2)
                frozen_qty = round(cell["frozen_qty"], 2)
                accum_diff += plan_qty - frozen_qty
                diff_qty = round(accum_diff, 2)

                total_plan += plan_qty
                total_frozen += frozen_qty
                total_demand_ids |= cell["demand_ids"]

                month_str, week_str = self._format_month_week(d)
                demand_ids_list = sorted(cell["demand_ids"])
                common = {
                    **base,
                    "date": d,
                    "month": month_str,
                    "week": week_str,
                    "demandIDs": demand_ids_list,
                }
                result_data.append({**common, "plan_type": "PLAN", "qty": plan_qty})
                result_data.append({**common, "plan_type": "FROZEN", "qty": frozen_qty})
                result_data.append({**common, "plan_type": "DIFF", "qty": diff_qty})

            # TOTAL 행 (원본 CalculateDiff 말미에 dateDict["TOTAL"] 생성)
            total_demand_list = sorted(total_demand_ids)
            total_common = {
                **base,
                "date": "TOTAL",
                "month": "",
                "week": "",
                "demandIDs": total_demand_list,
            }
            result_data.append({**total_common, "plan_type": "PLAN", "qty": round(total_plan, 2)})
            result_data.append({**total_common, "plan_type": "FROZEN", "qty": round(total_frozen, 2)})
            result_data.append({**total_common, "plan_type": "DIFF", "qty": round(accum_diff, 2)})

        act_start = plan_start_iso or self._get_plan_start_date(project_id, params.planVer)
        # 원본 GetActPeriod: endDate = _endDatetime.AddDays(-1)
        if plan_end_iso:
            try:
                end_obj = datetime.strptime(plan_end_iso, "%Y-%m-%d").date() - timedelta(days=1)
                act_end = str(end_obj)
            except ValueError:
                act_end = max_date
        else:
            act_end = max_date

        return {
            "success": True,
            "data": result_data,
            "demandData": demand_data,
            "actStartDate": act_start,
            "actEndDate": act_end,
            "frozenVer": frozen_ver,
        }


def get_re_execute_plan_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> ReExecutePlanService:
    return ReExecutePlanService(adapter)
