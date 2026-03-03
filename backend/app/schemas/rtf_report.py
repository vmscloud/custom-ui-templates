"""
RTF Report 관련 Pydantic 스키마
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# === 요청 스키마 ===


class RtfSummaryRequest(BaseModel):
    """RTF 요약 그리드 요청"""

    planVer: str = Field(..., description="Plan version")
    aggregateType: str = Field(
        default="MONTH", description="집계 유형: WEEK | MONTH"
    )
    summary: str = Field(
        default="itemGroup",
        description="요약 기준: due | cust | itemGroup | region | demandType",
    )
    customers: list[str] = Field(default=[], description="고객 필터 목록")
    itemGroupIDs: list[str] = Field(default=[], description="품목 그룹 필터 목록")
    regions: list[str] = Field(default=[], description="지역 필터 목록")
    demandTypes: list[str] = Field(default=[], description="수요 유형 필터 목록")
    prodStatus: str = Field(
        default="default",
        description="생산 상태 필터: default | on_time | late | short",
    )
    uomType: str = Field(
        default="DEFAULT", description="단위 유형: DEFAULT | CONVERSION"
    )


class RtfDetailRequest(BaseModel):
    """RTF 상세 그리드 요청"""

    planVer: str
    aggregateType: str = "MONTH"
    summary: str = "itemGroup"
    groupKey: str | None = Field(
        default=None, description="요약 행 선택 시 그룹 키 (드릴다운 필터)"
    )
    dueMonth: str | None = Field(
        default=None, description="선택된 월 (YYYY-MM, aggregateType=MONTH일 때)"
    )
    dueWeek: str | None = Field(
        default=None, description="선택된 주 (YYYY-WW, aggregateType=WEEK일 때)"
    )
    customers: list[str] = Field(default=[])
    itemGroupIDs: list[str] = Field(default=[])
    regions: list[str] = Field(default=[], description="생산 지역 필터 목록")
    demandTypes: list[str] = Field(default=[])
    prodStatus: str = "default"
    uomType: str = "DEFAULT"


class RtfDemandRequest(BaseModel):
    """수요 기반 요청 (Short, ProdDetail, DemandInfo, PegInfo 공통)"""

    planVer: str
    demandID: str
    uomType: str = "DEFAULT"


class RtfBufferPlanTargetRequest(BaseModel):
    """버퍼 계획 Target vs 실적 요청"""

    planVer: str
    demandID: str


class RtfDemandSummaryRequest(BaseModel):
    """수요 요약 메트릭 요청"""

    planVer: str
    demandIDs: list[str]
    uomType: str = "DEFAULT"


class RtfBomMapRequest(BaseModel):
    """BOM 구조 요청"""

    planVer: str
    demandID: str
    onlyTargetBom: bool = True
    uomType: str = "DEFAULT"


class RtfItemPropsRequest(BaseModel):
    """품목 속성 요청"""

    planVer: str
    itemID: str


class RtfDemandRecordRequest(BaseModel):
    """수요 레코드 상세 요청"""

    planVer: str
    demandID: str
