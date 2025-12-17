"""
API 라우터

Mozart Cloud Custom UI API 엔드포인트
"""

from app.services import ItemMasterService
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("")
async def get_item_master(
    project_id: str = Query(
        default="31C13202-5860-4123-8ACD-81C2373F1E73", description="프로젝트 ID"
    ),
    plan_ver: str = Query(default="20251017-M-01", description="Plan Version"),
):
    """
    odv_item_master 테이블을 조회합니다.

    Args:
        project_id: 프로젝트 ID
        plan_ver: Plan Version

    Returns:
        조회된 item master 목록
    """
    try:
        service = ItemMasterService()
        return service.get_item_master_list(project_id, plan_ver)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"조회 중 오류 발생: {str(e)}"},
        )
