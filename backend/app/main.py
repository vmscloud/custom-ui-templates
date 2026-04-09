"""
FastAPI 메인 애플리케이션

Mozart Cloud Custom UI 앱 진입점
"""

from app.api.v1.api import api_router
from app.core.mock_middleware import MockMiddleware
from app.core.mock_store import is_mock_mode
from fastapi import FastAPI
from pylogger.middleware import setup_http_middleware

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Mozart Cloud Custom UI")

# Mock 미들웨어 (USE_MOCK=true 시 DB 대신 캡처된 JSON 반환)
if is_mock_mode():
    app.add_middleware(MockMiddleware)
    import logging
    logging.getLogger(__name__).info("[MOCK MODE] DB 연결 없이 캡처된 데이터로 응답합니다.")

# 모든 라우터 등록
app.include_router(api_router)

setup_http_middleware(app)