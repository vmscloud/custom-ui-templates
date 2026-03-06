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

    # Trino 데이터베이스 설정
    TRINO_HOST: str = "internal-mzcalb-aps-api-dev-1563398398.ap-northeast-2.elb.amazonaws.com"
    TRINO_PORT: int = 18080
    TRINO_USER: str = "mzcadm"
    TRINO_CATALOG: str = "iceberg"
    TRINO_SCHEMA: str = "mzc_aps"

    # 쿼리 실행 타임아웃
    QUERY_TIMEOUT_SECONDS: int = 120
    # Query Executor 설정
    # QUERY_EXECUTOR_BASE_URL: str = "http://internal-mzcalb-aps-api-dev-1563398398.ap-northeast-2.elb.amazonaws.com:18000"
    # QUERY_EXECUTOR_BASE_URL: str = "http://mzc_common_queryexecutor:18000"
    QUERY_EXECUTOR_BASE_URL: str = "http://192.168.1.250:18000"
    QUERY_EXECUTOR_DB_ALIAS: str = "com"  # Query Database alias (고정값)
    QUERY_EXECUTOR_LIMIT: int = 50000  # 쿼리 결과 최대 행 수

    # APS 백엔드 프록시 설정
    # APS_BACKEND_BASE_URL: str = "http://internal-mzcalb-aps-api-dev-1563398398.ap-northeast-2.elb.amazonaws.com:5000"
    APS_BACKEND_BASE_URL: str = "https://dev.mozart-cloud.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
