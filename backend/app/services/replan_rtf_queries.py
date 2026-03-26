"""
재수립 RTF SQL 쿼리 상수

Trino (Iceberg) execute_direct_query로 실행.
파라미터는 Python str.format() 스타일 {param}.
"""

# 출하계획 조회 (Main/Detail 공용)
# RPT_SHIPMENT_PLAN에서 수요별 집계
# uom_type에 따라 DEFAULT/CONVERSION 컬럼 선택
SHIPMENT_PLAN_SQL = """
SELECT
    DEMAND_ID AS demand_id,
    MAX(STAGE_ID) AS stage_id,
    MAX(SHIPMENT_DATE) AS shipment_date,
    MAX(DEMAND_QTY) AS demand_qty,
    MAX(SHIPMENT_QTY) AS shipment_qty,
    SUM(CASE WHEN WAREHOUSE_STATUS = 'Early' THEN ONTIME_PLAN_QTY ELSE 0 END) AS early_qty,
    SUM(CASE WHEN WAREHOUSE_STATUS = 'OnTime' THEN ONTIME_PLAN_QTY ELSE 0 END) AS ontime_qty,
    SUM(LATE_QTY) AS late_qty,
    SUM(CASE WHEN WAREHOUSE_STATUS = 'Remain' THEN QTY ELSE 0 END) AS short_qty,
    MAX(QTY_UOM) AS qty_uom,
    MAX(QTY) AS qty,
    MAX(DEMAND_CONV_QTY) AS demand_conv_qty,
    MAX(SHIPMENT_CONV_QTY) AS shipment_conv_qty,
    SUM(CASE WHEN WAREHOUSE_STATUS = 'Early' THEN ONTIME_CONV_QTY ELSE 0 END) AS early_conv_qty,
    SUM(CASE WHEN WAREHOUSE_STATUS = 'OnTime' THEN ONTIME_CONV_QTY ELSE 0 END) AS ontime_conv_qty,
    SUM(LATE_CONV_QTY) AS late_conv_qty,
    SUM(CASE WHEN WAREHOUSE_STATUS = 'Remain' THEN CONV_QTY ELSE 0 END) AS short_conv_qty,
    MAX(CONV_QTY_UOM) AS conv_qty_uom,
    MAX(CONV_QTY) AS conv_qty,
    MAX(ITEM_ID) AS item_id,
    MAX(ITEM_NAME) AS item_name,
    MAX(ITEM_GROUP_ID) AS item_group_id,
    MAX(SITE_ID) AS site_id,
    MAX(SITE_NAME) AS site_name,
    MAX(BUFFER_ID) AS buffer_id,
    MAX(CUST_ID) AS cust_id,
    MAX(DUE_DATE) AS due_date,
    MAX(CONCAT(SUBSTR(DUE_WEEK, 1, 4), '-', SUBSTR(DUE_WEEK, 5))) AS due_week,
    MAX(CONCAT(SUBSTR(DUE_MONTH, 1, 4), '-', SUBSTR(DUE_MONTH, 5))) AS due_month,
    MAX(MAX_EARLINESS_DAY) AS max_earliness_day,
    MAX(MAX_LATENESS_DAY) AS max_lateness_day,
    MAX(DEMAND_TYPE) AS demand_type,
    MAX(DEMAND_PRIORITY) AS demand_priority,
    MAX(ITEM_TYPE) AS item_type,
    MAX(PROD_TYPE) AS prod_type,
    MAX(ITEM_SIZE_TYPE) AS item_size_type,
    MAX(ITEM_SPEC) AS item_spec,
    MIN(WAREHOUSE_STATUS) AS warehouse_status,
    MAX(SHIPMENT_STATUS) AS shipment_status
FROM rpt_shipment_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND (DEMAND_TYPE != 'SafetyStock' OR DEMAND_TYPE IS NULL)
  AND DEMAND_TYPE <> '#Dummy'
  {prod_status_filter}
  {due_filter}
  {demand_id_filter}
GROUP BY DEMAND_ID
"""

# 실적 데이터 조회 (사이클 기간 내)
EXEC_ACTUAL_SQL = """
SELECT
    buffer_id,
    item_id,
    oper_id,
    plan_date,
    CAST(plan_qty AS DOUBLE) AS plan_qty,
    qty_uom,
    CAST(plan_conv_qty AS DOUBLE) AS plan_conv_qty,
    conv_qty_uom,
    json_extract_scalar(detail_json, '$.demand_id') AS demand_id,
    json_extract_scalar(detail_json, '$.due_date') AS due_date,
    json_extract_scalar(detail_json, '$.oper_group_id') AS oper_group_id,
    json_extract_scalar(detail_json, '$.item_group_id') AS item_group_id,
    json_extract_scalar(detail_json, '$.prod_type') AS prod_type,
    json_extract_scalar(detail_json, '$.production_area') AS production_area,
    json_extract_scalar(detail_json, '$.demand_type') AS demand_type,
    json_extract_scalar(detail_json, '$.due_week') AS due_week_raw,
    json_extract_scalar(detail_json, '$.demand_priority') AS demand_priority
FROM ope_exec_actual
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND in_out_type = 'In'
  AND CAST(plan_date AS DATE) >= DATE '{cycle_start_date}'
  AND CAST(plan_date AS DATE) <= DATE '{act_end_date}'
  {buffer_filter}
  {demand_id_filter}
"""

# 실적의 cust_id 조회 (별도)
DEMAND_CUST_SQL = """
SELECT demand_id, cust_id
FROM odv_demand
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND demand_id IN ({demand_ids})
"""

# 계획 종료일
PLAN_END_DATE_SQL = """
SELECT CAST(plan_start_datetime + plan_period * INTERVAL '1' DAY AS DATE) AS plan_end_date
FROM cfg_plan_config
WHERE project_id = '{project_id}'
  AND plan_ver = '{plan_ver}'
"""

# 최종품 버퍼 ID
FINAL_ITEM_BUFFER_SQL = """
SELECT DISTINCT STD_BUFFER_ID AS buffer_id
FROM ODV_REPORT_STD_BUFFER_CONFIG
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND FINAL_ITEM_STD_BUFFER_YN = 'Y'
"""

# 생산유형 필터 목록
PROD_TYPES_SQL = """
SELECT DISTINCT PROD_TYPE AS value
FROM rpt_shipment_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND PROD_TYPE IS NOT NULL
ORDER BY 1
"""

# 생산계획 피벗 (ProdDetail)
PROD_DETAIL_SQL = """
SELECT
    oper_group_id,
    item_id,
    plan_month,
    plan_week,
    CAST(plan_date AS VARCHAR) AS plan_date,
    CAST(SUM(CASE WHEN inout_type = 'Out' THEN {qty_col} ELSE 0 END) AS DOUBLE) AS prod_qty,
    CAST(SUM({qty_col}) AS DOUBLE) AS plan_qty,
    {qty_uom_col} AS qty_uom
FROM ope_exec_actual
WHERE project_id = '{project_id}'
  AND json_extract_scalar(detail_json, '$.demand_id') = '{demand_id}'
GROUP BY oper_group_id, item_id, plan_month, plan_week, plan_date, {qty_uom_col}
ORDER BY oper_group_id, item_id, plan_date
"""

# 기간 범위 (ProdDetail section)
SECTION_SQL = """
SELECT
    MIN(CAST(plan_date AS VARCHAR)) AS min_date,
    MAX(CAST(plan_date AS VARCHAR)) AS max_date
FROM ope_exec_actual
WHERE project_id = '{project_id}'
  AND json_extract_scalar(detail_json, '$.demand_id') = '{demand_id}'
"""
