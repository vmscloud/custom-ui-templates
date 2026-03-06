"""
RTF Report 레포지토리 (Trino SQL)

원본 APS C# 백엔드의 RTF Report SQL을 Trino 호환으로 변환
"""

from app.core.database import execute_query


class RtfReportRepository:
    """RTF Report 데이터 접근"""

    @staticmethod
    def _partition_key(project_id: str, plan_ver: str) -> str:
        """partition_key 생성: project_id@YYYYMM (plan_ver 앞 6자리)"""
        return f"{project_id}@{plan_ver[:6]}"

    # ── Prop ID 조회 ──

    @staticmethod
    def get_prop_ids(project_id: str, plan_ver: str) -> dict:
        """
        odv_report_prop_config에서 productionAreaPropID, prodTypePropID 조회
        """
        query = """
        SELECT prop_id, prop_type
        FROM odv_report_prop_config
        WHERE partition_key = ?
          AND plan_ver = ?
          AND prop_type IN ('PRODUCTION_AREA', 'PROD_TYPE')
        """
        try:
            rows = execute_query(query, (project_id, plan_ver))
        except Exception:
            return {}

        result = {}
        for row in rows:
            if row.get("prop_type") == "PRODUCTION_AREA":
                result["productionAreaPropID"] = row["prop_id"]
            elif row.get("prop_type") == "PROD_TYPE":
                result["prodTypePropID"] = row["prop_id"]
        return result

    # ── 필터 쿼리 ──

    @staticmethod
    def get_customers(project_id: str, plan_ver: str) -> list[dict]:
        """ComCustInRtf — 고객 필터 목록"""
        query = """
        SELECT DISTINCT
            a.cust_id,
            b.cust_name,
            b.cust_priority,
            CONCAT(a.cust_id, ' / ',
                CASE WHEN COALESCE(b.cust_name, '') = ''
                     THEN a.cust_id ELSE b.cust_name END
            ) AS cust_label
        FROM rpt_shipment_plan a
        LEFT OUTER JOIN odv_cust_master b
            ON a.partition_key = b.partition_key
            AND a.cust_id = b.cust_id
            AND a.plan_ver = b.plan_ver
        WHERE a.partition_key = ?
          AND a.plan_ver = ?
          AND (a.demand_type != 'SafetyStock' OR a.demand_type IS NULL)
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_item_groups(project_id: str, plan_ver: str) -> list[dict]:
        """ComItemGroupInRtf — 품목그룹 필터 목록"""
        query = """
        SELECT DISTINCT
            item_group_id AS item_group
        FROM rpt_shipment_plan
        WHERE partition_key = ?
          AND plan_ver = ?
          AND (demand_type != 'SafetyStock' OR demand_type IS NULL)
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_regions(
        project_id: str, plan_ver: str, prop_id: str | None = None
    ) -> list[dict]:
        """RarRtfReport/GetRegions — 지역(생산영역) 필터 목록"""
        if not prop_id:
            return []

        # prop_id는 DB에서 조회한 내부 값이므로 안전하게 SQL에 삽입
        query = f"""
        SELECT DISTINCT
            json_extract_scalar(prop_json, '$.{prop_id}') AS value
        FROM rpt_shipment_plan
        WHERE partition_key = ?
          AND plan_ver = ?
          AND json_extract_scalar(prop_json, '$.{prop_id}') IS NOT NULL
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_demand_types(project_id: str, plan_ver: str) -> list[dict]:
        """RarRtfReport/GetDemandTypes — 수요유형 필터 목록"""
        query = """
        SELECT DISTINCT rsp.demand_type AS value
        FROM rpt_shipment_plan rsp
        INNER JOIN odv_demand d
            ON d.partition_key = rsp.partition_key
            AND d.plan_ver = rsp.plan_ver
            AND d.demand_id = rsp.demand_id
        WHERE rsp.partition_key = ?
          AND rsp.plan_ver = ?
          AND rsp.demand_type IS NOT NULL
        ORDER BY 1
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_prod_types(
        project_id: str, plan_ver: str, prop_id: str | None = None
    ) -> list[dict]:
        """ProdType 필터 목록"""
        if not prop_id:
            return []

        query = f"""
        SELECT DISTINCT
            json_extract_scalar(prop_json, '$.{prop_id}') AS value
        FROM rpt_shipment_plan
        WHERE partition_key = ?
          AND plan_ver = ?
          AND json_extract_scalar(prop_json, '$.{prop_id}') IS NOT NULL
        ORDER BY 1
        """
        return execute_query(query, (project_id, plan_ver))

    # ── 메인 데이터 쿼리 (원본 C# SQL 완전 일치) ──

    @staticmethod
    def get_raw_shipment_plans(
        project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """
        원본 C# RarRtfReport_Select_P_Cmd1.sql 완전 재현.

        C# 백엔드는 raw 행을 가져와 메모리에서 처리하므로,
        SQL에서 ratio 계산을 하지 않고 원시 데이터를 반환합니다.
        """
        uom_type = params.get("uomType", "DEFAULT")
        customers = params.get("customers")
        item_group_ids = params.get("itemGroupIDs")
        production_area = params.get("productionArea")
        prod_types = params.get("prodTypes")
        from_date = params.get("fromDate")
        to_date = params.get("toDate")
        demand_id = params.get("demandID")

        # Prop IDs 조회
        prop_ids = RtfReportRepository.get_prop_ids(project_id, plan_ver)
        pa_prop_id = prop_ids.get("productionAreaPropID")
        pt_prop_id = prop_ids.get("prodTypePropID")

        # 수량 컬럼 (uomType 조건) — 원본 C# SQL 완전 일치
        if uom_type == "CONVERSION":
            qty_cols = """
                rsp.DEMAND_CONV_QTY AS "demandQty",
                rsp.SHIPMENT_CONV_QTY AS "shipmentQty",
                rsp.ONTIME_CONV_QTY AS "onTimeQty",
                rsp.LATE_CONV_QTY AS "lateQty",
                rsp.CONV_QTY_UOM AS "qtyUom",
                rsp.CONV_QTY AS qty,
            """
        else:
            qty_cols = """
                rsp.DEMAND_QTY AS "demandQty",
                rsp.SHIPMENT_QTY AS "shipmentQty",
                rsp.ONTIME_PLAN_QTY AS "onTimeQty",
                rsp.LATE_QTY AS "lateQty",
                rsp.QTY_UOM AS "qtyUom",
                rsp.QTY AS qty,
            """

        # Prop 컬럼 (선택적)
        prop_select = ""
        if pa_prop_id:
            prop_select += f"""
                json_extract_scalar(rsp.prop_json, '$.{pa_prop_id}') AS production_area,
            """
        if pt_prop_id:
            prop_select += f"""
                json_extract_scalar(rsp.prop_json, '$.{pt_prop_id}') AS prod_type,
            """

        sql_params: list = [project_id, plan_ver]

        inner_where = ""
        if demand_id:
            inner_where += "\n          AND rsp.demand_id = ?"
            sql_params.append(demand_id)
        if from_date:
            inner_where += "\n          AND CAST(? AS DATE) <= CAST(rsp.due_date AS DATE)"
            sql_params.append(from_date)
        if to_date:
            inner_where += "\n          AND CAST(? AS DATE) > CAST(rsp.due_date AS DATE)"
            sql_params.append(to_date)

        # 원본 C# SQL: raw dueDate (yyyyMMdd), dueWeek/dueMonth에 '-' 삽입,
        # ratio 계산 없음, warehouse_status/shipment_status 포함
        query = f"""
        SELECT a.*
        FROM (
            SELECT
                rsp.STAGE_ID AS "stageID",
                rsp.DEMAND_ID AS "demandID",
                rsp.SHIPMENT_DATE AS "shipmentDate",
                {qty_cols}
                rsp.ITEM_ID AS "itemID",
                rsp.ITEM_NAME AS "itemName",
                rsp.ITEM_GROUP_ID AS "itemGroupID",
                CONCAT(rsp.item_id, ' / ',
                    CASE WHEN COALESCE(rsp.item_name, '') = ''
                         THEN rsp.item_id ELSE rsp.item_name END
                ) AS item_label,
                rsp.SITE_ID AS "siteID",
                rsp.SITE_NAME AS "siteName",
                rsp.BUFFER_ID AS "bufferID",
                rsp.CUST_ID AS "custID",
                rsp.DUE_DATE AS "dueDate",
                CONCAT(SUBSTR(rsp.DUE_WEEK, 1, 4), '-', SUBSTR(rsp.DUE_WEEK, 5)) AS "dueWeek",
                CONCAT(SUBSTR(rsp.DUE_MONTH, 1, 4), '-', SUBSTR(rsp.DUE_MONTH, 5)) AS "dueMonth",
                rsp.MAX_EARLINESS_DAY AS "maxEarlinessDay",
                rsp.MAX_LATENESS_DAY AS "maxLatenessDay",
                rsp.DEMAND_TYPE,
                rsp.DEMAND_PRIORITY,
                rsp.ITEM_TYPE,
                rsp.PROD_TYPE,
                rsp.ITEM_SIZE_TYPE,
                rsp.ITEM_SPEC,
                {prop_select}
                rsp.WAREHOUSE_STATUS,
                rsp.SHIPMENT_STATUS,
                rsp.QTY AS "raw_qty",
                rsp.CONV_QTY AS "raw_conv_qty",
                rsp.prop_json AS "prop_json"
            FROM rpt_shipment_plan rsp
            INNER JOIN odv_demand d
                ON d.partition_key = rsp.partition_key
                AND d.plan_ver = rsp.plan_ver
                AND d.demand_id = rsp.demand_id
            WHERE rsp.partition_key = ?
              AND rsp.plan_ver = ?
              {inner_where}
              AND (rsp.DEMAND_TYPE != 'SafetyStock' OR rsp.DEMAND_TYPE IS NULL)
        ) a
        WHERE 1 = 1
        """

        # 외부 필터 (동적)
        outer_where = ""
        if production_area and pa_prop_id:
            outer_where += "\n        AND production_area = ?"
            sql_params.append(production_area)
        if item_group_ids and len(item_group_ids) > 0:
            placeholders = ", ".join(["?"] * len(item_group_ids))
            outer_where += f'\n        AND "itemGroupID" IN ({placeholders})'
            sql_params.extend(item_group_ids)
        if customers and len(customers) > 0:
            placeholders = ", ".join(["?"] * len(customers))
            outer_where += f'\n        AND "custID" IN ({placeholders})'
            sql_params.extend(customers)
        if prod_types and pt_prop_id and len(prod_types) > 0:
            placeholders = ", ".join(["?"] * len(prod_types))
            outer_where += f"\n        AND prod_type IN ({placeholders})"
            sql_params.extend(prod_types)

        query += outer_where

        return execute_query(query, tuple(sql_params))

    @staticmethod
    def get_short(
        project_id: str,
        plan_ver: str,
        demand_id: str,
        uom_type: str = "DEFAULT",
    ) -> list[dict]:
        """RarRtfReport/Short — 부족 사유"""
        if uom_type == "CONVERSION":
            qty_cols = """
            SHORT_CONV_QTY AS "shortQty",
            CONV_QTY_UOM AS "qtyUom",
            CONV_UNIT_QTY_UOM AS "unitQtyUom",
            """
        else:
            qty_cols = """
            SHORT_QTY AS "shortQty",
            QTY_UOM AS "qtyUom",
            UNIT_QTY_UOM AS "unitQtyUom",
            """

        query = f"""
        SELECT
            SHORT_TYPE AS "shortType",
            SHORT_CATEGORY_TYPE AS "shortCategory",
            SHORT_REASON AS "shortReason",
            {qty_cols}
            SHORT_DETAIL_INFO AS "shortDetailInfo",
            ISB_ID AS "isbID",
            BOM_ID AS "bomID",
            ROUTING_ID AS "routingID",
            OPER_ID AS "operID",
            RES_ID AS "resID"
        FROM out_short_log
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id = ?
        """
        return execute_query(query, (project_id, plan_ver, demand_id))

    @staticmethod
    def get_plan_end_date(partition_key: str, plan_ver: str) -> list[dict]:
        """RarRtfReport/PlanEndDate — 계획 종료일"""
        # cfg_plan_config는 postgresql 카탈로그이며 project_id를 사용
        orig_project_id = partition_key.split("@")[0] if "@" in partition_key else partition_key
        query = """
        SELECT
            CAST(date_add('day', plan_period,
                 plan_start_datetime) AS DATE) AS plan_end_date
        FROM postgresql.mzc_aps.cfg_plan_config
        WHERE project_id = ?
          AND plan_ver = ?
        """
        return execute_query(query, (orig_project_id, plan_ver))

    # ══════════════════════════════════════════════════════════
    # Phase 2: 신규 API 엔드포인트
    # ══════════════════════════════════════════════════════════

    # ── RarPeggingReport/DemandInfo ──

    @staticmethod
    def get_demand_info(
        project_id: str, plan_ver: str, demand_id: str
    ) -> list[dict]:
        """
        RarPeggingReport/DemandInfo — 수요 기본 정보 + 생산수량 합계

        원본: RarPeggingDemandInfo_Select_P_Cmd1.sql
        """
        query = """
        WITH demand AS (
            SELECT A.partition_key
                 , A.plan_ver
                 , demand_id
                 , A.item_id
                 , A.item_id AS demand_item_id
                 , B.item_name AS demand_item_name
                 , site_id
                 , buffer_id
                 , CONCAT(due_date, ' (-',
                     CAST(max_earliness_day AS VARCHAR), ',+',
                     CAST(max_lateness_day AS VARCHAR), ')'
                   ) AS due_date
                 , demand_qty
            FROM odv_demand A
            INNER JOIN odv_item_master B
                ON A.partition_key = B.partition_key
                AND A.plan_ver = B.plan_ver
                AND A.item_id = B.item_id
            WHERE A.partition_key = ?
              AND A.plan_ver = ?
              AND A.demand_id = ?
        ),
        shipment_plan AS (
            SELECT partition_key, plan_ver, demand_id,
                   SUM(shipment_qty) AS prod_qty
            FROM rpt_shipment_plan
            WHERE partition_key = ?
              AND plan_ver = ?
              AND demand_id = ?
            GROUP BY 1, 2, 3
        )
        SELECT a.partition_key
             , a.plan_ver
             , a.demand_id
             , a.demand_item_id
             , a.demand_item_name
             , a.item_id
             , a.site_id
             , a.buffer_id
             , COALESCE(b.prod_qty, 0) AS prod_qty
             , a.demand_qty
             , a.due_date
        FROM demand a
        LEFT OUTER JOIN shipment_plan b
            ON a.partition_key = b.partition_key
            AND a.plan_ver = b.plan_ver
            AND a.demand_id = b.demand_id
        """
        return execute_query(
            query,
            (project_id, plan_ver, demand_id,
             project_id, plan_ver, demand_id),
        )

    # ── RarPeggingReport/PegInfoDetail ──

    @staticmethod
    def get_peg_info_detail(
        project_id: str,
        plan_ver: str,
        demand_id: str,
        uom_type: str = "DEFAULT",
    ) -> list[dict]:
        """
        RarPeggingReport/PegInfoDetail — Peg 상세 (buffer별 집계)

        원본: RarPeggingReportPegInfo_Select_P_Cmd1.sql
        uomType에 따라 wip_qty/peg_qty 또는 conv 버전 선택
        """
        if uom_type == "CONVERSION":
            qty_cols = """
                SUM(a.wip_conv_qty) AS wip_qty,
                SUM(a.peg_conv_qty) AS peg_qty,
                MAX(a.conv_qty_uom) AS qty_uom,
            """
        else:
            qty_cols = """
                SUM(a.wip_qty) AS wip_qty,
                SUM(a.peg_qty) AS peg_qty,
                MAX(a.qty_uom) AS qty_uom,
            """

        query = f"""
        SELECT a.demand_id
             , a.demand_item_id
             , a.item_id
             , a.site_id
             , a.buffer_id
             , b.buffer_seq
             , {qty_cols}
               c.item_name
        FROM out_peg_info a
        INNER JOIN odv_buffer_master b
            ON a.partition_key = b.partition_key
            AND a.plan_ver = b.plan_ver
            AND a.buffer_id = b.buffer_id
        INNER JOIN odv_item_master c
            ON a.partition_key = c.partition_key
            AND a.plan_ver = c.plan_ver
            AND a.item_id = c.item_id
        WHERE a.partition_key = ?
          AND a.plan_ver = ?
          AND a.demand_id = ?
        GROUP BY a.demand_id, a.demand_item_id, a.item_id,
                 a.site_id, a.buffer_id, b.buffer_seq, c.item_name
        ORDER BY a.demand_id, b.buffer_seq DESC, a.item_id
        """
        return execute_query(query, (project_id, plan_ver, demand_id))

    # ── RarPlanByProd/Detail2 helper queries ──
    # C# RarPlanDetailProcessor 완전 재현을 위한 개별 쿼리들

    @staticmethod
    def get_demands(
        project_id: str, plan_ver: str, demand_id: str
    ) -> list[dict]:
        """C# GetDemands — odv_demand + rpt_safety_stock_demand"""
        query = """
        SELECT demand_id, item_id, site_id, buffer_id, due_date
        FROM odv_demand
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id = ?
        UNION ALL
        SELECT demand_id, item_id, site_id, buffer_id,
               CAST(due_datetime AS VARCHAR) AS due_date
        FROM rpt_safety_stock_demand
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id = ?
        """
        return execute_query(
            query,
            (project_id, plan_ver, demand_id,
             project_id, plan_ver, demand_id),
        )

    @staticmethod
    def get_bom_network(
        project_id: str, plan_ver: str,
        item_id: str, site_id: str, buffer_id: str,
    ) -> list[dict]:
        """C# SetBomNetworkList — out_bom_network_info"""
        query = """
        SELECT from_item_id, from_site_id, from_buffer_id,
               to_item_id, to_site_id, to_buffer_id,
               routing_id
        FROM out_bom_network_info
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_item_id = ?
          AND demand_site_id = ?
          AND demand_buffer_id = ?
        """
        return execute_query(
            query, (project_id, plan_ver, item_id, site_id, buffer_id)
        )

    @staticmethod
    def get_routing_opers(
        project_id: str, plan_ver: str, routing_ids: list[str]
    ) -> list[dict]:
        """C# GetRoutingOperDict — odv_routing_oper"""
        if not routing_ids:
            return []
        placeholders = ", ".join(["?"] * len(routing_ids))
        query = f"""
        SELECT routing_id, oper_id
        FROM odv_routing_oper
        WHERE partition_key = ?
          AND plan_ver = ?
          AND routing_id IN ({placeholders})
        """
        return execute_query(
            query, (project_id, plan_ver, *routing_ids)
        )

    @staticmethod
    def get_oper_masters(
        project_id: str, plan_ver: str
    ) -> list[dict]:
        """C# SetOperGroupDict — odv_oper_master"""
        query = """
        SELECT oper_id, oper_group_id
        FROM odv_oper_master
        WHERE partition_key = ?
          AND plan_ver = ?
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_buffer_masters(
        project_id: str, plan_ver: str
    ) -> list[dict]:
        """C# SetBufferDict — odv_buffer_master"""
        query = """
        SELECT buffer_id, buffer_seq
        FROM odv_buffer_master
        WHERE partition_key = ?
          AND plan_ver = ?
        """
        return execute_query(query, (project_id, plan_ver))

    @staticmethod
    def get_wip_for_detail(
        project_id: str, plan_ver: str,
        item_id: str = None, site_id: str = None, buffer_id: str = None,
    ) -> list[dict]:
        """C# SetWipDict — odv_wip"""
        sql_params: list = [project_id, plan_ver]
        where_extra = ""
        if item_id:
            where_extra += " AND item_id = ?"
            sql_params.append(item_id)
        if site_id:
            where_extra += " AND site_id = ?"
            sql_params.append(site_id)
        if buffer_id:
            where_extra += " AND buffer_id = ?"
            sql_params.append(buffer_id)
        query = f"""
        SELECT item_id, site_id, buffer_id, oper_id, wip_qty
        FROM odv_wip
        WHERE partition_key = ?
          AND plan_ver = ?
          {where_extra}
        """
        return execute_query(query, tuple(sql_params))

    @staticmethod
    def get_peg_info_for_detail(
        project_id: str, plan_ver: str, demand_id: str,
        is_default_uom: bool = True,
    ) -> list[dict]:
        """C# SetPegDict — out_peg_info"""
        qty_col = "peg_qty" if is_default_uom else "peg_conv_qty"
        query = f"""
        SELECT item_id, site_id, buffer_id, oper_id,
               {qty_col} AS peg_qty
        FROM out_peg_info
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id = ?
        """
        return execute_query(query, (project_id, plan_ver, demand_id))

    @staticmethod
    def get_oper_group_plans(
        project_id: str, plan_ver: str, demand_id: str
    ) -> list[dict]:
        """C# SetProdPlanDict3 (detailType != BUFFER) — rpt_oper_group_plan"""
        query = """
        SELECT demand_id, item_id, site_id, buffer_id, buffer_seq,
               oper_id, item_type, plan_date,
               out_plan_qty, out_plan_conv_qty
        FROM rpt_oper_group_plan
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id = ?
        """
        return execute_query(query, (project_id, plan_ver, demand_id))

    @staticmethod
    def get_item_masters_by_ids(
        project_id: str, plan_ver: str, item_ids: list[str]
    ) -> list[dict]:
        """C# SetItemDict — odv_item_master"""
        if not item_ids:
            return []
        placeholders = ", ".join(["?"] * len(item_ids))
        query = f"""
        SELECT item_id, item_type, item_name
        FROM odv_item_master
        WHERE partition_key = ?
          AND plan_ver = ?
          AND item_id IN ({placeholders})
        """
        return execute_query(
            query, (project_id, plan_ver, *item_ids)
        )

    @staticmethod
    def get_prod_detail2_section(
        project_id: str, plan_ver: str, demand_id: str
    ) -> list[dict]:
        """
        C# GetSection — RarPlanByProdSection_Select_P_Cmd1.sql
        rpt_demand_plan_isb에서 plan_date min/max 조회
        """
        query = """
        SELECT
            MIN(kv.key) AS "minDate",
            COALESCE(
                date_format(
                    MAX(CAST(a.extend_due_datetime AS TIMESTAMP)),
                    '%Y-%m-%d'
                ),
                MAX(kv.key)
            ) AS "maxDate"
        FROM rpt_demand_plan_isb a
        CROSS JOIN UNNEST(
            CAST(json_parse(a.plan_qty_detail_json) AS MAP(VARCHAR, VARCHAR))
        ) AS kv(key, value)
        WHERE a.partition_key = ?
          AND a.plan_ver = ?
          AND a.demand_id = ?
        """
        return execute_query(query, (project_id, plan_ver, demand_id))

    # ── rarPlanByProd/DemandSummary helper queries ──
    # C# RarPlanSummaryProcessor 완전 재현을 위한 개별 쿼리들

    @staticmethod
    def get_demands_for_summary(
        project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """C# SetSummaryUsingDemand — odv_demand (+ item_name 조인)"""
        demand_ids = params.get("demandIDs", [])
        item_ids = params.get("itemIDs", [])
        customers = params.get("customers", [])

        sql_params: list = [project_id, plan_ver]
        where_extra = ""

        if demand_ids:
            placeholders = ", ".join(["?"] * len(demand_ids))
            where_extra += f" AND a.demand_id IN ({placeholders})"
            sql_params.extend(demand_ids)
        if item_ids:
            placeholders = ", ".join(["?"] * len(item_ids))
            where_extra += f" AND a.item_id IN ({placeholders})"
            sql_params.extend(item_ids)
        if customers:
            placeholders = ", ".join(["?"] * len(customers))
            where_extra += f" AND a.cust_id IN ({placeholders})"
            sql_params.extend(customers)

        query = f"""
        SELECT a.demand_id, a.item_id, b.item_name AS demand_item_name,
               a.site_id, a.buffer_id, a.demand_qty, a.due_date, a.cust_id
        FROM odv_demand a
        LEFT OUTER JOIN odv_item_master b
            ON a.partition_key = b.partition_key
            AND a.plan_ver = b.plan_ver
            AND a.item_id = b.item_id
        WHERE a.partition_key = ?
          AND a.plan_ver = ?
          {where_extra}
        """
        return execute_query(query, tuple(sql_params))

    @staticmethod
    def get_safety_stock_demands_for_summary(
        project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """C# SetSummaryUsingSafetyStockDemand — rpt_safety_stock_demand"""
        demand_ids = params.get("demandIDs", [])
        item_ids = params.get("itemIDs", [])
        customers = params.get("customers", [])

        sql_params: list = [project_id, plan_ver]
        where_extra = ""

        if demand_ids:
            placeholders = ", ".join(["?"] * len(demand_ids))
            where_extra += f" AND demand_id IN ({placeholders})"
            sql_params.extend(demand_ids)
        if item_ids:
            placeholders = ", ".join(["?"] * len(item_ids))
            where_extra += f" AND item_id IN ({placeholders})"
            sql_params.extend(item_ids)
        if customers:
            placeholders = ", ".join(["?"] * len(customers))
            where_extra += f" AND cust_id IN ({placeholders})"
            sql_params.extend(customers)

        query = f"""
        SELECT demand_id, item_id, site_id, buffer_id,
               demand_qty, CAST(due_datetime AS VARCHAR) AS due_date, cust_id
        FROM rpt_safety_stock_demand
        WHERE partition_key = ?
          AND plan_ver = ?
          {where_extra}
        """
        return execute_query(query, tuple(sql_params))

    @staticmethod
    def get_shipment_plans_for_summary(
        project_id: str, plan_ver: str, demand_ids: list[str]
    ) -> list[dict]:
        """C# SetSummaryUsingShipmentPlan — rpt_shipment_plan"""
        if not demand_ids:
            return []
        placeholders = ", ".join(["?"] * len(demand_ids))
        query = f"""
        SELECT demand_id, shipment_date, warehouse_in_date,
               shipment_qty, ontime_plan_qty AS on_time_qty, late_qty,
               demand_type
        FROM rpt_shipment_plan
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id IN ({placeholders})
        """
        return execute_query(
            query, (project_id, plan_ver, *demand_ids)
        )

    @staticmethod
    def get_wip_qty_by_isb(
        project_id: str, plan_ver: str,
        item_id: str, site_id: str, buffer_id: str,
    ) -> float:
        """C# GetWipQty — odv_wip by item/site/buffer"""
        query = """
        SELECT COALESCE(SUM(wip_qty), 0) AS total_wip
        FROM odv_wip
        WHERE partition_key = ?
          AND plan_ver = ?
          AND item_id = ?
          AND site_id = ?
          AND buffer_id = ?
        """
        rows = execute_query(
            query, (project_id, plan_ver, item_id, site_id, buffer_id)
        )
        return float(rows[0].get("total_wip") or 0) if rows else 0

    @staticmethod
    def get_peg_qty_from_demand_plan_isb(
        project_id: str, plan_ver: str,
        demand_id: str, item_id: str, site_id: str, buffer_id: str,
    ) -> float:
        """C# GetPegQty — rpt_demand_plan_isb by demand/item/site/buffer"""
        query = """
        SELECT COALESCE(SUM(peg_qty), 0) AS total_peg
        FROM rpt_demand_plan_isb
        WHERE partition_key = ?
          AND plan_ver = ?
          AND demand_id = ?
          AND item_id = ?
          AND site_id = ?
          AND buffer_id = ?
        """
        rows = execute_query(
            query, (project_id, plan_ver, demand_id, item_id, site_id, buffer_id)
        )
        return float(rows[0].get("total_peg") or 0) if rows else 0

    @staticmethod
    def get_cust_names(
        project_id: str, plan_ver: str, cust_ids: list[str]
    ) -> dict[str, str]:
        """C# SetCustomerDict — odv_cust_master"""
        if not cust_ids:
            return {}
        placeholders = ", ".join(["?"] * len(cust_ids))
        query = f"""
        SELECT cust_id, cust_name
        FROM odv_cust_master
        WHERE partition_key = ?
          AND plan_ver = ?
          AND cust_id IN ({placeholders})
        """
        rows = execute_query(
            query, (project_id, plan_ver, *cust_ids)
        )
        return {r["cust_id"]: r.get("cust_name", "") for r in rows}

    # ── RarPlanByProd/Detail (BOM path CTE) ──

    @staticmethod
    def get_plan_by_prod_detail(
        project_id: str, plan_ver: str, demand_id: str
    ) -> list[dict]:
        """
        RarPlanByProd/Detail — BOM 경로 기반 생산 상세

        원본: RarProdPlanInSummary_Detail_P_Cmd1.sql
        """
        query = """
        WITH
        demands AS (
            SELECT DISTINCT partition_key, plan_ver, demand_id,
                   item_id, site_id, buffer_id, due_date, max_lateness_day
            FROM odv_demand
            WHERE partition_key = ?
              AND plan_ver = ?
              AND demand_id = ?
            UNION ALL
            SELECT DISTINCT partition_key, plan_ver, demand_id,
                   item_id, site_id, buffer_id,
                   CAST(due_datetime AS VARCHAR) AS due_date,
                   max_lateness_day
            FROM rpt_safety_stock_demand
            WHERE partition_key = ?
              AND plan_ver = ?
              AND demand_id = ?
        ),
        bom_path AS (
            SELECT DISTINCT
                a.partition_key, a.plan_ver, b.demand_id,
                x.item_id, x.site_id, x.buffer_id
            FROM out_bom_network_info a
            INNER JOIN demands b
                ON a.partition_key = b.partition_key
                AND a.plan_ver = b.plan_ver
                AND a.demand_item_id = b.item_id
                AND a.demand_site_id = b.site_id
                AND a.demand_buffer_id = b.buffer_id
            CROSS JOIN UNNEST(
                ARRAY[a.from_item_id, a.to_item_id],
                ARRAY[a.from_site_id, a.to_site_id],
                ARRAY[a.from_buffer_id, a.to_buffer_id]
            ) AS x(item_id, site_id, buffer_id)
            WHERE a.partition_key = ?
              AND a.plan_ver = ?
        ),
        plan AS (
            SELECT a.item_id, a.buffer_id, a.site_id,
                   a.item_type, a.peg_qty,
                   0 AS wip_qty,
                   kv.key AS plan_date,
                   CAST(kv.value AS DOUBLE) AS out_plan_qty
            FROM rpt_demand_plan_isb a
            CROSS JOIN UNNEST(
                CAST(json_parse(a.plan_qty_detail_json) AS MAP(VARCHAR, VARCHAR))
            ) AS kv(key, value)
            WHERE a.partition_key = ?
              AND a.plan_ver = ?
              AND a.demand_id = ?
        )
        SELECT
            a.item_id AS "itemID",
            a.buffer_id AS "bufferID",
            a.site_id AS "siteID",
            f.item_type AS "itemType",
            f.item_name AS "itemName",
            0 AS "wipQty",
            plan.peg_qty AS "pegQty",
            plan.plan_date AS "planDate",
            plan.out_plan_qty AS "outPlanQty",
            e.buffer_seq
        FROM bom_path a
        LEFT JOIN odv_buffer_master e
            ON e.partition_key = ?
            AND e.plan_ver = ?
            AND a.buffer_id = e.buffer_id
        LEFT JOIN odv_item_master f
            ON f.partition_key = ?
            AND f.plan_ver = ?
            AND a.item_id = f.item_id
        LEFT JOIN plan
            ON a.item_id = plan.item_id
            AND a.site_id = plan.site_id
            AND a.buffer_id = plan.buffer_id
        ORDER BY CASE WHEN a.item_id IS NULL THEN 1 ELSE 0 END,
                 CASE WHEN e.buffer_seq IS NOT NULL THEN 0 ELSE 1 END,
                 e.buffer_seq DESC
        """
        return execute_query(
            query,
            (
                # demands CTE: odv_demand
                project_id, plan_ver, demand_id,
                # demands CTE: rpt_safety_stock_demand
                project_id, plan_ver, demand_id,
                # bom_path CTE
                project_id, plan_ver,
                # plan CTE
                project_id, plan_ver, demand_id,
                # LEFT JOIN odv_buffer_master
                project_id, plan_ver,
                # LEFT JOIN odv_item_master
                project_id, plan_ver,
            ),
        )

    # ── RarPlanByProd/Summary ──
    # Summary와 DemandSummary 모두 서비스 레이어에서 in-memory 처리
    # (C# RarPlanSummaryProcessor 재현, repository 개별 쿼리 사용)

    # ── RarPlanByProd/Wip ──

    @staticmethod
    def get_wip(project_id: str, plan_ver: str) -> list[dict]:
        """
        RarPlanByProd/Wip — WIP 재공 데이터

        원본: RarProdPlanInSummary_Wip_P_Cmd1.sql
        """
        query = """
        SELECT item_id AS "itemID"
             , site_id AS "siteID"
             , buffer_id AS "bufferID"
             , '' AS "itemType"
             , SUM(wip_qty) AS "wipQty"
             , 0 AS "pegQty"
             , '' AS "planDate"
             , 0 AS "outPlanQty"
        FROM odv_wip
        WHERE partition_key = ?
          AND plan_ver = ?
        GROUP BY 1, 2, 3
        """
        return execute_query(query, (project_id, plan_ver))

    # ── RarPlanByProd/GetBufferPlanTarget ──

    @staticmethod
    def get_buffer_plan_target(
        project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """
        RarPlanByProd/GetBufferPlanTarget — 버퍼 계획 타겟

        원본: RptBufferTarget_Select_P_Cmd1.sql + RptBufferPlan_Select_P_Cmd1.sql
        두 테이블을 합쳐서 반환
        """
        demand_id = params.get("demandID", "")

        # Buffer Target
        target_params: list = [project_id, plan_ver]
        target_where = ""
        if demand_id:
            target_where += " AND demand_id = ?"
            target_params.append(demand_id)

        target_query = f"""
        SELECT 'TARGET' AS record_type,
               project_id, plan_ver, stage_id, item_id, item_type,
               site_id, std_buffer_id, std_buffer_seq,
               target_datetime, target_date, target_week, target_month,
               arrival_target_qty, arrival_target_unit_qty,
               in_target_qty, in_target_unit_qty,
               out_target_qty, out_target_unit_qty,
               NULL AS in_plan_qty, NULL AS out_plan_qty,
               NULL AS in_plan_conv_qty, NULL AS out_plan_conv_qty,
               demand_id, demand_item_id, demand_site_id, demand_buffer_id,
               due_datetime, due_date, due_week, due_month,
               item_name, site_name, item_spec, prod_type,
               item_size_type, item_group_id, cust_id, demand_type,
               cust_name, prop_json
        FROM rpt_buffer_target
        WHERE partition_key = ?
          AND plan_ver = ?
          {target_where}
        """

        # Buffer Plan
        plan_params: list = [project_id, plan_ver]
        plan_where = ""
        if demand_id:
            plan_where += " AND demand_id = ?"
            plan_params.append(demand_id)

        plan_query = f"""
        SELECT 'PLAN' AS record_type,
               project_id, plan_ver, stage_id, item_id, item_type,
               site_id, std_buffer_id, std_buffer_seq,
               plan_datetime AS target_datetime,
               plan_date AS target_date,
               plan_week AS target_week,
               plan_month AS target_month,
               NULL AS arrival_target_qty, NULL AS arrival_target_unit_qty,
               NULL AS in_target_qty, NULL AS in_target_unit_qty,
               NULL AS out_target_qty, NULL AS out_target_unit_qty,
               in_plan_qty, out_plan_qty,
               in_plan_conv_qty, out_plan_conv_qty,
               demand_id, demand_item_id, demand_site_id, demand_buffer_id,
               due_datetime, due_date, due_week, due_month,
               item_name, site_name, item_spec, prod_type,
               item_size_type, item_group_id, cust_id, demand_type,
               cust_name, prop_json
        FROM rpt_buffer_plan
        WHERE partition_key = ?
          AND plan_ver = ?
          {plan_where}
        """

        full_query = f"{target_query}\nUNION ALL\n{plan_query}"
        all_params = target_params + plan_params
        return execute_query(full_query, tuple(all_params))

    # ── RarPlanByRes/GetProps ──

    @staticmethod
    def get_item_props(
        project_id: str, plan_ver: str, item_id: str
    ) -> dict:
        """
        RarPlanByRes/GetProps — 품목 속성 (마스터 + 동적 prop)

        C# GetPropValueDict: OdvItemMaster 속성 중 exceptProps 제외 후
        OdvItemProp rows를 병합하여 단일 dict 반환
        """
        # 1) Item Master 조회 — C# exceptProps 제외:
        # create_user_id, create_user, create_datetime,
        # update_user, update_user_id, update_datetime,
        # project_id, plan_ver, partition_key, ObjectState
        master_query = """
        SELECT item_id, item_type, item_name,
               item_group_id AS item_group, description,
               item_priority, procurement_type, prod_type,
               item_size_type AS item_size, item_spec,
               prop01, prop02, prop03, prop04, prop05,
               prop06, prop07, prop08, prop09, prop10
        FROM odv_item_master
        WHERE partition_key = ?
          AND plan_ver = ?
          AND item_id = ?
        """
        master_rows = execute_query(
            master_query, (project_id, plan_ver, item_id)
        )

        # 2) Item Prop 조회
        prop_query = """
        SELECT prop_id, prop_value
        FROM odv_item_prop_value
        WHERE partition_key = ?
          AND plan_ver = ?
          AND item_id = ?
        """
        prop_rows = execute_query(
            prop_query, (project_id, plan_ver, item_id)
        )

        # 3) 병합: C#과 동일하게 단일 dict 반환
        if not master_rows:
            return {}

        result = dict(master_rows[0])
        for prop in prop_rows:
            pid = prop.get("prop_id", "")
            pval = prop.get("prop_value", "")
            if pid:
                result[pid] = pval

        return result

    # ── odlReport (동적 스키마) ──

    @staticmethod
    def get_odl_report(
        project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """
        odlReport — 동적 스키마 쿼리

        schema_name 파라미터에 따라 테이블 결정.
        RTF Report에서는 주로 'Demand' 스키마 사용.
        """
        schema_name = params.get("schema_name", "")
        demand_id = params.get("demandID", "")

        # 스키마명 → 테이블 매핑
        table_map: dict[str, str] = {
            "Demand": "odv_demand",
            "DemandProp": "odv_demand_prop",
            "Wip": "odv_wip",
            "WipProp": "odv_wip_prop",
            "ItemMaster": "odv_item_master",
            "ItemProp": "odv_item_prop_value",
            "SiteMaster": "odv_site_master",
            "BufferMaster": "odv_buffer_master",
            "CustMaster": "odv_cust_master",
            "BomMaster": "odv_bom_master",
            "RoutingMaster": "odv_routing_master",
            "ResMaster": "odv_res_master",
            "OperMaster": "odv_oper_master",
            "OutPegInfo": "out_peg_info",
            "OutUnpegInfo": "out_unpeg_info",
            "RptBufferPlan": "rpt_buffer_plan",
            "RptBufferTarget": "rpt_buffer_target",
            "RptDemandPlanIsb": "rpt_demand_plan_isb",
            "RptShipmentPlan": "rpt_shipment_plan",
            "RptSafetyStockDemand": "rpt_safety_stock_demand",
        }

        table_name = table_map.get(schema_name)
        if not table_name:
            return []

        sql_params: list = [project_id, plan_ver]
        where_clause = ""

        if demand_id:
            where_clause += " AND demand_id = ?"
            sql_params.append(demand_id)

        # Demand 스키마의 경우 item_master 조인으로 item_name 추가
        if schema_name == "Demand":
            query = f"""
            SELECT a.*, b.item_name AS demand_item_name
            FROM {table_name} a
            LEFT OUTER JOIN odv_item_master b
                ON a.partition_key = b.partition_key
                AND a.plan_ver = b.plan_ver
                AND a.item_id = b.item_id
            WHERE a.partition_key = ?
              AND a.plan_ver = ?
              {where_clause}
            ORDER BY a.demand_id
            """
        else:
            query = f"""
            SELECT *
            FROM {table_name}
            WHERE partition_key = ?
              AND plan_ver = ?
              {where_clause}
            """

        return execute_query(query, tuple(sql_params))
