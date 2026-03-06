"""
Plan Cycle API 라우터

Plan Cycle과 Version 정보를 조회하는 API 엔드포인트
"""

from typing import Optional

from app.services.plan_cycle import PlanCycleService
from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class ComQuery(BaseModel):
    """Plan Cycle 조회 요청 파라미터"""

    planCycleID: Optional[str] = Field(default=None, description="Plan Cycle ID (부분 매칭)")
    planVer: Optional[str] = Field(default=None, description="Plan Version (부분 매칭, exact=True일 때)")
    skip: int = Field(default=0, ge=0, description="건너뛸 레코드 수")
    take: int = Field(default=0, ge=0, description="가져올 레코드 수 (0이면 제한 없음)")
    isDone: bool = Field(default=True, description="DONE/FROZEN 상태만 조회 여부")
    exact: Optional[bool] = Field(default=False, description="정확한 매칭 여부")


@router.post("/planCycleSource")
def get_plan_cycle_with_ver(
    project_id: str = Path(..., description="프로젝트 ID"),
    param: ComQuery = None,
):
    """
    Plan Cycle과 Version 정보를 조회합니다.

    - **project_id**: 프로젝트 ID (필수)
    - **planCycleID**: Plan Cycle ID로 필터링 (선택, 부분 매칭)
    - **planVer**: Plan Version으로 필터링 (선택, exact=True일 때 부분 매칭)
    - **skip**: 건너뛸 레코드 수 (페이지네이션)
    - **take**: 가져올 레코드 수 (0이면 제한 없음)
    - **isDone**: True면 DONE/FROZEN 상태만, False면 RUN/BOOK/INBOUND/CREATE 제외
    - **exact**: True면 정확한 페이지네이션, False면 주변 데이터 포함

    Sample request:
    ```json
    {
        "skip": 0,
        "take": 20,
        "isDone": true
    }
    ```

    Returns:
        Plan Cycle with Version 목록
    """
    try:
        if param is None:
            param = ComQuery()

        # exact가 None이면 False로 설정
        exact = param.exact if param.exact is not None else False

        service = PlanCycleService()
        result = service.get_plan_cycle_with_ver(
            project_id=project_id,
            plan_cycle_id=param.planCycleID,
            plan_ver=param.planVer,
            skip=param.skip,
            take=param.take,
            is_done=param.isDone,
            exact=exact,
        )

        return result

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred: {str(e)}"},
        )

