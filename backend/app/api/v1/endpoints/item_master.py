"""
API 라우터

Mozart Cloud Custom UI API 엔드포인트
"""

import time

from app.schemas.query import (
    QueryRequest,
    QueryResult,
)
from app.services import ItemMasterService
from app.services.query_execute_service import (
    QueryExecuteService,
    get_query_execute_service,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("")
async def get_item_master(
    project_id: str = Path(..., description="프로젝트 ID"),
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


@router.post("/stored-query", response_model=QueryResult)
async def execute_query(
    request: QueryRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: QueryExecuteService = Depends(get_query_execute_service),
):
    """SELECT 쿼리 실행"""
    try:
        start_time = time.time()

        result = await service.execute(
            query_id="odv_item_master_list",
            parameters=request.parameters,
            project_id=project_id,
        )
        execution_time = (time.time() - start_time) * 1000

        return QueryResult(
            columns=result["columns"],
            rows=result["rows"],
            row_count=result["row_count"],
            execution_time_ms=round(execution_time, 2),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "statement_timeout" in error_msg.lower():
            raise HTTPException(
                status_code=408, detail="쿼리 실행 시간이 초과되었습니다."
            )
        raise HTTPException(status_code=500, detail=error_msg)
