"""
재실행 계획 (ReExecutePlan) 관련 Pydantic 스키마
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReExecuteMainRequest(BaseModel):
    """재실행 계획 메인 요청"""

    planVer: str = Field(..., description="Plan version")
    frozenPlanVer: str | None = Field(default=None, description="Frozen plan version")
    summaryType: str = Field(default="OPERGROUP", description="요약 유형 (OPERGROUP | BUFFER)")
    aggregateType: str = Field(default="MONTH", description="집계 유형 (WEEK | MONTH)")
    operGroupIDs: list[str | None] = Field(default_factory=list, description="공정 그룹 필터")
    operIDs: list[str | None] = Field(default_factory=list, description="공정 필터")
    bufferIDs: list[str | None] = Field(default_factory=list, description="버퍼 필터")
    customers: list[str | None] = Field(default_factory=list, description="고객사 필터")
    itemGroupIDs: list[str | None] = Field(default_factory=list, description="품목 그룹 필터")
    regions: list[str | None] = Field(default_factory=list, description="지역 필터")
    demandTypes: list[str | None] = Field(default_factory=list, description="수요 유형 필터")
    uomType: str = Field(default="DEFAULT", description="UOM 유형 (DEFAULT | CONVERSION)")
