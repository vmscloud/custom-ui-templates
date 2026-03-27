"""
부하율 (LoadFactor) 관련 Pydantic 스키마
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoadFactorMainRequest(BaseModel):
    """부하율 메인 요청"""

    planVer: str = Field(..., description="Plan version")
    fromDate: str = Field(..., description="조회 시작일 (YYYY-MM-DD)")
    toDate: str = Field(..., description="조회 종료일 (YYYY-MM-DD)")
    operGroupIDs: list[str] = Field(default_factory=list, description="공정 그룹 필터")
    includeUndefinedCapa: bool = Field(default=True, description="미정의 Capa 포함 여부")


class LoadFactorGroupRequest(BaseModel):
    """부하율 그룹별 일간 조회 요청"""

    planVer: str = Field(..., description="Plan version")
    fromDate: str = Field(..., description="조회 시작일 (YYYY-MM-DD)")
    toDate: str = Field(..., description="조회 종료일 (YYYY-MM-DD)")
    operGroupIDs: list[str] = Field(default_factory=list, description="공정 그룹 필터")


class LoadFactorDetailRequest(BaseModel):
    """부하율 상세 조회 요청"""

    planVer: str = Field(..., description="Plan version")
    fromDate: str = Field(..., description="조회 시작일 (YYYY-MM-DD)")
    toDate: str = Field(..., description="조회 종료일 (YYYY-MM-DD)")
    operGroupIDs: list[str] = Field(default_factory=list, description="공정 그룹 필터")
    includeUndefinedCapa: bool = Field(default=True, description="미정의 Capa 포함 여부")
