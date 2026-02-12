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
    DATABASE_URL: str = "postgresql://mzcdev:cloud-vms1!@mzcrds-dev.cboeqa8ie939.ap-northeast-2.rds.amazonaws.com/aleatorik"

    # 쿼리 실행 타임아웃
    QUERY_TIMEOUT_SECONDS: int = 120
    # Query Executor 설정
    QUERY_EXECUTOR_BASE_URL: str = "http://internal-mzcalb-aps-api-dev-1563398398.ap-northeast-2.elb.amazonaws.com:18000"
    QUERY_EXECUTOR_DB_ALIAS: str = "com"  # Query Database alias (고정값)
    QUERY_EXECUTOR_LIMIT: int = 50000  # 쿼리 결과 최대 행 수

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
