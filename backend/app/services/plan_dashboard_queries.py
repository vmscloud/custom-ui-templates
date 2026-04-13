"""
Plan Dashboard SQL 쿼리 상수

Trino (Iceberg) execute_direct_query로 실행되는 SQL 쿼리들.
테이블명은 비한정(unqualified) — catalog/schema는 execute_direct_query에서 별도 전달.
파라미터는 Python str.format() 스타일 {param}.
"""

# RTF: 모든 TOTAL% index 조회 (서비스에서 동적 필터링)
RTF_INDEX_DATA_SQL = """
SELECT
    index_name,
    CAST(plan_value AS DOUBLE) AS plan_value,
    category_name,
    time_uom,
    qty_uom,
    CAST(conv_qty AS DOUBLE) AS conv_qty,
    conv_qty_uom
FROM out_plan_index
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND index_name LIKE 'TOTAL%'
  {category_filter}
"""

# OTD: rpt_buffer_plan 조회 (frozen/plan 비교용)
OTD_BUFFER_PLAN_SQL = """
SELECT
    demand_id,
    item_id,
    item_group_id,
    due_date,
    CAST(plan_qty AS DOUBLE) AS plan_qty,
    CAST(conv_qty AS DOUBLE) AS conv_qty,
    qty_uom,
    conv_qty_uom,
    demand_type,
    prod_type
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND buffer_id IN ({buffer_ids})
  {production_area_filter}
"""

# OTD: ope_exec_actual 조회 (실적 데이터)
# NOTE: PG 스키마에서 partition_key/plan_ver 없음, project_id 사용. inout_type (underscore 없음)
OTD_EXEC_ACTUAL_SQL = """
SELECT
    plan_date,
    CAST(plan_qty AS DOUBLE) AS plan_qty,
    CAST(plan_conv_qty AS DOUBLE) AS conv_qty,
    qty_uom,
    conv_qty_uom,
    oper_id,
    buffer_id,
    detail_json
FROM ope_exec_actual
WHERE project_id = '{project_id}'
  AND inout_type = 'In'
  AND buffer_id IN ({buffer_ids})
  AND plan_date >= '{start_date}'
  AND plan_date <= '{end_date}'
  {production_area_filter}
"""

# Final item buffer IDs (C# 원본: OdvBufferMaster → final_item_buffer_yn)
FINAL_ITEM_BUFFER_SQL = """
SELECT DISTINCT buffer_id
FROM odv_buffer_master
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND final_item_buffer_yn = 'y'
"""

# Demand types list
DEMAND_TYPES_SQL = """
SELECT DISTINCT demand_type
FROM odv_demand
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
ORDER BY demand_type
"""

# Item groups list
ITEM_GROUPS_SQL = """
SELECT DISTINCT item_group_id
FROM odv_item_master
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
ORDER BY item_group_id
"""

# Keep the existing non-RTF queries
PEG_REPORT_SUMMARY_SQL = """
SELECT
    MAX(CASE WHEN index_name = 'TOTAL_WIP_QTY' THEN plan_value END) AS wip_qty,
    MAX(CASE WHEN index_name = 'TOTAL_PEG_QTY' THEN plan_value END) AS peg_qty,
    MAX(CASE WHEN index_name = 'TOTAL_UNPEG_QTY' THEN plan_value END) AS unpeg_qty,
    AVG(CASE WHEN index_name = 'TOTAL_PEG_RATIO' THEN plan_value END) AS peg_ratio,
    AVG(CASE WHEN index_name = 'TOTAL_UNPEG_RATIO' THEN plan_value END) AS unpeg_ratio
FROM out_plan_index
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND index_name IN ('TOTAL_WIP_QTY', 'TOTAL_PEG_QTY', 'TOTAL_UNPEG_QTY', 'TOTAL_PEG_RATIO', 'TOTAL_UNPEG_RATIO')
"""

UNPEG_REASONS_SQL = """
WITH main_data AS (
    SELECT MAX(CASE WHEN index_name = 'TOTAL_WIP_QTY' THEN plan_value ELSE 0 END) AS wip_qty
    FROM out_plan_index
    WHERE partition_key = '{partition_key}' AND plan_ver = '{plan_ver}'
)
SELECT
    u.UNPEG_REASON AS unpeg_reason,
    SUM(u.UNPEG_QTY) AS unpeg_qty,
    CASE WHEN md.wip_qty > 0 THEN ROUND(CAST(SUM(u.UNPEG_QTY) / md.wip_qty * 100 AS DOUBLE), 2) ELSE 0 END AS unpeg_ratio
FROM OUT_UNPEG_INFO u
CROSS JOIN main_data md
WHERE u.partition_key = '{partition_key}' AND u.plan_ver = '{plan_ver}'
GROUP BY u.UNPEG_REASON, md.wip_qty
ORDER BY unpeg_qty DESC
"""

