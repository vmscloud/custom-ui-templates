"""
BOM Map 서비스

RarBomMapViewNew C# 엔드포인트 포팅.
out_bom_network_info + rpt_demand_plan_isb + OUT_SHORT_LOG 테이블에서
BOM 네트워크 다이어그램 데이터를 조회합니다.
"""

from __future__ import annotations

import logging
import math
from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------

_DEMAND_SQL = """
SELECT demand_id, item_id, site_id, buffer_id, cust_id
FROM odv_demand
WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}' AND demand_id = '{demand_id}'
UNION ALL
SELECT demand_id, item_id, site_id, buffer_id, cust_id
FROM rpt_safety_stock_demand
WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}' AND demand_id = '{demand_id}'
"""

_BOM_NETWORK_SQL = """
WITH im AS (
    SELECT DISTINCT item_id, item_name, item_type
    FROM odv_item_master
    WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}'
),
sm AS (
    SELECT DISTINCT site_id, site_name
    FROM odv_site_master
    WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}'
),
obni AS (
    SELECT *
    FROM out_bom_network_info
    WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}'
      AND demand_buffer_id = '{buffer_id}' AND demand_item_id = '{item_id}'
      {site_filter}
)
SELECT
    a.depth AS index_x,
    a.bom_id, a.bom_type, a.routing_id, a.routing_tat,
    a.min_cum_tat AS to_min_cum_tat, a.max_cum_tat AS to_max_cum_tat,
    a.from_item_id, imf.item_name AS from_item_name, a.from_site_id, smf.site_name AS from_site_name,
    a.from_buffer_id, imf.item_type AS from_item_type, a.from_qty, a.from_buffer_seq,
    a.to_item_id, imt.item_name AS to_item_name, a.to_site_id, smt.site_name AS to_site_name,
    a.to_buffer_id, imt.item_type AS to_item_type, a.to_qty, a.to_buffer_seq
FROM obni a
LEFT JOIN im imf ON a.from_item_id = imf.item_id
LEFT JOIN sm smf ON a.from_site_id = smf.site_id
LEFT JOIN im imt ON a.to_item_id = imt.item_id
LEFT JOIN sm smt ON a.to_site_id = smt.site_id
ORDER BY a.depth
"""

_ISB_SQL = """
SELECT item_id, site_id, buffer_id,
       CAST(peg_qty AS DOUBLE) AS peg_qty,
       CAST(plan_qty AS DOUBLE) AS plan_qty,
       CAST(plan_unit_qty AS DOUBLE) AS plan_unit_qty,
       CAST(plan_datetime AS VARCHAR) AS plan_datetime,
       CAST(target_datetime AS VARCHAR) AS target_datetime,
       CAST(extend_target_datetime AS VARCHAR) AS extd_target_datetime,
       plan_gap_sec
FROM rpt_demand_plan_isb
WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}' AND demand_id = '{demand_id}'
"""

_BOM_PATH_LOG_SQL = """
SELECT item_id, site_id, buffer_id,
       CAST(peg_qty AS DOUBLE) AS peg_qty,
       CAST(plan_qty AS DOUBLE) AS plan_qty,
       CAST(plan_unit_qty AS DOUBLE) AS plan_unit_qty,
       CAST(plan_datetime AS VARCHAR) AS plan_datetime,
       CAST(target_datetime AS VARCHAR) AS target_datetime,
       CAST(extend_target_datetime AS VARCHAR) AS extd_target_datetime,
       plan_gap_sec
FROM rpt_demand_plan_isb
WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}' AND demand_id = '{demand_id}'
  AND target_datetime IS NOT NULL
"""

_SHORT_LOG_SQL = """
SELECT SHORT_TYPE AS short_type, SHORT_CATEGORY_TYPE AS short_category, SHORT_REASON AS short_reason,
       CEILING(SHORT_QTY * 100) / 100 AS short_qty, SHORT_DETAIL_INFO AS short_detail_info,
       REPLACE(ISB_ID, '@', '∥') AS isb_id, BOM_ID AS bom_id, ROUTING_ID AS routing_id,
       OPER_ID AS oper_id, RES_ID AS res_id
FROM OUT_SHORT_LOG
WHERE PARTITION_KEY = '{partition_key}' AND PLAN_VER = '{plan_ver}' AND DEMAND_ID = '{demand_id}'
"""


# ---------------------------------------------------------------------------
# BomMapService
# ---------------------------------------------------------------------------


