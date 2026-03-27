"""
부하율 (LoadFactor) 서비스

rpt_oper_group_target 테이블에서 공정 그룹별 부하율 데이터를 조회합니다.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.core.database import execute_query
from app.services import load_factor_queries as Q
from fastapi import Depends


class LoadFactorService:
    """부하율 비즈니스 로직"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG
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
            "SELECT plan_start_datetime FROM cfg_plan_config WHERE project_id = %s AND plan_ver = %s LIMIT 1",
            (project_id, plan_ver),
        )
        if not rows:
            return "2000-01-01"
        start = rows[0].get("plan_start_datetime")
        if isinstance(start, datetime):
            return str(start.date())
        elif isinstance(start, date):
            return str(start)
        return str(start)[:10] if start else "2000-01-01"

    def _build_oper_group_filter(self, oper_group_ids: list[str]) -> str:
        if not oper_group_ids:
            return ""
        escaped = ", ".join(f"'{g}'" for g in oper_group_ids)
        return f"AND t.oper_group_id IN ({escaped})"

    async def get_oper_groups(
        self, project_id: str, plan_ver: str
    ) -> list[dict[str, Any]]:
        partition_key = self._partition_key(project_id, plan_ver)
        sql = Q.OPER_GROUPS_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
        )
        result = await self._trino(project_id, sql)
        return self._safe_rows(result)

    async def get_main(
        self, project_id: str, params
    ) -> dict[str, Any]:
        partition_key = self._partition_key(project_id, params.planVer)
        std_ts = self._get_plan_start_date(project_id, params.planVer)
        oper_group_filter = self._build_oper_group_filter(params.operGroupIDs)
        sql = Q.MAIN_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            std_ts=std_ts,
            from_date=params.fromDate,
            to_date=params.toDate,
            oper_group_filter=oper_group_filter,
        )
        result = await self._trino(project_id, sql)
        data = self._safe_rows(result)

        if not params.includeUndefinedCapa:
            data = [r for r in data if (r.get("capa") or 0) > 0]

        return {"success": True, "count": len(data), "data": data}

    async def get_group(
        self, project_id: str, params
    ) -> dict[str, Any]:
        partition_key = self._partition_key(project_id, params.planVer)
        std_ts = self._get_plan_start_date(project_id, params.planVer)
        oper_group_filter = self._build_oper_group_filter(params.operGroupIDs)
        sql = Q.GROUP_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            std_ts=std_ts,
            from_date=params.fromDate,
            to_date=params.toDate,
            oper_group_filter=oper_group_filter,
        )
        result = await self._trino(project_id, sql)
        data = self._safe_rows(result)
        data = self._gap_fill_group(data, params.fromDate, params.toDate)
        return {"success": True, "count": len(data), "data": data}

    def _gap_fill_group(
        self, data: list[dict], from_date: str, to_date: str
    ) -> list[dict]:
        if not data:
            return data

        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
        all_dates = set()
        cur = start
        while cur <= end:
            all_dates.add(str(cur))
            cur += timedelta(days=1)

        existing_keys: set[tuple[str, str]] = set()
        oper_groups: set[str] = set()
        default_capa = 0.0
        for row in data:
            oper_group_id = row.get("oper_group_id", "")
            d = row.get("date", "")
            existing_keys.add((oper_group_id, d))
            oper_groups.add(oper_group_id)
            if default_capa == 0 and row.get("capa"):
                default_capa = float(row["capa"])

        fill_rows: list[dict] = []
        for oper_group_id in oper_groups:
            for d in sorted(all_dates):
                if (oper_group_id, d) not in existing_keys:
                    fill_rows.append({
                        "oper_group_id": oper_group_id,
                        "item_group_id": "TOTAL",
                        "date": d,
                        "plan_qty": 0.0,
                        "capa": default_capa,
                        "str_rate": 0.0,
                        "base_line": 100,
                        "sort_order": 0,
                    })

        if fill_rows:
            data = data + fill_rows
            data.sort(key=lambda r: (r.get("date", ""), r.get("sort_order", 1), r.get("item_group_id", "")))

        return data

    async def get_detail(
        self, project_id: str, params
    ) -> dict[str, Any]:
        partition_key = self._partition_key(project_id, params.planVer)
        std_ts = self._get_plan_start_date(project_id, params.planVer)
        oper_group_filter = self._build_oper_group_filter(params.operGroupIDs)
        sql = Q.DETAIL_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            std_ts=std_ts,
            from_date=params.fromDate,
            to_date=params.toDate,
            oper_group_filter=oper_group_filter,
        )
        result = await self._trino(project_id, sql)
        data = self._safe_rows(result)

        if not params.includeUndefinedCapa:
            data = [r for r in data if (r.get("capa") or 0) > 0]

        return {"success": True, "count": len(data), "data": data}


def get_load_factor_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> LoadFactorService:
    return LoadFactorService(adapter)
