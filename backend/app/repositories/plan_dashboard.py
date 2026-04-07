"""
Plan Dashboard 레포지토리
"""

from app.core.database import execute_query, execute_write


class PlanDashboardRepository:
    """Plan Dashboard 데이터 접근"""

    @staticmethod
    def get_frozen_ver(project_id: str, plan_ver: str) -> str:
        """주어진 planVer에 대한 frozen version을 조회합니다."""
        # Step 1: plan_ver로 plan_cycle_id 조회
        cycle_rows = execute_query(
            f"SELECT plan_cycle_id FROM cfg_plan_config WHERE project_id = '{project_id}' AND plan_ver = '{plan_ver}' LIMIT 1"
        )
        if not cycle_rows:
            return plan_ver

        plan_cycle_id = cycle_rows[0]["plan_cycle_id"]

        # Step 2: 해당 cycle에서 FROZEN 상태인 version 조회
        frozen_rows = execute_query(
            f"""SELECT config.plan_ver
            FROM cfg_plan_config config
            INNER JOIN sys_plan_ctrl ctrl
                ON config.project_id = ctrl.project_id
                AND config.plan_ver = ctrl.plan_ver
            WHERE config.project_id = '{project_id}'
                AND config.plan_cycle_id = '{plan_cycle_id}'
                AND ctrl.plan_status = 'FROZEN'
            ORDER BY ctrl.sched_datetime DESC
            LIMIT 1"""
        )
        if not frozen_rows:
            return plan_ver

        return frozen_rows[0]["plan_ver"]

    @staticmethod
    def get_all_widget_settings(
        project_id: str, user_id: str, menu_id: str
    ) -> list[dict]:
        """사용자의 메뉴별 전체 위젯 설정을 조회합니다."""
        return execute_query(
            f"SELECT widget_id, widget_value FROM dp_user_widget_config WHERE project_id = '{project_id}' AND user_id = '{user_id}' AND menu_id = '{menu_id}'"
        )

    @staticmethod
    def get_widget_setting(
        project_id: str, user_id: str, menu_id: str, widget_id: str
    ) -> dict | None:
        """단일 위젯 설정을 조회합니다."""
        rows = execute_query(
            f"SELECT widget_id, widget_value FROM dp_user_widget_config WHERE project_id = '{project_id}' AND user_id = '{user_id}' AND menu_id = '{menu_id}' AND widget_id = '{widget_id}' LIMIT 1"
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
        """위젯 설정을 저장합니다 (UPSERT)."""
        # Trino(PostgreSQL 카탈로그) — MERGE 문 사용
        # 먼저 존재 여부 확인
        existing = execute_query(
            f"SELECT 1 FROM dp_user_widget_config WHERE project_id = '{project_id}' AND user_id = '{user_id}' AND menu_id = '{menu_id}' AND widget_id = '{widget_id}' LIMIT 1"
        )
        # Trino PostgreSQL connector에서는 INSERT/UPDATE 직접 실행
        escaped_value = widget_value.replace("'", "''")
        if existing:
            return execute_write(
                f"UPDATE dp_user_widget_config SET widget_value = '{escaped_value}', update_datetime = CURRENT_TIMESTAMP, update_user_id = '{user_id}' WHERE project_id = '{project_id}' AND user_id = '{user_id}' AND menu_id = '{menu_id}' AND widget_id = '{widget_id}'"
            )
        else:
            return execute_write(
                f"INSERT INTO dp_user_widget_config (project_id, user_id, menu_id, widget_id, widget_value, create_datetime, create_user_id, update_datetime, update_user_id) VALUES ('{project_id}', '{user_id}', '{menu_id}', '{widget_id}', '{escaped_value}', CURRENT_TIMESTAMP, '{user_id}', CURRENT_TIMESTAMP, '{user_id}')"
            )

    @staticmethod
    def get_plan_cycle_dates(project_id: str, plan_ver: str) -> dict:
        """Plan cycle의 시작/종료 날짜를 조회합니다 (OTD bucket 분류용)."""
        rows = execute_query(
            f"""SELECT
                ci.start_datetime AS cycle_start,
                ci.end_datetime AS cycle_end
            FROM cfg_plan_config c
            INNER JOIN cfg_plan_cycle_info ci
                ON c.project_id = ci.project_id AND c.plan_cycle_id = ci.plan_cycle_id
            WHERE c.project_id = '{project_id}' AND c.plan_ver = '{plan_ver}'
            LIMIT 1"""
        )
        if not rows:
            raise ValueError(f"Plan cycle not found for {plan_ver}")

        row = rows[0]
        cycle_start = str(row["cycle_start"])[:10]
        cycle_end = str(row["cycle_end"])[:10]

        # next_cycle_end: cycle_end에서 한 달 더
        from datetime import datetime
        end_dt = datetime.strptime(cycle_end, "%Y-%m-%d")
        if end_dt.month == 12:
            next_end = end_dt.replace(year=end_dt.year + 1, month=1)
        else:
            next_end = end_dt.replace(month=end_dt.month + 1)
        next_cycle_end = next_end.strftime("%Y-%m-%d")

        return {
            "cycle_start": cycle_start,
            "cycle_end": cycle_end,
            "next_cycle_end": next_cycle_end,
        }

    @staticmethod
    def get_error_log_master() -> list[dict]:
        """에러 심각도 유형 목록을 조회합니다."""
        return execute_query(
            "SELECT DISTINCT severity FROM at_error_log_master ORDER BY severity"
        )