RES_GROUP_DETAIL_SQL = """
SELECT
    util.INDEX_NAME AS res_group_id,
    ROUND(CAST(AVG(CASE WHEN util.CATEGORY_NAME = 'RESOURCE_UTILIZATION' THEN util.PLAN_VALUE END) AS DOUBLE), 1) AS avg_utilization,
    ROUND(CAST(AVG(CASE WHEN util.CATEGORY_NAME = 'RESOURCE_UTILIZATION_MIN' THEN util.PLAN_VALUE END) AS DOUBLE), 1) AS min_utilization,
    ROUND(CAST(AVG(CASE WHEN util.CATEGORY_NAME = 'RESOURCE_UTILIZATION_MAX' THEN util.PLAN_VALUE END) AS DOUBLE), 1) AS max_utilization,
    ROUND(CAST(COALESCE(AVG(setup.PLAN_VALUE), 0) AS DOUBLE), 1) AS setup_count
FROM OUT_PLAN_INDEX util
LEFT JOIN OUT_PLAN_INDEX setup
    ON util.INDEX_NAME = setup.INDEX_NAME
    AND setup.CATEGORY_NAME = 'SETUP_COUNT_DAILY_AVG'
    AND setup.TIME_KEY = '-'
    AND setup.partition_key = '{partition_key}'
    AND setup.plan_ver = '{plan_ver}'
WHERE util.partition_key = '{partition_key}'
  AND util.plan_ver = '{plan_ver}'
  AND util.CATEGORY_NAME LIKE 'RESOURCE_UTILIZATION%'
  AND util.TIME_KEY = '-'
  AND util.INDEX_NAME != 'ALL_RES_GROUP'
  {res_group_filter}
GROUP BY util.INDEX_NAME
ORDER BY 2 DESC NULLS LAST
LIMIT 4
"""

RES_GROUP_DETAIL_BY_PERIOD_SQL = """
WITH RankedData AS (
    SELECT
        INDEX_NAME AS res_group_id,
        time_key,
        ROUND(CAST(AVG(CASE WHEN CATEGORY_NAME = 'RESOURCE_UTILIZATION' THEN PLAN_VALUE END) AS DOUBLE), 1) AS avg_utilization,
        ROUND(CAST(AVG(CASE WHEN CATEGORY_NAME = 'RESOURCE_UTILIZATION_MIN' THEN PLAN_VALUE END) AS DOUBLE), 1) AS min_utilization,
        ROUND(CAST(AVG(CASE WHEN CATEGORY_NAME = 'RESOURCE_UTILIZATION_MAX' THEN PLAN_VALUE END) AS DOUBLE), 1) AS max_utilization,
        ROW_NUMBER() OVER (PARTITION BY INDEX_NAME ORDER BY time_key ASC) AS rn
    FROM out_plan_index
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND CATEGORY_NAME LIKE 'RESOURCE_UTILIZATION%'
      AND time_uom = 'Week'
      AND INDEX_NAME != 'ALL_RES_GROUP'
      {res_group_filter}
    GROUP BY INDEX_NAME, time_key
),
SetupRankedData AS (
    SELECT
        INDEX_NAME AS res_group_id,
        time_key,
        ROUND(CAST(SUM(PLAN_VALUE) / 7 AS DOUBLE), 2) AS setup_count,
        ROW_NUMBER() OVER (PARTITION BY INDEX_NAME ORDER BY time_key ASC) AS rn
    FROM out_plan_index
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND CATEGORY_NAME = 'SETUP_COUNT'
      AND time_uom = 'Week'
      {res_group_filter}
    GROUP BY INDEX_NAME, time_key
)
SELECT
    r.res_group_id,
    ROUND(CAST(AVG(r.avg_utilization) AS DOUBLE), 1) AS avg_utilization,
    ROUND(CAST(MIN(r.min_utilization) AS DOUBLE), 1) AS min_utilization,
    ROUND(CAST(MAX(r.max_utilization) AS DOUBLE), 1) AS max_utilization,
    ROUND(CAST(AVG(s.setup_count) AS DOUBLE), 1) AS setup_count
FROM RankedData r
LEFT JOIN SetupRankedData s ON r.res_group_id = s.res_group_id AND r.time_key = s.time_key
WHERE r.rn <= {week_period}
GROUP BY r.res_group_id
ORDER BY 2 DESC NULLS LAST
LIMIT 4
"""

