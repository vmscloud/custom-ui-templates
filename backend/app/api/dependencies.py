"""
공통 의존성 정의

FastAPI 앱에서 공통으로 사용되는 의존성들을 정의합니다.
"""

from app.adapters.adapter import QueryExecutorAdapter
from app.core.config import settings

# 싱글톤 어댑터 인스턴스 (HTTP 클라이언트 풀 재사용)
_adapter_instance: QueryExecutorAdapter | None = None


def get_query_executor_adapter() -> QueryExecutorAdapter:
    """QueryExecutorAdapter 의존성 주입 (싱글톤)

    HTTP 클라이언트 풀을 재사용하기 위해 싱글톤 패턴 적용.
    매 요청마다 새 인스턴스 생성 시 TCP 연결 오버헤드 발생.
    """
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = QueryExecutorAdapter(
            base_url=settings.QUERY_EXECUTOR_BASE_URL,
            db_alias=settings.QUERY_EXECUTOR_DB_ALIAS,  # "com" 고정
            timeout=float(settings.QUERY_TIMEOUT_SECONDS),
        )
    return _adapter_instance


async def close_adapter() -> None:
    """어댑터 리소스 정리 (앱 종료 시 호출)"""
    global _adapter_instance
    if _adapter_instance is not None:
        await _adapter_instance.close()
        _adapter_instance = None
