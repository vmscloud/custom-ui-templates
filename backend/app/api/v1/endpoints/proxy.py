"""
APS 백엔드 프록시 API 라우터

RTF Report에서 BomMap, PlanByProd, Pegging 등
원본 APS 백엔드 API를 프록시합니다.
"""

from typing import Any

import httpx
from app.core.config import settings
from fastapi import APIRouter, Path, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class ApsProxyRequest(BaseModel):
    """APS 프록시 요청 모델"""

    url: str = Field(..., description="APS API URL (예: RarBomMapViewNew/GetBomResList)")
    param: dict[str, Any] | None = Field(default=None, description="API 파라미터")
    method: str = Field(default="POST", description="HTTP 메서드")


@router.post("/proxy/aps")
async def proxy_aps(
    request: Request,
    project_id: str = Path(..., description="프로젝트 ID"),
    body: ApsProxyRequest = None,
) -> Any:
    """
    APS 백엔드 프록시 엔드포인트

    BomMap, PlanByProd, Pegging, Frozen Plan, Widget 설정 등
    원본 APS 백엔드 API를 프록시합니다.
    """
    if body is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Request body is required"},
        )

    aps_base = settings.APS_BACKEND_BASE_URL.rstrip("/")
    target_url = f"{aps_base}/api/aps/backend/{project_id}/{body.url}"

    # 프론트엔드 요청의 인증 헤더를 APS 백엔드로 전달
    forward_headers = {}
    if auth := request.headers.get("authorization"):
        forward_headers["Authorization"] = auth
    if cookie := request.headers.get("cookie"):
        forward_headers["Cookie"] = cookie

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if body.method.upper() == "GET":
                resp = await client.get(target_url, params=body.param, headers=forward_headers)
            else:
                resp = await client.request(
                    method=body.method.upper(),
                    url=target_url,
                    json=body.param,
                    headers=forward_headers,
                )

            # APS 응답을 그대로 반환
            try:
                return resp.json()
            except Exception:
                return {
                    "success": False,
                    "error": f"APS returned non-JSON response (status {resp.status_code})",
                    "data": [],
                }

    except httpx.ConnectError:
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": f"Cannot connect to APS backend at {aps_base}",
                "data": [],
            },
        )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "error": "APS backend request timed out",
                "data": [],
            },
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Proxy error: {str(e)}",
                "data": [],
            },
        )
