"""
부하율 (LoadFactor) 서비스

rpt_oper_group_target 테이블에서 공정 그룹별 부하율 데이터를 조회합니다.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from app.core.database import execute_query
from app.services import load_factor_queries as Q
from fastapi import Depends

logger = logging.getLogger(__name__)


class LoadFactorService:
    """부하율 비즈니스 로직"""

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
        if not result.get("success"):
            logger.warning(f"[LoadFactor] Trino query failed: {result.get('message', 'unknown error')}")
            return []
        return result.get("row", [])

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

    def _build_oper_group_filter(self, oper_group_ids: list[str]) -> str:
        if not oper_group_ids:
            return ""
        escaped = ", ".join(f"'{g}'" for g in oper_group_ids)
        return f"AND t.oper_group_id IN ({escaped})"

    async def _get_prop_keys(
        self, project_id: str, partition_key: str, plan_ver: str
    ) -> dict[str, str]:
        """odv_report_prop_config에서 prop_json 키 매핑 조회.

        Returns:
            dict with keys: capa_prop_key, uom_prop_key
            예: {"capa_prop_key": "PROP01", "uom_prop_key": "PROP02"}
        """
        defaults = {"capa_prop_key": "PROP01", "uom_prop_key": "PROP02"}
        try:
            sql = Q.PROP_CONFIG_SQL.format(
                partition_key=partition_key,
                plan_ver=plan_ver,
            )
            result = await self._trino(project_id, sql)
            rows = self._safe_rows(result)
            if not rows:
                logger.warning("[LoadFactor] prop config not found, using defaults")
                return defaults

            prop_json_str = rows[0].get("prop_json", "{}")
            prop_config = json.loads(prop_json_str) if isinstance(prop_json_str, str) else prop_json_str

            # prop_config 구조: {"PROP01": {"PropID": {"Value": "OperGroupCapa"}, ...}, ...}
            mapping = {}
            for key, val in prop_config.items():
                prop_id = val.get("PropID", {})
                display_name = prop_id.get("Value", "")
                if display_name == "OperGroupCapa":
                    mapping["capa_prop_key"] = key
                elif display_name == "OperGroupQtyUOM":
                    mapping["uom_prop_key"] = key

            return {
                "capa_prop_key": mapping.get("capa_prop_key", defaults["capa_prop_key"]),
                "uom_prop_key": mapping.get("uom_prop_key", defaults["uom_prop_key"]),
            }
        except Exception as e:
            logger.warning(f"[LoadFactor] prop config lookup failed: {e}, using defaults")
            return defaults

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
        prop_keys = await self._get_prop_keys(project_id, partition_key, params.planVer)
        sql = Q.MAIN_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            std_ts=std_ts,
            from_date=params.fromDate,
            to_date=params.toDate,
            oper_group_filter=oper_group_filter,
            **prop_keys,
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
        prop_keys = await self._get_prop_keys(project_id, partition_key, params.planVer)
        sql = Q.GROUP_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            std_ts=std_ts,
            from_date=params.fromDate,
            to_date=params.toDate,
            oper_group_filter=oper_group_filter,
            **prop_keys,
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
        prop_keys = await self._get_prop_keys(project_id, partition_key, params.planVer)
        sql = Q.DETAIL_SQL.format(
            partition_key=partition_key,
            plan_ver=params.planVer,
            std_ts=std_ts,
            from_date=params.fromDate,
            to_date=params.toDate,
            oper_group_filter=oper_group_filter,
            **prop_keys,
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
