"""
애플리케이션 설정 관리

환경 변수 로드 순서 (뒤가 앞을 덮어씀):
  1. .env              — 공통 기본값
  2. .env.development  — 개발 환경
  3. .env.local        — 로컬 개인 설정 (gitignore)
  4. OS 환경변수        — 최우선 (docker, CI 등)
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    """애플리케이션 설정"""

    model_config = SettingsConfigDict(
        env_file=(
            _BASE_DIR / ".env",
            _BASE_DIR / ".env.development",
            _BASE_DIR / ".env.local",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # 애플리케이션
    APP_NAME: str
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    USE_MOCK: bool = False

    # Trino 연결 (database.py — PostgreSQL 설정 테이블)
    TRINO_HOST: str
    TRINO_PORT: int = 18080
    TRINO_USER: str
    TRINO_CATALOG: str = "iceberg"
    TRINO_SCHEMA: str = "mzc_aps"
    TRINO_PG_CATALOG: str = "postgresql"
    TRINO_PG_SCHEMA: str = "mzc_aps"

    # Trino Iceberg (Query Executor adapter — 데이터 테이블)
    TRINO_CATALOG_ICEBERG: str = "iceberg"
    TRINO_SCHEMA_APS: str = "mzc_aps"

    # Query Executor
    QUERY_EXECUTOR_BASE_URL: str
    QUERY_EXECUTOR_DB_ALIAS: str = "com"
    QUERY_EXECUTOR_LIMIT: int = 50000
    QUERY_TIMEOUT_SECONDS: int = 120

    # APS C# 백엔드 (프록시)
    APS_BACKEND_BASE_URL: str = "http://localhost:8080"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
