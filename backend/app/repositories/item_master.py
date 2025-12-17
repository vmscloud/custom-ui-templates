"""
Item Master 레포지토리
"""

from app.core.database import execute_query


class ItemMasterRepository:
    """odv_item_master 테이블 데이터 접근"""

    @staticmethod
    def get_by_project_and_plan_ver(project_id: str, plan_ver: str) -> list[dict]:
        """
        프로젝트 ID와 Plan Version으로 Item Master 조회

        Args:
            project_id: 프로젝트 ID
            plan_ver: Plan Version

        Returns:
            조회된 Item Master 목록
        """
        query = """
            SELECT *
            FROM odv_item_master
            WHERE project_id = %s
              AND plan_ver = %s
        """
        return execute_query(query, (project_id, plan_ver))
