"""
부하율 (LoadFactor) SQL 쿼리 상수

Trino (Iceberg) execute_direct_query로 실행.
파라미터는 Python str.format() 스타일 {param}.
NOTE: plan_start_datetime(std_ts)는 PostgreSQL에서 사전 조회 후 전달.
NOTE: capa_prop_key는 odv_report_prop_config에서 동적 조회 (예: PROP01).
"""

# 공정 그룹 목록 조회
OPER_GROUPS_SQL = """
SELECT DISTINCT oper_group_id, oper_group_name, oper_group_seq
FROM rpt_oper_group_target
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND oper_group_id != '#Undefined'
  AND (demand_type IS NULL OR demand_type != '#Dummy')
ORDER BY oper_group_seq, oper_group_id
"""

# RPT 프로퍼티 매핑 조회 (OperGroupCapa 등의 실제 prop_json 키 확인용)
PROP_CONFIG_SQL = """
SELECT prop_json
FROM odv_report_prop_config
WHERE partition_key = '{partition_key}'
  AND plan_ver = '{plan_ver}'
  AND table_name = 'RPT_OPER_GROUP_TARGET'
LIMIT 1
"""

# 공정 그룹별 총 부하율 (메인 차트용)
MAIN_SQL = """
WITH base AS (
    SELECT
        t.oper_group_id,
        t.oper_group_seq,
        CASE WHEN CAST(t.target_datetime AS DATE) < DATE '{std_ts}'
             THEN DATE '{std_ts}'
             ELSE CAST(t.target_datetime AS DATE)
        END AS fixed_date,
        CASE
            WHEN json_extract_scalar(t.prop_json, '$.{uom_prop_key}') IS NULL
              OR json_extract_scalar(t.prop_json, '$.{uom_prop_key}') = 'DEFAULT'
            THEN t.out_target_qty
            ELSE t.out_target_conv_qty
        END AS target_qty,
        CAST(json_extract_scalar(t.prop_json, '$.{capa_prop_key}') AS DOUBLE) AS capa_val
    FROM rpt_oper_group_target t
    WHERE t.partition_key = '{partition_key}'
      AND t.plan_ver = '{plan_ver}'
      AND t.oper_group_id != '#Undefined'
      AND (t.demand_type IS NULL OR t.demand_type != '#Dummy')
      AND t.oper_id IS NOT NULL
      {oper_group_filter}
)
SELECT
    oper_group_id,
    ROUND(MAX(capa_val), 2) AS capa,
    ROUND(CAST(SUM(target_qty) AS DOUBLE), 2) AS plan_qty,
    CASE WHEN MAX(capa_val) > 0 AND COUNT(DISTINCT fixed_date) > 0
         THEN ROUND(SUM(target_qty) / (MAX(capa_val) * COUNT(DISTINCT fixed_date)) * 100, 1)
         ELSE 0 END AS str_rate,
    100 AS base_line
FROM base
WHERE fixed_date >= DATE '{from_date}' AND fixed_date <= DATE '{to_date}'
GROUP BY oper_group_id
ORDER BY MAX(oper_group_seq), oper_group_id
"""