SHORT_LOG_SUMMARY_SQL = """
SELECT
    short_reason,
    COUNT(*) AS cnt
FROM out_short_log
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND short_type = 'Short'
GROUP BY short_reason
ORDER BY cnt DESC
"""

ERROR_LOG_SUMMARY_SQL = """
SELECT
    severity,
    COUNT(*) AS cnt
FROM out_error_log
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
GROUP BY severity
ORDER BY cnt DESC
"""

# OTD: rpt_buffer_plan에서 item_group별 집계 (frozen/plan 비교)
# C# GetOTDSummaryRowsWithFrozenAndPlan / GetOTDSummaryRowsWithFrozenAndAct 대응
OTD_BUFFER_PLAN_SUMMARY_SQL = """
SELECT
    COALESCE(b.item_group_id, 'Unknown') AS category,
    ROUND(CAST(SUM(b.conv_qty) AS DOUBLE), 1) AS total_qty,
    SUM(b.conv_qty) AS origin_total_qty,
    MAX(b.conv_qty_uom) AS qty_uom,
    ROUND(CAST(SUM(CASE
        WHEN b.due_date >= '{cycle_start}' AND b.due_date < '{cycle_end}' THEN b.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS current_due_bucket_prod_qty,
    ROUND(CAST(SUM(CASE
        WHEN b.due_date < '{cycle_start}' THEN b.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS previous_due_bucket_prod_qty,
    ROUND(CAST(SUM(CASE
        WHEN b.due_date >= '{cycle_end}' AND b.due_date < '{next_cycle_end}' THEN b.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS next_due_bucket_prod_qty,
    ROUND(CAST(SUM(CASE
        WHEN b.due_date >= '{next_cycle_end}' THEN b.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS after_next_due_bucket_prod_qty
FROM rpt_buffer_plan b
INNER JOIN (
    SELECT DISTINCT STD_BUFFER_ID AS buffer_id
    FROM ODV_REPORT_STD_BUFFER_CONFIG
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND FINAL_ITEM_STD_BUFFER_YN = 'Y'
) fb ON b.buffer_id = fb.buffer_id
WHERE b.partition_key = '{partition_key}'
  AND b.plan_ver = '{plan_ver}'
  {production_area_filter}
GROUP BY b.item_group_id
ORDER BY b.item_group_id
"""

# OTD: ope_exec_actual에서 item_group별 실적 집계
OTD_ACTUAL_SUMMARY_SQL = """
SELECT
    COALESCE(a.item_group_id, 'Unknown') AS category,
    ROUND(CAST(SUM(a.conv_qty) AS DOUBLE), 1) AS total_qty,
    SUM(a.conv_qty) AS origin_total_qty,
    MAX(a.conv_qty_uom) AS qty_uom,
    ROUND(CAST(SUM(CASE
        WHEN a.plan_date >= '{cycle_start}' AND a.plan_date < '{cycle_end}' THEN a.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS current_due_bucket_prod_qty,
    ROUND(CAST(SUM(CASE
        WHEN a.plan_date < '{cycle_start}' THEN a.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS previous_due_bucket_prod_qty,
    ROUND(CAST(SUM(CASE
        WHEN a.plan_date >= '{cycle_end}' AND a.plan_date < '{next_cycle_end}' THEN a.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS next_due_bucket_prod_qty,
    ROUND(CAST(SUM(CASE
        WHEN a.plan_date >= '{next_cycle_end}' THEN a.conv_qty ELSE 0
    END) AS DOUBLE), 1) AS after_next_due_bucket_prod_qty
FROM ope_exec_actual a
INNER JOIN (
    SELECT DISTINCT STD_BUFFER_ID AS buffer_id
    FROM ODV_REPORT_STD_BUFFER_CONFIG
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND FINAL_ITEM_STD_BUFFER_YN = 'Y'
) fb ON a.buffer_id = fb.buffer_id
WHERE a.partition_key = '{partition_key}'
  AND a.plan_ver = '{plan_ver}'
  AND a.in_out_type = 'In'
  {production_area_filter}
GROUP BY a.item_group_id
ORDER BY a.item_group_id
"""

PROD_QTY_SQL = """
SELECT
    ROUND(CAST(AVG(PLAN_VALUE) AS DOUBLE), 0) AS total_avg_prod_qty
FROM out_plan_index
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND CATEGORY_NAME = CASE WHEN '{aggregate_type}' = 'MONTH' THEN 'PROD_MONTH_AVG' ELSE 'PROD_WEEK_AVG' END
"""

