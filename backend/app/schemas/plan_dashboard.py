"""
Plan Dashboard 관련 Pydantic 스키마
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# === 메인 대시보드 요청 ===


class DashboardRequest(BaseModel):
    """메인 대시보드 전체 데이터 요청"""

    planVer: str = Field(..., description="Plan version")
    region: str = Field(default="RTF", description="지역 필터: RTF | RTF_대구 | RTF_HK")
    detailRegion: str = Field(
        default="전체", description="상세 지역: 전체 | HK 완제 | HK 반제"
    )
    aggregateType: str = Field(
        default="MONTH", description="집계 유형: Day | Week | Month"
    )
    userId: str = Field(default="", description="사용자 ID (위젯 설정 조회용)")
    menuId: str = Field(
        default="/pa/PlanDashboard", description="메뉴 ID (위젯 설정 조회용)"
    )
    regions: list[str] = Field(default=[], description="지역 필터 목록")
    productionArea: str = Field(default="", description="생산 영역 필터")


# === RTF 세부 통계 요청 ===


class RtfDetailRequest(BaseModel):
    """RTF 세부 통계 드릴다운 요청"""

    planVer: str
    region: str = "RTF"
    detailRegion: str = "전체"
    month: str | None = Field(default=None, description="선택된 월 (YYYY-MM)")
    week: str | None = Field(default=None, description="선택된 주 (YYYY-WW)")


# === 설비 가동 현황 요청 ===


class ResGroupRequest(BaseModel):
    """설비 가동 현황 단독 리프레시 요청"""

    planVer: str
    resGroupIDs: list[str] = Field(default=[], description="선택된 설비 그룹 ID 목록")
    weekPeriod: int = Field(default=0, description="주 기간 (0=전체)")


# === 생산 현황 요청 ===


class ProdReportRequest(BaseModel):
    """생산 현황 집계 기준 변경 요청"""

    planVer: str
    aggregateType: str = Field(default="MONTH", description="Day | Week | Month")


# === 설정 조회 요청 ===


class SettingsQueryParams(BaseModel):
    """위젯 설정 조회 쿼리 파라미터"""

    userId: str = Field(..., description="사용자 ID")
    menuId: str = Field(
        default="/pa/PlanDashboard", description="메뉴 ID"
    )
    planVer: str = Field(default="", description="Plan version (설비그룹 팝업용)")


# === 설정 저장 요청 ===


class SettingsSaveRequest(BaseModel):
    """위젯 설정 저장 요청"""

    userId: str = Field(..., description="사용자 ID")
    menuId: str = Field(
        default="/pa/PlanDashboard", description="메뉴 ID"
    )
    widgetId: str = Field(..., description="위젯 ID (e.g. rtfReportPopup, ResGroupPopup)")
    widgetValue: str = Field(
        ..., description="위젯 설정 JSON 문자열"
    )
