"""
Mock 미들웨어

USE_MOCK=true 환경에서 API 요청을 가로채서 캡처된 JSON 응답을 반환합니다.
실제 DB 연결 없이 프론트엔드 개발/테스트가 가능합니다.
"""

import logging
import re

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.mock_store import get_mock_response, is_mock_mode

logger = logging.getLogger(__name__)

# project_id 부분을 제거하고 엔드포인트 경로만 추출하는 패턴
_PATH_PATTERN = re.compile(
    r"/api/custom/backend/[^/]+(/.*)"
)


class MockMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not is_mock_mode():
            return await call_next(request)

        path = request.url.path
        method = request.method

        # project_id 이후 경로 추출
        match = _PATH_PATTERN.match(path)
        if not match:
            return await call_next(request)

        endpoint_path = match.group(1)
        mock_data = get_mock_response(method, endpoint_path)

        if mock_data is not None:
            logger.info(f"[MOCK] {method} {endpoint_path} → serving from file")
            return JSONResponse(content=mock_data)

        # mock 데이터가 없으면 실제 핸들러로 전달 (fallback)
        logger.debug(f"[MOCK] {method} {endpoint_path} → no mock, passing through")
        return await call_next(request)
