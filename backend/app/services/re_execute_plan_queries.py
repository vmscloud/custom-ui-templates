"""
재실행 계획 (ReExecutePlan) SQL 쿼리 상수

Trino (Iceberg) execute_direct_query로 실행.
파라미터는 Python str.format() 스타일 {param}.
"""

# 지역(Region) 목록 조회 - rpt_buffer_plan.prop_json에서 추출
REGIONS_SQL = """
SELECT DISTINCT json_extract_scalar(prop_json, '$.production_area') AS region
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND json_extract_scalar(prop_json, '$.production_area') IS NOT NULL
  AND json_extract_scalar(prop_json, '$.production_area') != ''
ORDER BY region
"""

# 공정 그룹 목록 조회 - 원본: odv_oper_group_master
OPER_GROUPS_SQL = """
SELECT oper_group_id, oper_group_name, oper_group_seq
FROM odv_oper_group_master
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
ORDER BY oper_group_seq, oper_group_id
"""

# 버퍼 목록 조회 - rpt_buffer_plan에서 추출
BUFFERS_SQL = """
SELECT DISTINCT std_buffer_id AS buffer_id
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
ORDER BY std_buffer_id
"""

# 개별 공정(Oper) 목록 조회 - rpt_oper_group_plan에서 추출
OPERS_SQL = """
SELECT DISTINCT oper_id, oper_name
FROM rpt_oper_group_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND oper_id IS NOT NULL AND oper_id != ''
ORDER BY oper_id
"""

# 고객 목록 조회 - rpt_buffer_plan에서 추출
CUSTOMERS_SQL = """
SELECT DISTINCT cust_id
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND cust_id IS NOT NULL AND cust_id != ''
ORDER BY cust_id
"""

# 품목그룹 목록 조회 - rpt_buffer_plan에서 추출
ITEM_GROUPS_SQL = """
SELECT DISTINCT item_group_id
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND item_group_id IS NOT NULL AND item_group_id != ''
ORDER BY item_group_id
"""

# 수요유형 목록 조회 - rpt_buffer_plan에서 추출
DEMAND_TYPES_SQL = """
SELECT DISTINCT demand_type
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND demand_type IS NOT NULL AND demand_type != ''
ORDER BY demand_type
"""

# 공정 그룹 기준 피벗 데이터 (summaryType=OPERGROUP)
# C# 원본: startDate=cycleStart, endDate=cycleEnd 필터 적용
PIVOT_OPER_GROUP_SQL = """
SELECT
    oper_group_id,
    item_group_id,
    demand_type,
    CAST(plan_date AS VARCHAR) AS date,
    plan_month AS month,
    plan_week AS week,
    ROUND(CAST(SUM({qty_col}) AS DOUBLE), 2) AS qty
FROM rpt_oper_group_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND plan_date >= '{start_date}'
  AND plan_date <= '{end_date}'
  {oper_group_filter}
  {oper_filter}
  {demand_type_filter}
  {item_group_filter}
GROUP BY oper_group_id, item_group_id, demand_type, plan_date, plan_month, plan_week
ORDER BY oper_group_id, date
"""

# 버퍼 기준 피벗 데이터 (summaryType=BUFFER)
PIVOT_BUFFER_SQL = """
SELECT
    std_buffer_id AS buffer_id,
    item_group_id,
    demand_type,
    cust_id,
    CAST(plan_date AS VARCHAR) AS date,
    plan_month AS month,
    plan_week AS week,
    ROUND(CAST(SUM({qty_col}) AS DOUBLE), 2) AS qty
FROM rpt_buffer_plan
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND plan_date >= '{start_date}'
  AND plan_date <= '{end_date}'
  {buffer_filter}
  {customer_filter}
  {demand_type_filter}
  {item_group_filter}
GROUP BY std_buffer_id, item_group_id, demand_type, cust_id, plan_date, plan_month, plan_week
ORDER BY std_buffer_id, plan_date
"""

# 수요 목록 조회 (상세 FlexGrid용)
DEMAND_LIST_SQL = """
SELECT
    demand_id,
    item_id,
    site_id,
    buffer_id,
    CAST(due_date AS VARCHAR) AS due_date,
    CAST(due_datetime AS VARCHAR) AS due_datetime,
    ROUND(CAST(demand_qty AS DOUBLE), 2) AS demand_qty,
    demand_priority,
    cust_id,
    demand_type,
    max_lateness_day,
    max_earliness_day,
    demand_group_id AS demand_group,
    final_item_buffer_id,
    description
FROM odv_demand
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  {demand_type_filter}
  {customer_filter}
ORDER BY demand_id
"""
