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

    async def get_main(
        self, project_id: str, params
    ) -> dict[str, Any]:
        """메인 데이터 조회 - 피벗 데이터 + 수요 목록 병렬 실행"""
        partition_key = self._partition_key(project_id, params.planVer)
        qty_col = "out_plan_conv_qty" if params.uomType == "CONVERSION" else "out_plan_qty"

        demand_type_filter = self._build_filter("demand_type", params.demandTypes)
        item_group_filter = self._build_filter("item_group_id", params.itemGroupIDs)
        customer_filter = self._build_filter("cust_id", params.customers)

        # 피벗 SQL 구성
        if params.summaryType == "BUFFER":
            buffer_filter = self._build_filter("buffer_id", params.bufferIDs)
            pivot_sql = Q.PIVOT_BUFFER_SQL.format(
                partition_key=partition_key,
                plan_ver=params.planVer,
                qty_col=qty_col,
                buffer_filter=buffer_filter,
                customer_filter=customer_filter,
                demand_type_filter=demand_type_filter,
                item_group_filter=item_group_filter,
            )
        else:
            # OPERGROUP (default)
            oper_group_filter = self._build_filter("oper_group_id", params.operGroupIDs)
            oper_filter = self._build_filter("oper_id", params.operIDs)
            pivot_sql = Q.PIVOT_OPER_GROUP_SQL.format(
                partition_key=partition_key,
                plan_ver=params.planVer,
                qty_col=qty_col,
                oper_group_filter=oper_group_filter,
                oper_filter=oper_filter,
                demand_type_filter=demand_type_filter,
                item_group_filter=item_group_filter,
            )

        # 수요 목록 SQL 구성
        demand_sql = Q.DEMAND_LIST_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            demand_type_filter=demand_type_filter,
            customer_filter=customer_filter,
        )

        # 피벗 데이터 + 수요 목록 병렬 실행
        pivot_result, demand_result = await asyncio.gather(
            self._trino(project_id, pivot_sql),
            self._trino(project_id, demand_sql),
        )

        pivot_data = self._safe_rows(pivot_result)
        demand_data = self._safe_rows(demand_result)

        return {
            "success": True,
            "pivotData": pivot_data,
            "demandData": demand_data,
        }


def get_re_execute_plan_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> ReExecutePlanService:
    return ReExecutePlanService(adapter)
