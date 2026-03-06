"""
Plan Cycle 레포지토리 (Trino)
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
        plan_status_condition = (
            "AND ctrl.plan_status IN ('DONE', 'FROZEN')"
            if is_done
            else "AND ctrl.plan_status NOT IN ('RUN', 'BOOK', 'INBOUND', 'CREATE')"
        )

        plan_cycle_filter = ""
        if plan_cycle_id:
            plan_cycle_filter = "AND LOWER(ci.plan_cycle_id) LIKE LOWER(?)"

        plan_ver_filter = ""
        if plan_ver:
            plan_ver_filter = "AND LOWER(config.plan_ver) LIKE LOWER(?)"

        pagination = ""
        if take > 0:
            pagination = f"OFFSET {skip} LIMIT {take}"

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
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), ' ~ ', date_format(date_add('day', 7, ci.start_datetime), '%Y-%m-%d'), ')')
                     WHEN ci.cycle_create_type = 7 THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), ')')
                     WHEN ci.cycle_create_type = 9 AND status = 'open' THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), '~)')
                     WHEN ci.cycle_create_type = 9 AND status = 'close' THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), ' ~ ', date_format(ci.end_datetime, '%Y-%m-%d'), ')')
                     ELSE CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), '~)')
                   END AS display_date
                 , ci.frozen_plan_ver
                 , ci.frozen_end_datetime as frozen_end_date
            FROM postgresql.mzc_aps.cfg_plan_cycle_info ci
            WHERE ci.project_id = ?
            {plan_cycle_filter}
            ORDER BY ci.plan_cycle_id DESC
            {pagination}
        )
        , planver AS (
            SELECT config.plan_cycle_id
                 , config.plan_ver
                 , config.scenario_id
                 , config.plan_start_datetime as plan_start_date
                 , date_add('day', config.plan_period, config.plan_start_datetime) AS plan_end_date
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
            FROM postgresql.mzc_aps.cfg_plan_config config
            INNER JOIN postgresql.mzc_aps.sys_plan_ctrl ctrl
                ON config.project_id = ctrl.project_id AND config.plan_ver = ctrl.plan_ver
                {plan_status_condition}
            WHERE config.project_id = ?
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

        params = [project_id]
        if plan_cycle_id:
            params.append(f"%{plan_cycle_id}%")
        params.append(project_id)
        if plan_ver:
            params.append(f"%{plan_ver}%")

        return execute_query(query, tuple(params))

    @staticmethod
    def _get_fuzzy_query(
        project_id: str,
        plan_cycle_id: str | None,
        is_done: bool,
    ) -> list[dict]:
        plan_status_condition = (
            "AND ctrl.plan_status IN ('DONE', 'FROZEN')"
            if is_done
            else "AND ctrl.plan_status NOT IN ('RUN', 'BOOK', 'INBOUND', 'CREATE')"
        )

        plan_cycle_filter = ""
        if plan_cycle_id:
            plan_cycle_filter = "WHERE LOWER(plan_cycle_id) LIKE LOWER(?)"

        query = f"""
        WITH ordered AS (
            SELECT ci.*
                 , ROW_NUMBER() OVER (ORDER BY ci.plan_cycle_id DESC) AS rownum
            FROM postgresql.mzc_aps.cfg_plan_cycle_info ci
            WHERE ci.project_id = ?
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
                     WHEN ci.cycle_create_type BETWEEN 0 AND 6 THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), ' ~ ', date_format(date_add('day', 7, ci.start_datetime), '%Y-%m-%d'), ')')
                     WHEN ci.cycle_create_type = 7 THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), ')')
                     WHEN ci.cycle_create_type = 9 AND status = 'open' THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), '~)')
                     WHEN ci.cycle_create_type = 9 AND status = 'close' THEN CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), ' ~ ', date_format(ci.end_datetime, '%Y-%m-%d'), ')')
                     ELSE CONCAT(ci.plan_cycle_id, ' (', date_format(ci.start_datetime, '%Y-%m-%d'), '~)')
                   END AS display_date
                 , ci.frozen_plan_ver
                 , ci.frozen_end_datetime as frozen_end_date
            FROM ordered ci
            WHERE (EXISTS (SELECT 1 FROM target) AND rownum BETWEEN
                    (SELECT GREATEST(1, MIN(rownum) - CAST(CEILING((11 - 1) / 2.0) AS INTEGER)) FROM target)
                AND
                    (SELECT GREATEST(11, MIN(rownum) + CAST(FLOOR((11 - 1) / 2.0) AS INTEGER)) FROM target))
               OR (NOT EXISTS (SELECT 1 FROM target) AND rownum <= 11)
            ORDER BY plan_cycle_id DESC
        )
        , planver AS (
            SELECT config.plan_cycle_id
                 , config.plan_ver
                 , config.scenario_id
                 , config.plan_start_datetime as plan_start_date
                 , date_add('day', config.plan_period, config.plan_start_datetime) AS plan_end_date
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
            FROM postgresql.mzc_aps.cfg_plan_config config
            INNER JOIN postgresql.mzc_aps.sys_plan_ctrl ctrl
                ON config.project_id = ctrl.project_id AND config.plan_ver = ctrl.plan_ver
                {plan_status_condition}
            WHERE config.project_id = ?
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

        params = [project_id]
        if plan_cycle_id:
            params.append(f"%{plan_cycle_id}%")
        params.append(project_id)

        return execute_query(query, tuple(params))
