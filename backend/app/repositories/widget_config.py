"""
Widget 설정 저장소 (파일 기반)

사용자별 위젯 설정을 JSON 파일로 관리합니다.
원본 APS의 dp_user_widget_config 테이블을 대체합니다.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# 위젯 설정 저장 디렉토리
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "widget_configs"


def _get_config_path(project_id: str, user_id: str, widget_id: str) -> Path:
    """설정 파일 경로 생성"""
    safe_project = project_id.replace("/", "_").replace("\\", "_")
    safe_user = user_id.replace("/", "_").replace("\\", "_").replace("@", "_at_")
    safe_widget = widget_id.replace("/", "_").replace("\\", "_")
    return _DATA_DIR / safe_project / f"{safe_user}__{safe_widget}.json"


# RTFSummaryPopup 기본값 (원본 RarWidgetValueService 참조)
_DEFAULT_RTF_SUMMARY = {
    "rtfStd": "LOT",
    "uomType": "CONVERSION",
    "detailType": "BUFFER",
    "isDefault": True,
    "summaryTypes": {
        "period": True,
        "cust": True,
        "itemGroup": True,
        "demandType": False,
        "region": False,
    },
    "setting": [
        {
            "category": "within_plan",
            "plan_type": "early",
            "apply_early": True,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": False,
        },
        {
            "category": "within_plan",
            "plan_type": "on_time",
            "apply_early": False,
            "apply_on_time": True,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": False,
        },
        {
            "category": "within_plan",
            "plan_type": "late",
            "apply_early": False,
            "apply_on_time": False,
            "apply_late": True,
            "apply_short": False,
            "apply_excluded": False,
        },
        {
            "category": "within_plan",
            "plan_type": "remain",
            "apply_early": False,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": True,
            "apply_excluded": False,
        },
        {
            "category": "within_plan",
            "plan_type": "short",
            "apply_early": False,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": True,
            "apply_excluded": False,
        },
        {
            "category": "after_plan",
            "plan_type": "early",
            "apply_early": True,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": False,
        },
        {
            "category": "after_plan",
            "plan_type": "on_time",
            "apply_early": False,
            "apply_on_time": True,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": False,
        },
        {
            "category": "after_plan",
            "plan_type": "late",
            "apply_early": False,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": True,
        },
        {
            "category": "after_plan",
            "plan_type": "remain",
            "apply_early": False,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": True,
        },
        {
            "category": "after_plan",
            "plan_type": "short",
            "apply_early": False,
            "apply_on_time": False,
            "apply_late": False,
            "apply_short": False,
            "apply_excluded": True,
        },
    ],
}


def get_rtf_summary_popup(
    project_id: str, user_id: str, plan_ver: str
) -> dict:
    """
    PlanDashboard/GetRTFSummaryPopup — RTF 위젯 설정 조회

    원본: RarWidgetValueService.GetRTFReportPopupWidgetValue
    - dp_user_widget_config에서 widget_id='rtfSummaryPopup' 조회
    - 없으면 기본값 반환
    """
    config_path = _get_config_path(project_id, user_id, "rtfSummaryPopup")

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            widget_value = data.get("widget_value", "")
            if widget_value:
                parsed = json.loads(widget_value) if isinstance(widget_value, str) else widget_value
                # 기본값으로 누락 필드 보완
                result = {**_DEFAULT_RTF_SUMMARY, **parsed}
                result["isDefault"] = False
                return result
        except (json.JSONDecodeError, IOError):
            pass

    return dict(_DEFAULT_RTF_SUMMARY)


def save_widget_value(
    project_id: str, rows: list[dict]
) -> int:
    """
    PlanDashboard/SaveWidgetValue — 위젯 설정 저장

    원본: RarPlanDashboardController.SaveWidgetSettingValue
    - dp_user_widget_config UPSERT
    """
    saved = 0
    now = datetime.now(timezone.utc).isoformat()

    for row in rows:
        user_id = row.get("user_id", "")
        widget_id = row.get("widget_id", "")
        widget_value = row.get("widget_value", "")

        if not user_id or not widget_id:
            continue

        config_path = _get_config_path(project_id, user_id, widget_id)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "project_id": project_id,
            "user_id": user_id,
            "menu_id": row.get("menu_id", "/pa/PlanDashboard"),
            "widget_id": widget_id,
            "widget_value": widget_value,
            "update_datetime": now,
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        saved += 1

    return saved
