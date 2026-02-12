"""
쿼리 실행 서비스
저장된 쿼리 실행 비즈니스 로직
"""

from typing import Any

from app.adapters.adapter import QueryExecutorAdapter
from app.api.dependencies import get_query_executor_adapter
from app.core.config import settings
from fastapi import Depends


class QueryExecuteService:
    def __init__(self, adapter: QueryExecutorAdapter):
        """
        서비스 초기화

        Args:
            adapter: QueryExecutorAdapter 인스턴스
        """
        self.adapter = adapter

    async def execute(
        self,
        query_id: str,
        parameters: dict[str, str | int | float | list[str]] | None = None,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        result = await self.adapter.execute_query(
            project_id=project_id,
            query_id=query_id,
            parameters=parameters,
            limit=settings.QUERY_EXECUTOR_LIMIT,
        )

        # Adapter는 success=false 시 예외를 던지지 않음 → 직접 체크
        if not result.get("success"):
            raise ValueError(result.get("message", "쿼리 실행 실패"))

        return {
            "columns": result["columns"],
            "rows": result["row"],  # Adapter: "row" → Service: "rows"
            "row_count": result[
                "rowcount"
            ],  # Adapter: "rowcount" → Service: "row_count"
        }


def get_query_execute_service(
    adapter: QueryExecutorAdapter = Depends(get_query_executor_adapter),
) -> QueryExecuteService:
    """FastAPI 의존성 주입용 서비스 생성"""
    return QueryExecuteService(adapter)
