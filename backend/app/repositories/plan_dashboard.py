"""
Plan Dashboard 레포지토리
"""

from app.core.database import execute_query, execute_write


class PlanDashboardRepository:
    """Plan Dashboard 데이터 접근"""

    @staticmethod
    def get_frozen_ver(project_id: str, plan_ver: str) -> str:
        """
        주어진 planVer에 대한 frozen version을 조회합니다.

        Args:
            project_id: 프로젝트 ID
            plan_ver: Plan Version

        Returns:
            Frozen version 문자열. 없으면 원래 plan_ver 반환
        """
        # Step 1: plan_ver로 plan_cycle_id 조회
        cycle_query = """
        SELECT plan_cycle_id
        FROM cfg_plan_config
        WHERE project_id = %s AND plan_ver = %s
        LIMIT 1
        """
        cycle_rows = execute_query(cycle_query, (project_id, plan_ver))

        if not cycle_rows:
            return plan_ver

        plan_cycle_id = cycle_rows[0]["plan_cycle_id"]

        # Step 2: 해당 cycle에서 FROZEN 상태인 version 조회
        frozen_query = """
        SELECT config.plan_ver
        FROM cfg_plan_config config
        INNER JOIN sys_plan_ctrl ctrl
            ON config.project_id = ctrl.project_id
            AND config.plan_ver = ctrl.plan_ver
        WHERE config.project_id = %s
            AND config.plan_cycle_id = %s
            AND ctrl.plan_status = 'FROZEN'
        ORDER BY ctrl.sched_datetime DESC
        LIMIT 1
        """
        frozen_rows = execute_query(
            frozen_query, (project_id, plan_cycle_id)
        )

        if not frozen_rows:
            return plan_ver

        return frozen_rows[0]["plan_ver"]

    @staticmethod
    def get_all_widget_settings(
        project_id: str, user_id: str, menu_id: str
    ) -> list[dict]:
        """
        사용자의 메뉴별 전체 위젯 설정을 조회합니다.

        Args:
            project_id: 프로젝트 ID
            user_id: 사용자 ID
            menu_id: 메뉴 ID

        Returns:
            위젯 설정 목록
        """
        query = """
        SELECT widget_id, widget_value
        FROM dp_user_widget_config
        WHERE project_id = %s AND user_id = %s AND menu_id = %s
        """
        return execute_query(query, (project_id, user_id, menu_id))

    @staticmethod
    def get_widget_setting(
        project_id: str, user_id: str, menu_id: str, widget_id: str
    ) -> dict | None:
        """
        단일 위젯 설정을 조회합니다.

        Args:
            project_id: 프로젝트 ID
            user_id: 사용자 ID
            menu_id: 메뉴 ID
            widget_id: 위젯 ID

        Returns:
            위젯 설정 dict 또는 None
        """
        query = """
        SELECT widget_id, widget_value
        FROM dp_user_widget_config
        WHERE project_id = %s AND user_id = %s AND menu_id = %s AND widget_id = %s
        LIMIT 1
        """
        rows = execute_query(
            query, (project_id, user_id, menu_id, widget_id)
        )

        if not rows:
            return None

        return rows[0]

    @staticmethod
    def save_widget_setting(
        project_id: str,
        user_id: str,
        menu_id: str,
        widget_id: str,
        widget_value: str,
    ) -> int:
        """
        위젯 설정을 저장합니다 (UPSERT).

        Args:
            project_id: 프로젝트 ID
            user_id: 사용자 ID
            menu_id: 메뉴 ID
            widget_id: 위젯 ID
            widget_value: 위젯 설정 값

        Returns:
            영향받은 행 수
        """
        query = """
        INSERT INTO dp_user_widget_config
            (project_id, user_id, menu_id, widget_id, widget_value,
             create_datetime, create_user_id, update_datetime, update_user_id)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s, NOW(), %s)
        ON CONFLICT (project_id, user_id, menu_id, widget_id)
        DO UPDATE SET
            widget_value = EXCLUDED.widget_value,
            update_datetime = NOW(),
            update_user_id = EXCLUDED.update_user_id
        """
        return execute_write(
            query,
            (
                project_id,
                user_id,
                menu_id,
                widget_id,
                widget_value,
                user_id,
                user_id,
            ),
        )

    @staticmethod
    def get_error_log_master() -> list[dict]:
        """
        에러 심각도 유형 목록을 조회합니다.
        at_error_log_master는 프로젝트 무관 글로벌 마스터 테이블.

        Returns:
            에러 심각도 목록
        """
        query = """
        SELECT DISTINCT severity
        FROM at_error_log_master
        ORDER BY severity
        """
        return execute_query(query)
