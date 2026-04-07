"""
애플리케이션 설정 관리
Pydantic Settings를 사용한 환경 변수 관리
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 애플리케이션 정보
    APP_NAME: str = "Mozart Cloud Custom UI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # 데이터베이스 설정
    # DATABASE_URL: str = "postgresql://mzcdev:cloud-vms1!@mzcrds-dev.cboeqa8ie939.ap-northeast-2.rds.amazonaws.com/aleatorik"
    DATABASE_URL: str = "postgresql://mzcadm:mzcadm@203.231.40.243:5432/mzc_aps"

    # Trino 연결 설정
    TRINO_HOST: str = "203.231.40.243"
    TRINO_PORT: int = 18080
    TRINO_USER: str = "mzcadm"
    TRINO_CATALOG: str = "iceberg"
    TRINO_SCHEMA: str = "mzc_aps"
    # PostgreSQL 카탈로그 (cfg_plan_config 등 설정 테이블 접근용)
    TRINO_PG_CATALOG: str = "postgresql"
    TRINO_PG_SCHEMA: str = "mzc_aps"

    # 쿼리 실행 타임아웃
    QUERY_TIMEOUT_SECONDS: int = 120
    # Query Executor 설정
    # QUERY_EXECUTOR_BASE_URL: str = "http://internal-mzcalb-aps-api-dev-1563398398.ap-northeast-2.elb.amazonaws.com:18000"
    # QUERY_EXECUTOR_BASE_URL: str = "http://mzc_common_queryexecutor:18000"
    QUERY_EXECUTOR_BASE_URL: str = "http://aps-dev.petasys.com:18000"
    QUERY_EXECUTOR_DB_ALIAS: str = "com"  # Query Database alias (고정값)
    QUERY_EXECUTOR_LIMIT: int = 50000  # 쿼리 결과 최대 행 수

    # Trino Iceberg 설정 (Query Executor adapter용 — Iceberg 데이터 테이블)
    TRINO_CATALOG_ICEBERG: str = "iceberg"
    TRINO_SCHEMA_APS: str = "mzc_aps"

    # APS C# 백엔드 (프록시용)
    APS_BACKEND_BASE_URL: str = "http://localhost:8080"

    # APS 백엔드 프록시 설정 (dev 환경)
    # APS_BACKEND_BASE_URL: str = "http://internal-mzcalb-aps-api-dev-1563398398.ap-northeast-2.elb.amazonaws.com:5000"
    # APS_BACKEND_BASE_URL: str = "https://dev.mozart-cloud.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
