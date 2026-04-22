"""
APS C# 백엔드 프록시

FE → Python BE → C# BE 구조로 APS API를 중계합니다.
인증 헤더(Cookie 등)를 그대로 전달합니다.
"""

import logging

import httpx
from app.core.config import settings
from fastapi import APIRouter, Path, Request
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# APS API 경로 매핑: proxy path → (C# API path, HTTP method)
PROXY_ROUTES = {
    "demand-source": ("OdlReport", "POST"),
    "plan-cycle-info": ("PlmSysOperPlan/PlanCycleInfo", "GET"),
    "execution-flows": ("PlmExecutionFlowMaster", "GET"),
    "scenarios": ("PlmScenarioMaster", "GET"),
    "scenario-config": ("PlmScenarioMaster/Config/OptionConfigGlobal", "POST"),
    "scenario-modules": ("PlmScenarioMaster/Config/AllModules", "POST"),
    "inbound-scenario-config": ("PlmInboundScenarioMaster/Config", "POST"),
    "demand-ver": ("ComDemandVer", "POST"),
    "demand-ver-latest": ("MdmDemandVer/GetLastRev", "POST"),
    "demand-ver-check": ("MdmDemandVer", "GET"),
    "inbound": ("PlmPlanExecute/Inbound", "GET"),
    "plan-ver-info": ("PlmPlanExecute", "GET"),
    "execute": ("RarReExecutePlan/ReExecutePlan", "POST"),
    "save-widget": ("RarReExecutePlan/SaveWidget", "POST"),
    "get-widget": ("RarReExecutePlan/GetWidget", "POST"),
}


@router.api_route("/proxy/{proxy_path:path}", methods=["GET", "POST"])
async def proxy_to_aps(
    proxy_path: str,
    request: Request,
    project_id: str = Path(..., description="프로젝트 ID"),
):
    """APS C# 백엔드로 요청을 프록시합니다."""
    route_info = PROXY_ROUTES.get(proxy_path)
    if not route_info:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": f"Unknown proxy path: {proxy_path}"},
        )

    aps_path, method = route_info
    aps_url = f"{settings.APS_BACKEND_BASE_URL}/api/aps/backend/{project_id}/{aps_path}"

    # 요청 본문 읽기
    body = await request.body()

    # 원본 요청 헤더에서 인증 관련 헤더 전달
    forward_headers = {}
    for key in ["cookie", "authorization", "content-type"]:
        if key in request.headers:
            forward_headers[key] = request.headers[key]
    if "content-type" not in forward_headers:
        forward_headers["content-type"] = "application/json"

    try:
        async with httpx.AsyncClient(timeout=settings.QUERY_TIMEOUT_SECONDS) as client:
            if method == "GET":
                # GET 요청: body를 query params로 변환
                import json
                params = {}
                if body:
                    try:
                        params = json.loads(body)
                    except (json.JSONDecodeError, ValueError):
                        pass
                resp = await client.get(aps_url, params=params, headers=forward_headers)
            else:
                resp = await client.post(aps_url, content=body, headers=forward_headers)

        # C# 응답을 그대로 전달
        if resp.status_code == 401:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "APS 인증이 필요합니다. 로그인 후 다시 시도하세요."},
            )

        try:
            content = resp.json()
        except Exception:
            content = {"data": resp.text} if resp.text else {"success": resp.is_success}

        return JSONResponse(status_code=resp.status_code, content=content)
    except httpx.ConnectError as e:
        logger.error(f"[APS Proxy] C# 백엔드 연결 실패: {aps_url} ({e})")
        content = {
            "success": False,
            "error": (
                "APS 백엔드에 연결할 수 없습니다. "
                "APS_BACKEND_BASE_URL 환경변수가 올바른 APS 호스트를 가리키는지 확인하세요."
            ),
        }
        if settings.DEBUG:
            content["target"] = aps_url
            content["detail"] = str(e)
        return JSONResponse(status_code=502, content=content)
    except Exception as e:
        logger.exception(f"[APS Proxy] 프록시 오류: {e}")
        content = {"success": False, "error": "APS 프록시 호출 중 오류가 발생했습니다."}
        if settings.DEBUG:
            content["target"] = aps_url
            content["detail"] = str(e)
        return JSONResponse(status_code=500, content=content)
