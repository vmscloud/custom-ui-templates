"""
Plan Cycle 서비스
"""

from app.repositories.plan_cycle import PlanCycleRepository


class PlanCycleService:
    """Plan Cycle 비즈니스 로직"""

    def __init__(self):
        self.repository = PlanCycleRepository()

    def get_plan_cycle_with_ver(
        self,
        project_id: str,
        plan_cycle_id: str | None = None,
        plan_ver: str | None = None,
        skip: int = 0,
        take: int = 0,
        is_done: bool = True,
        exact: bool = False,
    ) -> dict:
        """
        Plan Cycle with Version 조회

        Args:
            project_id: 프로젝트 ID
            plan_cycle_id: Plan Cycle ID (선택)
            plan_ver: Plan Version (선택)
            skip: 건너뛸 레코드 수
            take: 가져올 레코드 수
            is_done: DONE/FROZEN 상태만 조회 여부
            exact: 정확한 매칭 여부

        Returns:
            조회 결과 딕셔너리
        """
        results = self.repository.get_plan_cycle_with_ver(
            project_id=project_id,
            plan_cycle_id=plan_cycle_id,
            plan_ver=plan_ver,
            skip=skip,
            take=take,
            is_done=is_done,
            exact=exact,
        )

        if results:
            return {
                "success": True,
                "count": len(results),
                "data": results,
            }
        else:
            return {
                "success": True,
                "count": 0,
                "data": [],
                "message": "NO_CONTENT",
            }

