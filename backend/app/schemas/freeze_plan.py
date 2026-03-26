"""Freeze Plan 관련 Pydantic 스키마"""
from pydantic import BaseModel, Field

class FrozenStatusRequest(BaseModel):
    planCycleID: str = Field(..., description="계획 사이클 ID")
    planVer: str = Field(default="", description="계획 버전")

class FrozenPlanRequest(BaseModel):
    planCycleID: str = Field(..., description="계획 사이클 ID")
    planVer: str = Field(..., description="계획 버전")
    description: str = Field(default="", description="확정 설명")

class FrozenPeriodRequest(BaseModel):
    planVer: str = Field(..., description="계획 버전")