# 공정 그룹별 일간 item_group 분해 (그룹 차트용)
GROUP_SQL = """
WITH base AS (
    SELECT
        t.oper_group_id,
        t.item_group_id,
        CASE WHEN CAST(t.target_datetime AS DATE) < DATE '{std_ts}'
             THEN DATE '{std_ts}'
             ELSE CAST(t.target_datetime AS DATE)
        END AS fixed_date,
        CASE
            WHEN json_extract_scalar(t.prop_json, '$.{uom_prop_key}') IS NULL
              OR json_extract_scalar(t.prop_json, '$.{uom_prop_key}') = 'DEFAULT'
            THEN t.out_target_qty
            ELSE t.out_target_conv_qty
        END AS target_qty,
        CAST(json_extract_scalar(t.prop_json, '$.{capa_prop_key}') AS DOUBLE) AS capa_val
    FROM rpt_oper_group_target t
    WHERE t.partition_key = '{partition_key}'
      AND t.plan_ver = '{plan_ver}'
      AND t.oper_group_id != '#Undefined'
      AND (t.demand_type IS NULL OR t.demand_type != '#Dummy')
      AND t.oper_id IS NOT NULL
      {oper_group_filter}
)
SELECT
    oper_group_id,
    COALESCE(item_group_id, 'N/A') AS item_group_id,
    CAST(fixed_date AS VARCHAR) AS date,
    ROUND(CAST(SUM(target_qty) AS DOUBLE), 2) AS plan_qty,
    ROUND(MAX(capa_val), 2) AS capa,
    CASE WHEN MAX(capa_val) > 0
         THEN ROUND(SUM(target_qty) / MAX(capa_val) * 100, 1)
         ELSE 0 END AS str_rate,
    100 AS base_line,
    1 AS sort_order
FROM base
WHERE fixed_date >= DATE '{from_date}' AND fixed_date <= DATE '{to_date}'
GROUP BY oper_group_id, item_group_id, fixed_date

UNION ALL

SELECT
    oper_group_id,
    'TOTAL' AS item_group_id,
    CAST(fixed_date AS VARCHAR) AS date,
    ROUND(CAST(SUM(target_qty) AS DOUBLE), 2) AS plan_qty,
    ROUND(MAX(capa_val), 2) AS capa,
    CASE WHEN MAX(capa_val) > 0
         THEN ROUND(SUM(target_qty) / MAX(capa_val) * 100, 1)
         ELSE 0 END AS str_rate,
    100 AS base_line,
    0 AS sort_order
FROM base
WHERE fixed_date >= DATE '{from_date}' AND fixed_date <= DATE '{to_date}'
GROUP BY oper_group_id, fixed_date
ORDER BY date, sort_order, item_group_id
"""

# 공정 그룹별 수요별 상세 행
DETAIL_SQL = """
WITH base AS (
    SELECT
        t.oper_group_id,
        CASE WHEN CAST(t.target_datetime AS DATE) < DATE '{std_ts}'
             THEN DATE '{std_ts}'
             ELSE CAST(t.target_datetime AS DATE)
        END AS fixed_date,
        CASE
            WHEN json_extract_scalar(t.prop_json, '$.{uom_prop_key}') IS NULL
              OR json_extract_scalar(t.prop_json, '$.{uom_prop_key}') = 'DEFAULT'
            THEN t.out_target_qty
            ELSE t.out_target_conv_qty
        END AS target_qty,
        t.out_target_conv_qty AS conv_qty,
        CAST(json_extract_scalar(t.prop_json, '$.{capa_prop_key}') AS DOUBLE) AS capa_val,
        t.item_id,
        t.item_group_id,
        t.demand_id,
        CAST(t.due_date AS VARCHAR) AS due_date,
        t.oper_id,
        t.item_spec
    FROM rpt_oper_group_target t
    WHERE t.partition_key = '{partition_key}'
      AND t.plan_ver = '{plan_ver}'
      AND t.oper_group_id != '#Undefined'
      AND (t.demand_type IS NULL OR t.demand_type != '#Dummy')
      AND t.oper_id IS NOT NULL
      {oper_group_filter}
)
SELECT
    oper_group_id,
    CAST(fixed_date AS VARCHAR) AS str_date,
    ROUND(MAX(capa_val), 2) AS capa,
    ROUND(CAST(SUM(target_qty) AS DOUBLE), 2) AS str_qty,
    ROUND(CAST(SUM(conv_qty) AS DOUBLE), 1) AS outer_str_area,
    CASE WHEN MAX(capa_val) > 0
         THEN ROUND(SUM(target_qty) / MAX(capa_val) * 100, 1)
         ELSE 0 END AS str_rate,
    item_id,
    COALESCE(item_group_id, 'N/A') AS item_group_id,
    demand_id,
    due_date,
    oper_id
FROM base
WHERE fixed_date >= DATE '{from_date}' AND fixed_date <= DATE '{to_date}'
GROUP BY oper_group_id, fixed_date, item_id, item_group_id, demand_id, due_date, oper_id
ORDER BY oper_group_id, fixed_date, item_id
"""