PROD_REPORT_SQL = """
SELECT date, prod_qty FROM (
    SELECT
        time_key AS date,
        SUM(plan_value) AS prod_qty
    FROM out_plan_index
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND CATEGORY_NAME = 'PROD_QTY'
      AND time_uom = '{aggregate_type}'
    GROUP BY time_key

    UNION ALL

    SELECT
        'Total' AS date,
        SUM(plan_value) AS prod_qty
    FROM out_plan_index
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND CATEGORY_NAME = 'PROD_QTY'
      AND time_uom = '{aggregate_type}'
    HAVING SUM(plan_value) > 0
) t
ORDER BY date
"""

STD_DETAIL_SQL = """
WITH std_config AS (
    SELECT
        STD_BUFFER_ID AS buffer_id,
        FINAL_ITEM_STD_BUFFER_YN
    FROM ODV_REPORT_STD_BUFFER_CONFIG
    WHERE partition_key = '{partition_key}'
      AND plan_ver = '{plan_ver}'
      AND FINAL_ITEM_STD_BUFFER_YN = 'Y'
)
SELECT
    p.INDEX_NAME AS buffer_id,
    MAX(CASE WHEN p.CATEGORY_NAME = 'BOH_QTY' THEN p.plan_value END) AS boh_qty,
    MAX(CASE WHEN p.CATEGORY_NAME = 'EOH_QTY' THEN p.plan_value END) AS eoh_qty,
    MAX(CASE WHEN p.CATEGORY_NAME = 'BOH_DAY' THEN p.plan_value END) AS boh_days,
    MAX(CASE WHEN p.CATEGORY_NAME = 'EOH_DAY' THEN p.plan_value END) AS eoh_days,
    CASE WHEN c.buffer_id IS NOT NULL THEN 1 ELSE 0 END AS is_final_item
FROM out_plan_index p
LEFT JOIN std_config c ON p.INDEX_NAME = c.buffer_id
WHERE p.partition_key = '{partition_key}'
  AND p.plan_ver = '{plan_ver}'
  AND p.CATEGORY_NAME IN ('BOH_QTY', 'BOH_DAY', 'EOH_QTY', 'EOH_DAY')
  AND p.time_key = '-'
GROUP BY p.INDEX_NAME, c.buffer_id
ORDER BY is_final_item DESC, p.INDEX_NAME
LIMIT 2
"""

OPER_GROUP_CAPA_SQL = """
SELECT
    INDEX_NAME AS oper_group_id,
    time_key,
    MAX(CASE WHEN CATEGORY_NAME LIKE '%UTILIZATION' AND CATEGORY_NAME NOT LIKE '%_MIN' AND CATEGORY_NAME NOT LIKE '%_MAX' THEN plan_value END) AS utilization,
    MAX(CASE WHEN CATEGORY_NAME LIKE '%CAPA' THEN plan_value END) AS capa,
    MAX(CASE WHEN CATEGORY_NAME LIKE '%LOAD' THEN plan_value END) AS load_value
FROM out_plan_index
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND CATEGORY_NAME LIKE 'OPER_GROUP%'
  AND time_uom = 'Day'
  {oper_group_filter}
GROUP BY INDEX_NAME, time_key
ORDER BY INDEX_NAME, time_key
"""

RES_GROUP_MASTER_SQL = """
SELECT DISTINCT
    rg.RES_GROUP_ID AS res_group_id,
    rg.RES_GROUP_NAME AS res_group_name
FROM ODV_RES_GROUP_MASTER rg
INNER JOIN ODV_RES_MASTER r
    ON rg.partition_key = r.partition_key
    AND rg.plan_ver = r.plan_ver
    AND rg.RES_GROUP_ID = r.RES_GROUP_ID
    AND r.RES_CATEGORY = 'Resource'
WHERE rg.partition_key = '{partition_key}'
  AND rg.plan_ver = '{plan_ver}'
ORDER BY rg.RES_GROUP_ID
"""

# Plan cycle dates (for OTD date calculations)
PLAN_CONFIG_DATES_SQL = """
SELECT
    c.plan_start_datetime,
    c.plan_period,
    ci.start_datetime AS cycle_start_date,
    ci.end_datetime AS cycle_end_date,
    ci.frozen_plan_ver
FROM cfg_plan_config c
INNER JOIN cfg_plan_cycle_info ci
    ON c.project_id = ci.project_id AND c.plan_cycle_id = ci.plan_cycle_id
WHERE c.project_id = '{project_id}'
  AND c.plan_ver = '{plan_ver}'
LIMIT 1
"""
