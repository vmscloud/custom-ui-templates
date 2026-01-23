"""
Plan Cycle 레포지토리
"""

from app.core.database import execute_query


class PlanCycleRepository:
    """Plan Cycle 데이터 접근"""

    @staticmethod
    def get_plan_cycle_with_ver(
        project_id: str,
        plan_cycle_id: str | None = None,
        plan_ver: str | None = None,
        skip: int = 0,
        take: int = 0,
        is_done: bool = True,
        exact: bool = False,
    ) -> list[dict]:
        """
        Plan Cycle과 Version 정보를 조회합니다.

        Args:
            project_id: 프로젝트 ID
            plan_cycle_id: Plan Cycle ID (선택, 필터링용)
            plan_ver: Plan Version (선택, exact=True일 때 필터링용)
            skip: 건너뛸 레코드 수
            take: 가져올 레코드 수 (0이면 제한 없음)
            is_done: True면 DONE/FROZEN 상태만, False면 RUN/BOOK/INBOUND/CREATE 제외
            exact: True면 정확한 매칭, False면 주변 데이터 포함

        Returns:
            조회된 Plan Cycle with Version 목록
        """
        if exact:
            return PlanCycleRepository._get_exact_query(
                project_id, plan_cycle_id, plan_ver, skip, take, is_done
            )
        else:
            return PlanCycleRepository._get_fuzzy_query(
                project_id, plan_cycle_id, is_done
            )

    @staticmethod
    def _get_exact_query(
        project_id: str,
        plan_cycle_id: str | None,
        plan_ver: str | None,
        skip: int,
        take: int,
        is_done: bool,
    ) -> list[dict]:
        """exact=True일 때의 쿼리"""

        # Plan status 조건
        plan_status_condition = (
            "AND ctrl.plan_status IN ('DONE', 'FROZEN')"
            if is_done
            else "AND ctrl.plan_status NOT IN ('RUN', 'BOOK', 'INBOUND', 'CREATE')"
        )

        # Plan cycle ID 필터
        plan_cycle_filter = ""
        if plan_cycle_id:
            plan_cycle_filter = "AND ci.plan_cycle_id ILIKE %s"

        # Plan ver 필터
        plan_ver_filter = ""
        if plan_ver:
            plan_ver_filter = "AND config.plan_ver ILIKE %s"

        # Pagination
        pagination = ""
        if take > 0:
            pagination = f"OFFSET {skip} ROWS FETCH NEXT {take} ROWS ONLY"

        query = f"""
        WITH limitedcycleinfo AS (
            SELECT ci.project_id
                 , ci.plan_cycle_id
                 , ci.start_datetime as start_date
                 , ci.end_datetime as end_date
                 , ci.status
                 , ci.cycle_create_type
                 , CASE
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN 'week'
                     WHEN ci.cycle_create_type = 7 THEN 'day'
                     ELSE 'manual'
                   END AS period_uom
                 , CASE
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN 7
                     WHEN ci.cycle_create_type = 7 THEN 1
                     ELSE 9999
                   END AS cycle_period
                 , CASE
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), ' ~ ', to_char(ci.start_datetime + interval '7 days', 'YYYY-MM-DD'), ')')
                     WHEN ci.cycle_create_type = 7 THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), ')')
                     WHEN ci.cycle_create_type = 9 AND status = 'open' THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), '~)')
                     WHEN ci.cycle_create_type = 9 AND status = 'close' THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), ' ~ ', to_char(ci.end_datetime, 'YYYY-MM-DD'), ')')
                     ELSE concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), '~)')
                   END AS display_date
                 , ci.frozen_plan_ver
                 , ci.frozen_end_datetime as frozen_end_date
            FROM cfg_plan_cycle_info ci
            WHERE ci.project_id = %s
            {plan_cycle_filter}
            ORDER BY ci.plan_cycle_id DESC
            {pagination}
        )
        , planver AS (
            SELECT config.plan_cycle_id
                 , config.plan_ver
                 , config.scenario_id
                 , config.plan_start_datetime as plan_start_date
                 , config.plan_start_datetime + INTERVAL '1 day' * config.plan_period AS plan_end_date
                 , config.plan_period
                 , config.plan_type
                 , config.execution_type
                 , config.description
                 , config.demand_ver
                 , ctrl.plan_status
                 , config.create_user_id
                 , config.update_user_id
                 , config.create_datetime
                 , config.update_datetime
            FROM cfg_plan_config config
            INNER JOIN sys_plan_ctrl ctrl
                ON config.project_id = ctrl.project_id AND config.plan_ver = ctrl.plan_ver
                {plan_status_condition}
            WHERE config.project_id = %s
            {plan_ver_filter}
            ORDER BY config.update_datetime DESC
        )
        SELECT c.project_id
             , c.plan_cycle_id
             , c.start_date
             , c.end_date
             , c.status
             , c.frozen_plan_ver
             , c.frozen_end_date
             , c.cycle_period
             , c.period_uom
             , c.display_date
             , v.plan_ver
             , v.scenario_id
             , v.plan_start_date
             , v.plan_end_date
             , v.plan_period
             , v.plan_type
             , v.execution_type
             , CASE WHEN v.description IS NULL OR v.description = '' THEN '(No Description)'
                    ELSE v.description END AS description
             , v.demand_ver
             , v.plan_status
             , v.create_user_id as create_user
             , v.update_user_id as update_user
             , v.create_datetime
             , v.update_datetime
             , CASE WHEN c.frozen_plan_ver = v.plan_ver THEN TRUE ELSE FALSE END AS is_frozen
        FROM limitedcycleinfo c
        INNER JOIN planver v ON c.plan_cycle_id = v.plan_cycle_id
        ORDER BY c.start_date DESC, v.create_datetime DESC
        """

        # Build parameters
        params = [project_id]
        if plan_cycle_id:
            params.append(f"%{plan_cycle_id}%")
        params.append(project_id)  # For planver CTE
        if plan_ver:
            params.append(f"%{plan_ver}%")

        return execute_query(query, tuple(params))

    @staticmethod
    def _get_fuzzy_query(
        project_id: str,
        plan_cycle_id: str | None,
        is_done: bool,
    ) -> list[dict]:
        """exact=False일 때의 쿼리 (주변 데이터 포함)"""

        # Plan status 조건
        plan_status_condition = (
            "AND ctrl.plan_status IN ('DONE', 'FROZEN')"
            if is_done
            else "AND ctrl.plan_status NOT IN ('RUN', 'BOOK', 'INBOUND', 'CREATE')"
        )

        # Plan cycle ID 필터
        plan_cycle_filter = ""
        if plan_cycle_id:
            plan_cycle_filter = "WHERE plan_cycle_id ILIKE %s"

        query = f"""
        WITH ordered AS (
            SELECT ci.*
                 , ROW_NUMBER() OVER (ORDER BY ci.plan_cycle_id DESC) AS rownum
            FROM cfg_plan_cycle_info ci
            WHERE ci.project_id = %s
        )
        , target AS (
            SELECT rownum
            FROM ordered
            {plan_cycle_filter}
        )
        , limitedcycleinfo AS (
            SELECT ci.project_id
                 , ci.plan_cycle_id
                 , ci.start_datetime as start_date
                 , ci.end_datetime as end_date
                 , ci.status
                 , ci.cycle_create_type
                 , CASE
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN 'week'
                     WHEN ci.cycle_create_type = 7 THEN 'day'
                     ELSE 'manual'
                   END AS period_uom
                 , CASE
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN 7
                     WHEN ci.cycle_create_type = 7 THEN 1
                     ELSE 9999
                   END AS cycle_period
                 , CASE
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), ' ~ ', to_char(ci.start_datetime + interval '7 days', 'YYYY-MM-DD'), ')')
                     WHEN ci.cycle_create_type = 7 THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), ')')
                     WHEN ci.cycle_create_type = 9 AND status = 'open' THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), '~)')
                     WHEN ci.cycle_create_type = 9 AND status = 'close' THEN concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), ' ~ ', to_char(ci.end_datetime, 'YYYY-MM-DD'), ')')
                     ELSE concat(ci.plan_cycle_id, ' (', to_char(ci.start_datetime, 'YYYY-MM-DD'), '~)')
                   END AS display_date
                 , ci.frozen_plan_ver
                 , ci.frozen_end_datetime as frozen_end_date
            FROM ordered ci
            WHERE (EXISTS (SELECT 1 FROM target) AND rownum BETWEEN
                    (SELECT GREATEST(1, MIN(rownum) - CEIL((11 - 1) / 2.0)) FROM target)
                AND
                    (SELECT GREATEST(11, MIN(rownum) + FLOOR((11 - 1) / 2.0)) FROM target))
               OR (NOT EXISTS (SELECT 1 FROM target) AND rownum <= 11)
            ORDER BY plan_cycle_id DESC
        )
        , planver AS (
            SELECT config.plan_cycle_id
                 , config.plan_ver
                 , config.scenario_id
                 , config.plan_start_datetime as plan_start_date
                 , config.plan_start_datetime + INTERVAL '1 day' * config.plan_period AS plan_end_date
                 , config.plan_period
                 , config.plan_type
                 , config.execution_type
                 , config.description
                 , config.demand_ver
                 , ctrl.plan_status
                 , config.create_user_id
                 , config.update_user_id
                 , config.create_datetime
                 , config.update_datetime
            FROM cfg_plan_config config
            INNER JOIN sys_plan_ctrl ctrl
                ON config.project_id = ctrl.project_id AND config.plan_ver = ctrl.plan_ver
                {plan_status_condition}
            WHERE config.project_id = %s
            ORDER BY config.update_datetime DESC
        )
        SELECT c.project_id
             , c.plan_cycle_id
             , c.start_date
             , c.end_date
             , c.status
             , c.frozen_plan_ver
             , c.frozen_end_date
             , c.cycle_period
             , c.period_uom
             , c.display_date
             , v.plan_ver
             , v.scenario_id
             , v.plan_start_date
             , v.plan_end_date
             , v.plan_period
             , v.plan_type
             , v.execution_type
             , CASE WHEN v.description IS NULL OR v.description = '' THEN '(No Description)'
                    ELSE v.description END AS description
             , v.demand_ver
             , v.plan_status
             , v.create_user_id as create_user
             , v.update_user_id as update_user
             , v.create_datetime
             , v.update_datetime
             , CASE WHEN c.frozen_plan_ver = v.plan_ver THEN TRUE ELSE FALSE END AS is_frozen
        FROM limitedcycleinfo c
        LEFT JOIN planver v ON c.plan_cycle_id = v.plan_cycle_id
        ORDER BY c.start_date DESC, v.create_datetime DESC
        """

        # Build parameters
        params = [project_id]
        if plan_cycle_id:
            params.append(f"%{plan_cycle_id}%")
        params.append(project_id)  # For planver CTE

        return execute_query(query, tuple(params))

