"""
RTF Report API 라우터

RTF(Ready-To-Fill) Report 데이터 조회 API 엔드포인트
QueryExecutorAdapter를 통해 Query Manager에 등록된 쿼리를 실행합니다.
"""

from app.schemas.rtf_report import (
    RtfBomMapRequest,
    RtfBufferPlanTargetRequest,
    RtfDemandRecordRequest,
    RtfDemandRequest,
    RtfDemandSummaryRequest,
    RtfDetailRequest,
    RtfItemPropsRequest,
    RtfSummaryRequest,
)
from app.services.rtf_report import RtfReportService, get_rtf_report_service
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

router = APIRouter()


# ============================================================================
# 핵심 데이터 API (POST)
# ============================================================================


@router.post("/summary")
async def get_summary(
    params: RtfSummaryRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    RTF 요약 그리드 데이터 조회

    기간/고객/품목그룹/지역/수요유형별 수요 충족률(On-Time, Late, Short) 집계
    """
    try:
        return await service.get_summary(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"요약 조회 중 오류 발생: {e}"},
        )


@router.post("/detail")
async def get_detail(
    params: RtfDetailRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    RTF 상세 그리드 데이터 조회

    요약 그리드에서 선택한 행의 개별 수요 상세 데이터
    """
    try:
        return await service.get_detail(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"상세 조회 중 오류 발생: {e}"},
        )


@router.post("/short")
async def get_short(
    params: RtfDemandRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    부족(Short) 사유 조회

    선택된 수요의 부족 사유 상세 정보
    """
    try:
        return await service.get_short(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Short 사유 조회 중 오류 발생: {e}"},
        )


@router.post("/prod-detail")
async def get_prod_detail(
    params: RtfDemandRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    생산계획 피벗 데이터 조회

    수요별 생산 계획 상세 (ExtendPivotGrid용)
    """
    try:
        return await service.get_prod_detail(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"생산 상세 조회 중 오류 발생: {e}"},
        )


@router.post("/buffer-plan-target")
async def get_buffer_plan_target(
    params: RtfBufferPlanTargetRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    버퍼 계획 Target vs 실적 조회
    """
    try:
        return await service.get_buffer_plan_target(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"버퍼 계획 조회 중 오류 발생: {e}"},
        )


@router.post("/demand-summary")
async def get_demand_summary(
    params: RtfDemandSummaryRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    수요 요약 메트릭 조회

    선택된 수요의 충족 메트릭 요약 (수요량, 출하량, WIP, Peg 비율 등)
    """
    try:
        return await service.get_demand_summary(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"수요 요약 조회 중 오류 발생: {e}"},
        )


@router.post("/demand-info")
async def get_demand_info(
    params: RtfDemandRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    수요 상세 정보 조회 (모달)
    """
    try:
        return await service.get_demand_info(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"수요 정보 조회 중 오류 발생: {e}"},
        )


@router.post("/peg-info")
async def get_peg_info(
    params: RtfDemandRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    Peg 정보 상세 조회 (모달)
    """
    try:
        return await service.get_peg_info(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Peg 정보 조회 중 오류 발생: {e}"},
        )


@router.post("/bom-map")
async def get_bom_map(
    params: RtfBomMapRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    BOM 구조 조회 (모달)
    """
    try:
        return await service.get_bom_map(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"BOM 구조 조회 중 오류 발생: {e}"},
        )


@router.post("/item-props")
async def get_item_props(
    params: RtfItemPropsRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    품목 속성 조회 (모달)
    """
    try:
        return await service.get_item_props(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"품목 속성 조회 중 오류 발생: {e}"},
        )


@router.post("/demand-record")
async def get_demand_record(
    params: RtfDemandRecordRequest,
    project_id: str = Path(..., description="프로젝트 ID"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """
    수요 레코드 상세 조회 (모달)
    """
    try:
        return await service.get_demand_record(project_id, params)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"수요 레코드 조회 중 오류 발생: {e}"},
        )


# ============================================================================
# 필터 API (GET)
# ============================================================================


@router.get("/filters/customers")
async def get_filter_customers(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., description="Plan Version"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """고객 필터 목록 조회"""
    try:
        return await service.get_filter_customers(project_id, plan_ver)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"고객 목록 조회 중 오류 발생: {e}"},
        )


@router.get("/filters/item-groups")
async def get_filter_item_groups(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., description="Plan Version"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """품목 그룹 필터 목록 조회"""
    try:
        return await service.get_filter_item_groups(project_id, plan_ver)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"품목 그룹 목록 조회 중 오류 발생: {e}",
            },
        )


@router.get("/filters/regions")
async def get_filter_regions(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., description="Plan Version"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """지역 필터 목록 조회"""
    try:
        return await service.get_filter_regions(project_id, plan_ver)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"지역 목록 조회 중 오류 발생: {e}"},
        )


@router.get("/filters/demand-types")
async def get_filter_demand_types(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., description="Plan Version"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """수요 유형 필터 목록 조회"""
    try:
        return await service.get_filter_demand_types(project_id, plan_ver)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"수요 유형 목록 조회 중 오류 발생: {e}",
            },
        )


@router.get("/filters/prop-columns")
async def get_filter_prop_columns(
    project_id: str = Path(..., description="프로젝트 ID"),
    plan_ver: str = Query(..., description="Plan Version"),
    service: RtfReportService = Depends(get_rtf_report_service),
):
    """동적 속성 컬럼 정의 조회"""
    try:
        return await service.get_filter_prop_columns(project_id, plan_ver)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"속성 컬럼 조회 중 오류 발생: {e}",
            },
        )
