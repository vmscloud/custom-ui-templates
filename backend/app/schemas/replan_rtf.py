"""
재수립 RTF 관련 Pydantic 스키마
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReplanRtfMainRequest(BaseModel):
    """재수립 RTF 요약 요청"""

    planVer: str = Field(..., description="Plan version")
    aggregateType: str = Field(default="MONTH", description="집계 유형: WEEK | MONTH")
    summary: str = Field(
        default="itemGroup",
        description="요약 기준: cust | itemGroup | prodType | region",
    )
    customers: list[str] = Field(default=[], description="고객 필터")
    itemGroupIDs: list[str] = Field(default=[], description="품목 그룹 필터")
    prodTypes: list[str] = Field(default=[], description="생산유형 필터")
    prodStatus: str | None = Field(
        default=None,
        description="생산 상태: default | on_time | late | short | early",
    )
    uomType: str = Field(default="DEFAULT", description="단위: DEFAULT | CONVERSION")
    productionArea: str | None = Field(default=None, description="생산 영역 필터")
    userId: str = Field(default="", description="사용자 ID (위젯 설정용)")


class ReplanRtfDetailRequest(ReplanRtfMainRequest):
    """재수립 RTF 상세 요청"""

    dueMonth: str | None = Field(default=None, description="월 필터 (YYYY-MM)")
    dueWeek: str | None = Field(default=None, description="주 필터 (YYYY-WW)")


class ReplanRtfProdDetailRequest(BaseModel):
    """재수립 RTF 생산계획 피벗 요청"""

    planVer: str
    demandID: str
    uomType: str = "DEFAULT"
