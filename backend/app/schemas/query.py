"""
쿼리 관련 Pydantic 스키마
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    parameters: dict[str, str | int | float | list[str]] | None = Field(default=None)


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    execution_time_ms: float | None = None


class QueryCancelRequest(BaseModel):
    query_id: str


class QueryError(BaseModel):
    error: str
    detail: str | None = None


class ExplainResult(BaseModel):
    plan: dict[str, Any]  # Trino EXPLAIN JSON 결과
    execution_time_ms: float | None = None


class MozProject(BaseModel):
    """프로젝트 정보 (moz_project 기반)"""

    project_id: str
    project_name: str
    system_id: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
