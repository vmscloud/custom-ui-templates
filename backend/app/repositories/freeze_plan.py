"""Freeze Plan 레포지토리 — PostgreSQL 직접 접근"""
from app.core.database import execute_query, execute_write

class FreezePlanRepository:

    @staticmethod
    def get_frozen_status(project_id: str, plan_cycle_id: str) -> list[dict]:
        """cfg_plan_cycle_info에서 frozen 상태 조회"""
        query = """
        SELECT project_id, plan_cycle_id, status, frozen_plan_ver, frozen_desc,
               cycle_start_date, cycle_end_date, frozen_end_datetime
        FROM cfg_plan_cycle_info
        WHERE project_id = %s AND plan_cycle_id = %s
        """
        return execute_query(query, (project_id, plan_cycle_id))

    @staticmethod
    def update_frozen_desc(project_id: str, plan_cycle_id: str, description: str) -> int:
        """frozen 설명 업데이트"""
        query = """
        UPDATE cfg_plan_cycle_info
        SET frozen_desc = %s, update_datetime = NOW()
        WHERE project_id = %s AND plan_cycle_id = %s
        """
        return execute_write(query, (description, project_id, plan_cycle_id))

    @staticmethod
    def freeze_plan(project_id: str, plan_ver: str, plan_cycle_id: str, user_id: str, description: str = "") -> int:
        """계획 확정 실행 — cfg_plan_cycle_info + sys_plan_ctrl 업데이트"""
        from app.core.database import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. cfg_plan_cycle_info 업데이트
                cur.execute("""
                    UPDATE cfg_plan_cycle_info
                    SET frozen_plan_ver = %s,
                        status = 'close',
                        frozen_end_datetime = NOW(),
                        frozen_desc = %s,
                        update_datetime = NOW(),
                        update_user_id = %s
                    WHERE project_id = %s AND plan_cycle_id = %s
                """, (plan_ver, description, user_id, project_id, plan_cycle_id))

                # 2. sys_plan_ctrl 업데이트
                cur.execute("""
                    UPDATE sys_plan_ctrl
                    SET plan_status = 'FROZEN',
                        update_datetime = NOW(),
                        update_user_id = %s
                    WHERE project_id = %s AND plan_ver = %s
                """, (user_id, project_id, plan_ver))

                return cur.rowcount

    @staticmethod
    def unfreeze_plan(project_id: str, plan_ver: str, plan_cycle_id: str, user_id: str) -> int:
        """계획 확정 취소"""
        from app.core.database import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE cfg_plan_cycle_info
                    SET frozen_plan_ver = '',
                        status = 'open',
                        frozen_end_datetime = NULL,
                        frozen_desc = '',
                        update_datetime = NOW(),
                        update_user_id = %s
                    WHERE project_id = %s AND plan_cycle_id = %s
                """, (user_id, project_id, plan_cycle_id))

                cur.execute("""
                    UPDATE sys_plan_ctrl
                    SET plan_status = 'DONE',
                        update_datetime = NOW(),
                        update_user_id = %s
                    WHERE project_id = %s AND plan_ver = %s
                """, (user_id, project_id, plan_ver))

                return cur.rowcount

    @staticmethod
    def get_frozen_period(project_id: str, plan_ver: str) -> list[dict]:
        """frozen 기간 조회"""
        query = """
        SELECT ci.plan_cycle_id, ci.cycle_start_date, ci.cycle_end_date,
               ci.frozen_end_datetime, ci.frozen_plan_ver, ci.status,
               config.plan_start_datetime, config.plan_period
        FROM cfg_plan_cycle_info ci
        INNER JOIN cfg_plan_config config
            ON ci.project_id = config.project_id
            AND ci.plan_cycle_id = config.plan_cycle_id
        WHERE ci.project_id = %s
          AND config.plan_ver = %s
        LIMIT 1
        """
        return execute_query(query, (project_id, plan_ver))
