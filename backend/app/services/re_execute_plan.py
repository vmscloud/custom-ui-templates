"""
재실행 계획 (ReExecutePlan) 서비스

rpt_oper_group_plan, rpt_buffer_plan 테이블에서 재실행 계획 데이터를 조회합니다.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.core.database import execute_query
from app.services import re_execute_plan_queries as Q
from fastapi import Depends


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

    def _safe_rows(self, result: dict[str, Any]) -> list[dict]:
        return result.get("row", []) if result.get("success") else []

    def _partition_key(self, project_id: str, plan_ver: str) -> str:
        return f"{project_id}@{plan_ver[:6]}"

    def _get_plan_start_date(self, project_id: str, plan_ver: str) -> str:
        """PostgreSQL에서 plan_start_datetime 조회"""
        rows = execute_query(
            f"SELECT plan_start_datetime FROM cfg_plan_config WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1",
        )
        if not rows:
            return "2000-01-01"
        start = rows[0].get("plan_start_datetime")
        if isinstance(start, datetime):
            return str(start.date())
        elif isinstance(start, date):
            return str(start)
        return str(start)[:10] if start else "2000-01-01"

    def _build_filter(self, field: str, values: list) -> str:
        """범용 IN 필터 빌더 (null 값 자동 제거)"""
        filtered = [v for v in values if v is not None and v != ""]
        if not filtered:
            return ""
        escaped = ", ".join(f"'{v}'" for v in filtered)
        return f"AND {field} IN ({escaped})"

    async def get_regions(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """지역 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.REGIONS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_oper_groups(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """공정 그룹 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.OPER_GROUPS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_buffers(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """버퍼 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.BUFFERS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_opers(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """공정 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.OPERS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_customers(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """고객 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.CUSTOMERS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_item_groups(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """품목그룹 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.ITEM_GROUPS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_demand_types(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        """수요유형 목록 조회"""
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.DEMAND_TYPES_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    def _get_frozen_ver(self, project_id: str, plan_ver: str) -> str:
        """
        frozen version 조회 — C# GetFrozenPlanVer 포팅.
        같은 plan_cycle 내에서 FROZEN 상태의 plan_ver를 찾는다.
        없으면 cfg_plan_cycle_info.frozen_plan_ver 폴백.
        """
        try:
            # Step 1: plan_cycle_id 조회
            cycle_rows = execute_query(
                f"SELECT plan_cycle_id FROM cfg_plan_config WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1"
            )
            if not cycle_rows:
                return plan_ver
            plan_cycle_id = cycle_rows[0].get("plan_cycle_id", "")

            # Step 2: 같은 cycle 내 FROZEN 상태 plan_ver 조회 (C# Select_PlanVerInPlanCycle)
            frozen_rows = execute_query(
                f"""SELECT plan_ver FROM cfg_plan_config
                    WHERE project_id = '{project_id}'
                      AND plan_cycle_id = '{plan_cycle_id}'
                      AND plan_status = 'FROZEN'
                    ORDER BY plan_ver DESC LIMIT 1"""
            )
            if frozen_rows and frozen_rows[0].get("plan_ver"):
                return frozen_rows[0]["plan_ver"]

            # Step 3: 폴백 — frozen_plan_ver 컬럼
            fallback_rows = execute_query(
                f"""SELECT frozen_plan_ver FROM cfg_plan_cycle_info
                    WHERE project_id = '{project_id}' AND plan_cycle_id = '{plan_cycle_id}'
                    LIMIT 1"""
            )
            if fallback_rows and fallback_rows[0].get("frozen_plan_ver"):
                return fallback_rows[0]["frozen_plan_ver"]
        except Exception:
            pass
        return plan_ver

    def _get_cycle_dates(self, project_id: str, plan_ver: str) -> tuple[str, str]:
        """plan cycle start/end 조회 (C# SetPlanStartEndDate)"""
        try:
            rows = execute_query(
                f"""SELECT c.plan_start_datetime, c.plan_period,
                           ci.start_datetime AS cycle_start, ci.end_datetime AS cycle_end
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
        # fallback
        return plan_ver[:4] + "-" + plan_ver[4:6] + "-01", plan_ver[:4] + "-" + plan_ver[4:6] + "-30"

    def _build_pivot_sql(self, partition_key: str, plan_ver: str, params, qty_col: str, start_date: str, end_date: str) -> str:
        """summaryType에 따라 피벗 SQL 생성"""
        demand_type_filter = self._build_filter("demand_type", params.demandTypes)
        item_group_filter = self._build_filter("item_group_id", params.itemGroupIDs)
        customer_filter = self._build_filter("cust_id", params.customers)

        if params.summaryType == "BUFFER":
            buffer_filter = self._build_filter("std_buffer_id", params.bufferIDs)
            return Q.PIVOT_BUFFER_SQL.format(
                partition_key=partition_key, plan_ver=plan_ver, qty_col=qty_col,
                start_date=start_date, end_date=end_date,
                buffer_filter=buffer_filter, customer_filter=customer_filter,
                demand_type_filter=demand_type_filter, item_group_filter=item_group_filter,
            )
        else:
            oper_group_filter = self._build_filter("oper_group_id", params.operGroupIDs)
            oper_filter = self._build_filter("oper_id", params.operIDs)
            return Q.PIVOT_OPER_GROUP_SQL.format(
                partition_key=partition_key, plan_ver=plan_ver, qty_col=qty_col,
                start_date=start_date, end_date=end_date,
                oper_group_filter=oper_group_filter, oper_filter=oper_filter,
                demand_type_filter=demand_type_filter, item_group_filter=item_group_filter,
            )

    async def get_main(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """
        메인 데이터 조회 — C# GetReExecutePlanDatas 포팅.
        1. plan + frozen 데이터 병렬 조회
        2. 날짜별 merge
        3. FillEmptyCell (빈 날짜 채우기)
        4. CalculateDiff (누적 차이 계산)
        5. plan/frozen/diff 3종 flat list 반환
        """
        partition_key = self._partition_key(project_id, params.planVer)
        qty_col = "out_plan_conv_qty" if params.uomType == "CONVERSION" else "out_plan_qty"

        # Frozen version + cycle dates 조회
        frozen_ver = self._get_frozen_ver(project_id, params.planVer)
        frozen_pk = self._partition_key(project_id, frozen_ver)
        cycle_start, cycle_end = self._get_cycle_dates(project_id, params.planVer)

        # Plan + Frozen + Demand 병렬 조회
        plan_sql = self._build_pivot_sql(partition_key, params.planVer, params, qty_col, cycle_start, cycle_end)
        frozen_sql = self._build_pivot_sql(frozen_pk, frozen_ver, params, qty_col, cycle_start, cycle_end)

        demand_type_filter = self._build_filter("demand_type", params.demandTypes)
        customer_filter = self._build_filter("cust_id", params.customers)
        demand_sql = Q.DEMAND_LIST_SQL.format(
            partition_key=partition_key, plan_ver=params.planVer,
            demand_type_filter=demand_type_filter, customer_filter=customer_filter,
        )

        plan_result, frozen_result, demand_result = await asyncio.gather(
            self._trino(project_id, plan_sql),
            self._trino(project_id, frozen_sql),
            self._trino(project_id, demand_sql),
        )

        plan_rows = self._safe_rows(plan_result)
        frozen_rows = self._safe_rows(frozen_result)
        demand_data = self._safe_rows(demand_result)

        # 그룹 키 결정 — C# 원본: summaryType(OPER/BUFFER) + aggregateType(itemGroup/cust/region/demandType)
        group_key = "oper_group_id" if params.summaryType != "BUFFER" else "buffer_id"
        # aggregateType에 따른 추가 집계 키 (C# _aggrColumn)
        aggr_key_map = {
            "itemGroup": "item_group_id",
            "cust": "cust_id",
            "region": "region",
            "demandType": "demand_type",
        }
        aggr_key = aggr_key_map.get(getattr(params, "aggregateType", ""), "")

        # Plan/Frozen 데이터를 (group, date) dict로 merge
        data_dict: dict[str, dict[str, dict]] = {}  # {group_key: {date: {plan_qty, frozen_qty}}}
        min_date_str = "9999-99-99"
        max_date_str = "0000-00-00"

        def _make_composite_key(row: dict) -> str:
            """그룹 키 + 집계 키 조합"""
            parts = [row.get(group_key, "")]
            if aggr_key:
                parts.append(row.get(aggr_key, ""))
            return "|".join(parts)

        def _parse_composite_key(ck: str) -> dict:
            """composite key → 필드 dict"""
            parts = ck.split("|")
            result = {group_key: parts[0]}
            if aggr_key and len(parts) > 1:
                result["aggr_value"] = parts[1]
            return result

        for row in plan_rows:
            ck = _make_composite_key(row)
            d = (row.get("date") or "")[:10]
            if not d:
                continue
            if d < min_date_str:
                min_date_str = d
            if d > max_date_str:
                max_date_str = d
            if ck not in data_dict:
                data_dict[ck] = {}
            if d not in data_dict[ck]:
                data_dict[ck][d] = {"plan_qty": 0.0, "frozen_qty": 0.0}
            data_dict[ck][d]["plan_qty"] += float(row.get("qty") or 0)

        for row in frozen_rows:
            ck = _make_composite_key(row)
            d = (row.get("date") or "")[:10]
            if not d:
                continue
            if d < min_date_str:
                min_date_str = d
            if d > max_date_str:
                max_date_str = d
            if ck not in data_dict:
                data_dict[ck] = {}
            if d not in data_dict[ck]:
                data_dict[ck][d] = {"plan_qty": 0.0, "frozen_qty": 0.0}
            data_dict[ck][d]["frozen_qty"] += float(row.get("qty") or 0)

        # FillEmptyCell: min~max 사이 빈 날짜 채우기
        if min_date_str <= max_date_str:
            from datetime import timedelta
            try:
                min_dt = datetime.strptime(min_date_str, "%Y-%m-%d")
                max_dt = datetime.strptime(max_date_str, "%Y-%m-%d")
                for ck in data_dict:
                    dt = min_dt
                    while dt <= max_dt:
                        ds = dt.strftime("%Y-%m-%d")
                        if ds not in data_dict[ck]:
                            data_dict[ck][ds] = {"plan_qty": 0.0, "frozen_qty": 0.0}
                        dt += timedelta(days=1)
            except ValueError:
                pass

        # CalculateDiff: 누적 차이 계산 + flat list 생성
        result_data: list[dict] = []
        for ck, date_dict in data_dict.items():
            accum_diff = 0.0
            key_fields = _parse_composite_key(ck)
            for d in sorted(date_dict.keys()):
                if d == "TOTAL":
                    continue
                item = date_dict[d]
                plan_qty = round(item["plan_qty"], 2)
                frozen_qty = round(item["frozen_qty"], 2)
                accum_diff += plan_qty - frozen_qty

                base = {**key_fields, "date": d}
                result_data.append({**base, "plan_type": "PLAN", "qty": plan_qty})
                result_data.append({**base, "plan_type": "FROZEN", "qty": frozen_qty})
                result_data.append({**base, "plan_type": "DIFF", "qty": round(accum_diff, 2)})

        # actPeriod
        act_start = self._get_plan_start_date(project_id, params.planVer)

        return {
            "success": True,
            "data": result_data,
            "demandData": demand_data,
            "actStartDate": act_start,
            "actEndDate": max_date_str if max_date_str != "0000-00-00" else "",
            "frozenVer": frozen_ver,
        }


def get_re_execute_plan_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> ReExecutePlanService:
    return ReExecutePlanService(adapter)
