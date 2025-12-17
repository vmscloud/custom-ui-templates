"""
Item Master 서비스
"""

from app.repositories.item_master import ItemMasterRepository


class ItemMasterService:
    """Item Master 비즈니스 로직"""

    def __init__(self):
        self.repository = ItemMasterRepository()

    def get_item_master_list(self, project_id: str, plan_ver: str) -> dict:
        """
        Item Master 목록 조회

        Args:
            project_id: 프로젝트 ID
            plan_ver: Plan Version

        Returns:
            조회 결과 딕셔너리
        """
        results = self.repository.get_by_project_and_plan_ver(project_id, plan_ver)

        return {
            "success": True,
            "count": len(results),
            "data": results,
        }
