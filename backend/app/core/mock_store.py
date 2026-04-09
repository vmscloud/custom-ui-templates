"""
Mock 데이터 스토어

USE_MOCK=true 환경에서 실제 DB 대신 캡처된 JSON 파일을 반환합니다.
API 엔드포인트 → 파일명 매핑으로 동작합니다.
"""

import json
import os
from pathlib import Path
from typing import Any

MOCK_DIR = Path(__file__).parent.parent.parent / "mock_data" / "responses"

# 엔드포인트 → 파일명 매핑
_ROUTE_MAP: dict[str, str] = {
    # LoadFactorByOperGroup
    "GET:/load-factor/oper-groups": "lf_oper_groups",
    "POST:/load-factor/main": "lf_main",
    "POST:/load-factor/group": "lf_group_sample",
    "POST:/load-factor/detail": "lf_detail_sample",
    # ReExecutePlan
    "GET:/re-execute-plan/oper-groups": "re_oper_groups",
    "GET:/re-execute-plan/regions": "re_regions",
    # OnTimeRescheduledPlanResult
    "POST:/replan-rtf/summary": "replan_summary",
    "POST:/replan-rtf/detail": "replan_detail",
    "GET:/replan-rtf/filters/prod-types": "replan_prod_types",
    "GET:/rtf-report/filters/customers": "replan_customers",
    "GET:/rtf-report/filters/item-groups": "replan_item_groups",
    # PlanDashboard
    "POST:/plan-dashboard/dashboard": "dash_dashboard",
    "GET:/plan-dashboard/settings": "dash_settings",
    "GET:/plan-dashboard/frozen-ver": "dash_frozen_ver",
    # RTFReport
    "POST:/rtf-report/RarRtfReport/Main2": "rtf_main2",
    "POST:/rtf-report/RarRtfReport/Detail2": "rtf_detail2",
    "POST:/rtf-report/RarRtfReport/Short": "rtf_short_sample",
    # PlanCycle
    "POST:/planCycleSource": "plan_cycle",
}

_cache: dict[str, Any] = {}


def is_mock_mode() -> bool:
    return os.environ.get("USE_MOCK", "").lower() in ("true", "1", "yes")


# RTFReport 프록시용 매핑 (api_name → 파일명)
_RTF_PROXY_MAP: dict[str, str] = {
    "RarRtfReport/Main2": "rtf_main2",
    "RarRtfReport/Detail2": "rtf_detail2",
    "RarRtfReport/Short": "rtf_short_sample",
}


def get_mock_response(method: str, path: str) -> dict | None:
    """
    엔드포인트 경로에 대한 mock 응답을 반환합니다.
    path는 project_id 이후 부분 (예: /load-factor/main)
    """
    if not is_mock_mode():
        return None

    key = f"{method.upper()}:{path}"
    file_name = _ROUTE_MAP.get(key)
    if not file_name:
        return None

    if file_name in _cache:
        return _cache[file_name]

    file_path = MOCK_DIR / f"{file_name}.json"
    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _cache[file_name] = data
    return data


def get_mock_file(name: str) -> dict | None:
    """파일명으로 직접 mock 데이터를 가져옵니다."""
    if not is_mock_mode():
        return None

    if name in _cache:
        return _cache[name]

    file_path = MOCK_DIR / f"{name}.json"
    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _cache[name] = data
    return data
