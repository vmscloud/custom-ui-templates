"""
Demand Distribution 레포지토리

Demand Version과 Distribution 데이터 조회를 위한 SQL 쿼리
"""

from app.core.database import execute_query


class DemandDistributionRepository:
    """Demand Distribution 데이터 접근"""

    @staticmethod
    def get_demand_versions(project_id: str) -> list[dict]:
        """
        Demand Version 목록 조회

        Args:
            project_id: 프로젝트 ID

        Returns:
            Demand Version 목록
        """
        query = """
        SELECT
            dv.project_id,
            dv.plan_cycle_id,
            dv.demand_ver,
            dv.demand_type,
            dv.description,
            dv.fix_datetime,
            dv.create_datetime,
            dv.create_user_id as create_user,
            dv.update_datetime,
            dv.update_user_id as update_user,
            CONCAT(dv.demand_ver,
                   CASE WHEN dv.description IS NOT NULL AND dv.description != ''
                        THEN CONCAT(' (', dv.description, ')')
                        ELSE ''
                   END) as display_text
        FROM cfg_demand_ver dv
        WHERE dv.project_id = %s
          AND (dv.demand_type IS NULL OR dv.demand_type != 'plan')
        ORDER BY dv.create_datetime DESC
        """
        return execute_query(query, (project_id,))

    @staticmethod
    def get_demand_distribution(
        project_id: str,
        demand_ver: str,
        aggregate_type: str = "month",
        summary: str = "sum",
        uom_type: str = "QTY",
    ) -> list[dict]:
        """
        Demand Distribution 데이터 조회

        Args:
            project_id: 프로젝트 ID
            demand_ver: Demand Version
            aggregate_type: 집계 타입 (day/week/month)
            summary: 집계 방식 (sum/count)
            uom_type: UOM 타입

        Returns:
            Demand Distribution 데이터 목록
        """
        # 날짜 집계 표현식
        date_expr = DemandDistributionRepository._get_date_expression(aggregate_type)

        query = f"""
        SELECT
            d.item_id,
            COALESCE(i.item_name, d.item_id) as item_name,
            d.cust_id,
            {date_expr} as due_date,
            COALESCE(i.item_group_id, '') as item_group_id,
            COALESCE(i.item_size_type, '') as item_size_type,
            COALESCE(i.prod_type, '') as prod_type,
            d.prop01, d.prop02, d.prop03, d.prop04, d.prop05,
            d.prop06, d.prop07, d.prop08, d.prop09, d.prop10,
            CASE
                WHEN %s = 'sum' THEN SUM(d.demand_qty)
                ELSE COUNT(DISTINCT d.item_id)
            END as qty,
            COUNT(DISTINCT d.item_id) as item_cnt,
            %s as qty_uom
        FROM cfg_demand d
        LEFT JOIN cfg_item_master i
            ON d.project_id = i.project_id AND d.item_id = i.item_id
        WHERE d.project_id = %s
          AND d.demand_ver = %s
        GROUP BY
            d.item_id, i.item_name, d.cust_id, {date_expr},
            i.item_group_id, i.item_size_type, i.prod_type,
            d.prop01, d.prop02, d.prop03, d.prop04, d.prop05,
            d.prop06, d.prop07, d.prop08, d.prop09, d.prop10
        ORDER BY {date_expr}, d.item_id
        """
        return execute_query(
            query, (summary, uom_type, project_id, demand_ver)
        )

    @staticmethod
    def _get_date_expression(aggregate_type: str) -> str:
        """
        집계 타입에 따른 날짜 표현식 반환

        Args:
            aggregate_type: WEEK/MONTH/YEAR

        Returns:
            SQL 날짜 표현식
        """
        agg_upper = aggregate_type.upper()
        if agg_upper == "YEAR":
            return "TO_CHAR(d.due_datetime, 'YYYY-01-01')"
        elif agg_upper == "MONTH":
            return "TO_CHAR(d.due_datetime, 'YYYY-MM-01')"
        elif agg_upper == "WEEK":
            return "TO_CHAR(DATE_TRUNC('week', d.due_datetime), 'YYYY-MM-DD')"
        else:  # DAY or default
            return "TO_CHAR(d.due_datetime, 'YYYY-MM-DD')"

    @staticmethod
    def get_demand_distribution_columns(project_id: str) -> list[dict]:
        """
        Demand Distribution 컬럼 정보 조회 (고정 컬럼)

        Args:
            project_id: 프로젝트 ID

        Returns:
            컬럼 메타데이터 목록
        """
        # 동적 컬럼 조회 대신 고정 컬럼 반환
        return []

    @staticmethod
    def get_uom_preference(
        project_id: str,
        user_id: str,
        menu_id: str | None = None,
    ) -> dict | None:
        """
        UOM Type 사용자 설정 조회

        우선순위: user_setting_value > project_setting_value > default_value

        Args:
            project_id: 프로젝트 ID
            user_id: 사용자 ID
            menu_id: 메뉴 ID (선택)

        Returns:
            UOM 설정 정보 또는 None
        """
        menu_filter = ""
        params = [project_id, user_id]

        if menu_id:
            menu_filter = "AND menu_id = %s"
            params.append(menu_id)

        query = f"""
        SELECT
            user_setting_value,
            project_setting_value,
            default_value
        FROM dp_uom_type
        WHERE project_id = %s
          AND user_id = %s
          {menu_filter}
        LIMIT 1
        """
        results = execute_query(query, tuple(params))
        return results[0] if results else None
