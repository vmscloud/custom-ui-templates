"""
Mock 데이터 캡처 스크립트

VPN 연결 상태에서 실행하여 모든 API 응답을 파일로 저장합니다.
저장된 데이터는 USE_MOCK=true 환경에서 DB 대신 사용됩니다.

Usage:
    cd backend
    python -m mock_data.capture
"""

import hashlib
import json
import os
import sys

import httpx

# 프로젝트 설정
PROJECT_ID = "EED70012-E49D-4BA5-AD05-870C338DF39A"
PLAN_VER = "20260403-M-01"
BASE = f"http://localhost:5300/api/custom/backend/{PROJECT_ID}"
OUT_DIR = os.path.join(os.path.dirname(__file__), "responses")


def save(name: str, data: dict):
    path = os.path.join(OUT_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    count = data.get("count", len(data.get("data", [])) if isinstance(data.get("data"), list) else "?")
    print(f"  [OK] {name} ({count} rows)")


def get(url, params=None):
    return httpx.get(url, params=params, timeout=120).json()


def post(url, body):
    return httpx.post(url, json=body, timeout=120).json()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Capturing mock data for planVer={PLAN_VER}...\n")

    # ===== LoadFactorByOperGroup =====
    print("[LoadFactorByOperGroup]")
    save("lf_oper_groups", get(f"{BASE}/load-factor/oper-groups", {"planVer": PLAN_VER}))
    save("lf_main", post(f"{BASE}/load-factor/main", {
        "planVer": PLAN_VER, "fromDate": "2026-04-01", "toDate": "2026-04-30",
        "operGroupIDs": [], "includeUndefinedCapa": True,
    }))
    # group/detail은 oper_group_id별로 호출됨 — 샘플 1개만
    save("lf_group_sample", post(f"{BASE}/load-factor/group", {
        "planVer": PLAN_VER, "fromDate": "2026-04-01", "toDate": "2026-04-30",
        "operGroupIDs": ["031. 판넬도금"],
    }))
    save("lf_detail_sample", post(f"{BASE}/load-factor/detail", {
        "planVer": PLAN_VER, "fromDate": "2026-04-01", "toDate": "2026-04-30",
        "operGroupIDs": ["031. 판넬도금"], "includeUndefinedCapa": True,
    }))

    # ===== ReExecutePlan =====
    print("\n[ReExecutePlan]")
    save("re_oper_groups", get(f"{BASE}/re-execute-plan/oper-groups", {"planVer": PLAN_VER}))
    save("re_regions", get(f"{BASE}/re-execute-plan/regions", {"planVer": PLAN_VER}))

    # ===== OnTimeRescheduledPlanResult =====
    print("\n[OnTimeRescheduledPlanResult]")
    save("replan_summary", post(f"{BASE}/replan-rtf/summary", {
        "planVer": PLAN_VER, "aggregateType": "MONTH", "summary": "itemGroup",
        "uomType": "DEFAULT", "userId": "",
    }))
    save("replan_detail", post(f"{BASE}/replan-rtf/detail", {
        "planVer": PLAN_VER, "aggregateType": "MONTH", "summary": "itemGroup",
        "uomType": "DEFAULT", "userId": "", "dueMonth": "202604",
    }))
    save("replan_prod_types", get(f"{BASE}/replan-rtf/filters/prod-types", {"planVer": PLAN_VER}))
    save("replan_customers", get(f"{BASE}/rtf-report/filters/customers", {"plan_ver": PLAN_VER}))
    save("replan_item_groups", get(f"{BASE}/rtf-report/filters/item-groups", {"plan_ver": PLAN_VER}))

    # ===== PlanDashboard =====
    print("\n[PlanDashboard]")
    save("dash_dashboard", post(f"{BASE}/plan-dashboard/dashboard", {
        "planVer": PLAN_VER, "region": "RTF", "detailRegion": "all",
        "aggregateType": "MONTH", "userId": "", "menuId": "/pa/PlanDashboard2",
    }))
    save("dash_settings", get(f"{BASE}/plan-dashboard/settings", {"userId": "admin", "menuId": "/pa/PlanDashboard2"}))
    save("dash_frozen_ver", get(f"{BASE}/plan-dashboard/frozen-ver", {"planVer": PLAN_VER}))

    # ===== RTFReport (프록시) =====
    print("\n[RTFReport]")
    save("rtf_main2", post(f"{BASE}/rtf-report/RarRtfReport/Main2", {
        "planVer": PLAN_VER, "aggregateType": "MONTH", "summary": "itemGroup", "uomType": "DEFAULT",
    }))
    save("rtf_detail2", post(f"{BASE}/rtf-report/RarRtfReport/Detail2", {
        "planVer": PLAN_VER, "aggregateType": "MONTH", "summary": "itemGroup",
        "uomType": "DEFAULT", "dueMonth": "202604",
    }))
    save("rtf_short_sample", post(f"{BASE}/rtf-report/RarRtfReport/Short", {
        "planVer": PLAN_VER, "demandID": "5121294", "uomType": "DEFAULT",
    }))

    # ===== PlanCycle =====
    print("\n[PlanCycle]")
    save("plan_cycle", post(f"{BASE}/planCycleSource", {}))

    print(f"\n=== Done! Files saved to: {OUT_DIR} ===")


if __name__ == "__main__":
    main()
