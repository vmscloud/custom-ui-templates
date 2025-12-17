"""
FastAPI 메인 애플리케이션

Mozart Cloud Custom UI 앱 진입점
"""

from app.api.v1.api import api_router
from fastapi import FastAPI

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Mozart Cloud Custom UI")

# 모든 라우터 등록
app.include_router(api_router)