class BomMapService:
    """BOM Map 비즈니스 로직 — RarBomMapViewNew C# 포팅"""

    def __init__(self, adapter: QueryExecutorAdapter):
        self.adapter = adapter
        self.catalog = settings.TRINO_CATALOG_ICEBERG
        self.schema = settings.TRINO_SCHEMA_APS

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    async def _trino(self, project_id: str, sql: str) -> dict[str, Any]:
        return await self.adapter.execute_direct_query(
            project_id=project_id,
            query=sql,
            catalog=self.catalog,
            schema=self.schema,
        )

    def _rows(self, result: dict[str, Any], label: str) -> list[dict]:
        if not result.get("success"):
            logger.warning(
                "[BomMap] %s query failed: %s",
                label,
                result.get("message", "unknown error"),
            )
            return []
        return result.get("row", [])

    def _partition_key(self, project_id: str, plan_ver: str) -> str:
        return f"{project_id}@{plan_ver[:6]}"

    # ------------------------------------------------------------------
    # Step 1: demand 기본 정보 조회
    # ------------------------------------------------------------------

    async def _get_demand_info(
        self, project_id: str, partition_key: str, plan_ver: str, demand_id: str
    ) -> dict | None:
        sql = _DEMAND_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            demand_id=demand_id,
        )
        rows = self._rows(await self._trino(project_id, sql), "demand")
        return rows[0] if rows else None

    # ------------------------------------------------------------------
    # Step 2: BOM 네트워크 조회
    # ------------------------------------------------------------------

    async def _get_bom_network(
        self,
        project_id: str,
        partition_key: str,
        plan_ver: str,
        item_id: str,
        buffer_id: str,
        site_id: str = "",
    ) -> list[dict]:
        site_filter = f"AND demand_site_id = '{site_id}'" if site_id else ""
        sql = _BOM_NETWORK_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            item_id=item_id,
            buffer_id=buffer_id,
            site_filter=site_filter,
        )
        return self._rows(await self._trino(project_id, sql), "bom_network")

    # ------------------------------------------------------------------
    # Step 3: ISB dict + BomPathLog
    # ------------------------------------------------------------------

    async def _get_isb_data(
        self, project_id: str, partition_key: str, plan_ver: str, demand_id: str
    ) -> tuple[dict[str, dict], list[dict]]:
        """Returns (isb_dict keyed by item@site@buffer, path_log_list)."""
        isb_rows = self._rows(
            await self._trino(
                project_id,
                _ISB_SQL.format(
                    partition_key=partition_key,
                    plan_ver=plan_ver,
                    demand_id=demand_id,
                ),
            ),
            "isb",
        )
        path_rows = self._rows(
            await self._trino(
                project_id,
                _BOM_PATH_LOG_SQL.format(
                    partition_key=partition_key,
                    plan_ver=plan_ver,
                    demand_id=demand_id,
                ),
            ),
            "bom_path_log",
        )

        isb_dict: dict[str, dict] = {}
        for r in isb_rows:
            key = f"{r.get('item_id')}@{r.get('site_id')}@{r.get('buffer_id')}"
            isb_dict[key] = r

        logger.info(f"[BomMap] ISB rows={len(isb_rows)}, path_log rows={len(path_rows)}, isb_dict keys={list(isb_dict.keys())[:5]}")

        return isb_dict, path_rows

    # ------------------------------------------------------------------
    # Step 3b: ISB 병합 + path_yn 설정
    # ------------------------------------------------------------------

    def _merge_isb_and_path(
        self,
        network: list[dict],
        isb_dict: dict[str, dict],
        path_log: list[dict],
    ) -> list[dict]:
        """네트워크 항목에 ISB peg/plan 수량 병합 및 경로 플래그 설정 (C# SetBomPathLog 동일)."""
        path_set: set[str] = {
            f"{r.get('item_id')}@{r.get('site_id')}@{r.get('buffer_id')}"
            for r in path_log
        }

        has_both_path = False
        has_to_path = False

        result: list[dict] = []
        for row in network:
            item = dict(row)

            from_key = f"{item.get('from_item_id')}@{item.get('from_site_id')}@{item.get('from_buffer_id')}"
            to_key = f"{item.get('to_item_id')}@{item.get('to_site_id')}@{item.get('to_buffer_id')}"

            from_isb = isb_dict.get(from_key, {})
            to_isb = isb_dict.get(to_key, {})

            # ISB 수량 병합
            for prefix, isb in [("from", from_isb), ("to", to_isb)]:
                item[f"{prefix}_peg_qty"] = isb.get("peg_qty")
                item[f"{prefix}_plan_qty"] = isb.get("plan_qty")
                item[f"{prefix}_plan_unit_qty"] = isb.get("plan_unit_qty")
                item[f"{prefix}_plan_datetime"] = isb.get("plan_datetime")
                item[f"{prefix}_target_datetime"] = isb.get("target_datetime")
                item[f"{prefix}_extd_target_datetime"] = isb.get("extd_target_datetime")
                item[f"{prefix}_plan_gap_sec"] = isb.get("plan_gap_sec")

            # C# SetBomPathLog: path_yn은 from+to 모두 매칭, to_path_yn은 나중에 설정
            from_in_path = from_key in path_set
            to_in_path = to_key in path_set

            item["path_yn"] = False
            item["to_path_yn"] = False

            if from_in_path and to_in_path:
                item["path_yn"] = True
                has_both_path = True
            elif to_in_path:
                has_to_path = True

            result.append(item)

        # C# 원본: 양쪽 매칭된 게 하나라도 있으면 path_yn만으로 필터 가능 → 그대로 반환
        if has_both_path:
            return result

        # 양쪽 매칭은 없고 to만 매칭된 게 있으면 → 첫 번째 항목에 to_path_yn 설정
        if has_to_path and result:
            result[0]["to_path_yn"] = True

        return result

    # ------------------------------------------------------------------
    # Step 4: Short logs
    # ------------------------------------------------------------------

    async def _get_short_logs(
        self, project_id: str, partition_key: str, plan_ver: str, demand_id: str
    ) -> list[dict]:
        sql = _SHORT_LOG_SQL.format(
            partition_key=partition_key,
            plan_ver=plan_ver,
            demand_id=demand_id,
        )
        rows = self._rows(await self._trino(project_id, sql), "short_log")

        result: list[dict] = []
        for r in rows:
            short_qty = r.get("short_qty")
            if short_qty is not None:
                try:
                    # CEILING to 2 decimal places (already done in SQL, but ensure float)
                    short_qty = float(short_qty)
                except (TypeError, ValueError):
                    short_qty = None

            result.append(
                {
                    "short_type": r.get("short_type"),
                    "short_category": r.get("short_category"),
                    "short_reason": r.get("short_reason"),
                    "short_qty": short_qty,
                    "short_detail_info": r.get("short_detail_info"),
                    "isb_id": r.get("isb_id"),
                    "bom_id": r.get("bom_id"),
                    "routing_id": r.get("routing_id"),
                    "oper_id": r.get("oper_id"),
                    "res_id": r.get("res_id"),
                }
            )
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_bom_map_view(
        self, project_id: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        RarBomMapViewNew 응답 구조 반환:
        {
            "bomNetworkInfos": [...],
            "demandInfos": {...},
            "shortLogs": [...]
        }

        params 키:
            planVer (str): 계획 버전
            demandID (str): 수요 ID
            onlyTargetBom (bool, optional): True이면 path_yn/to_path_yn 필터 적용
        """
        plan_ver: str = params.get("planVer", "")
        demand_id: str = params.get("demandID", "")
        only_target_bom: bool = bool(params.get("onlyTargetBom", False))

        if not plan_ver or not demand_id:
            logger.warning("[BomMap] planVer or demandID is missing")
            return {"bomNetworkInfos": [], "demandInfos": {}, "shortLogs": []}

        partition_key = self._partition_key(project_id, plan_ver)

        # Step 1: demand 기본 정보
        demand = await self._get_demand_info(
            project_id, partition_key, plan_ver, demand_id
        )
        if not demand:
            logger.warning(
                "[BomMap] demand not found: project=%s demand_id=%s", project_id, demand_id
            )
            return {"bomNetworkInfos": [], "demandInfos": {}, "shortLogs": []}

        item_id: str = demand.get("item_id", "")
        site_id: str = demand.get("site_id", "")
        buffer_id: str = demand.get("buffer_id", "")

        # Steps 2, 3, 4 — 병렬 실행 (독립 쿼리)
        import asyncio

        bom_task = asyncio.create_task(
            self._get_bom_network(project_id, partition_key, plan_ver, item_id, buffer_id, site_id)
        )
        isb_task = asyncio.create_task(
            self._get_isb_data(project_id, partition_key, plan_ver, demand_id)
        )
        short_task = asyncio.create_task(
            self._get_short_logs(project_id, partition_key, plan_ver, demand_id)
        )

        network, (isb_dict, path_log), short_logs = await asyncio.gather(
            bom_task, isb_task, short_task
        )

        # Step 3b: ISB 병합 + path 플래그
        bom_network_infos = self._merge_isb_and_path(network, isb_dict, path_log)

        # Step 6: onlyTargetBom 필터
        if only_target_bom:
            bom_network_infos = [
                item
                for item in bom_network_infos
                if item.get("path_yn") or item.get("to_path_yn")
            ]

        # Step 5: demand 요약 (demandInfos) — ISB의 첫 행에서 기본 정보 추출
        first_isb = next(iter(isb_dict.values()), {})
        demand_qty = float(first_isb.get("peg_qty") or 0)
        demand_infos = {
            "demand_id": demand.get("demand_id"),
            "item_id": item_id,
            "item_name": demand.get("item_name", item_id),
            "item_label": f"{item_id} / {demand.get('item_name', item_id)}",
            "site_id": demand.get("site_id"),
            "site_name": demand.get("site_name", demand.get("site_id")),
            "buffer_id": buffer_id,
            "cust_id": demand.get("cust_id"),
            "qty": demand_qty,
            "due_date": None,
            "extended_due_date": None,
            "priority": None,
            "max_earliness_day": 0,
            "max_lateness_day": 0,
            "rtf_ratio": 0,
            "rtf_qty": 0,
            "on_time_ratio": 0,
            "on_time_qty": 0,
            "late_ratio": 0,
            "late_qty": 0,
            "short_ratio": 0,
            "short_qty": 0,
        }

        return {
            "bomNetworkInfos": bom_network_infos,
            "demandInfos": demand_infos,
            "shortLogs": short_logs,
        }
