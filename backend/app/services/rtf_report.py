"""
RTF Report 서비스 레이어

apiUrl 기반 라우팅 + 비즈니스 로직
원본 C# RarRtfReportService/RarRtfReportProcessor 완전 재현
"""

import math
import traceback
from datetime import datetime, timedelta

from app.repositories.rtf_report import RtfReportRepository
from app.repositories.widget_config import get_rtf_summary_popup, save_widget_value


# ══════════════════════════════════════════════════════════
# 상수 (C# RTFSummaryConst, DPConstant 완전 재현)
# ══════════════════════════════════════════════════════════

WITHIN_PLAN = "within_plan"
AFTER_PLAN = "after_plan"
EARLY = "early"
ON_TIME = "on_time"
LATE = "late"
REMAIN = "remain"
SHORT = "short"
UPCOMING = "up_coming"

# C# DPConstant
TOTAL = "[TOTAL]"
SUBTOTAL = "[SUB TOTAL]"
CUST = "CUST"
ITEMGROUP = "ITEMGROUP"
REGION = "REGION"
DEMANDTYPE = "DEMANDTYPE"
WEEK = "WEEK"
LOT = "LOT"
DEFAULT_UOM = "DEFAULT"

# timedelta 상수
_ONE_DAY = timedelta(days=1)


def _create_key(*parts: str) -> str:
    """C# StringHelper.CreateKey — 파이프 구분 키 생성"""
    return "|".join(parts)


def _parse_date_yyyymmdd(s: str | None) -> datetime | None:
    """yyyyMMdd 형식 파싱"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:8], "%Y%m%d")
    except (ValueError, TypeError):
        return None


def _parse_date_yyyy_mm_dd(s: str | None) -> datetime | None:
    """yyyy-MM-dd 형식 파싱"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


# ══════════════════════════════════════════════════════════
# TypeQtyProcessor (C# 완전 재현)
# ══════════════════════════════════════════════════════════

class TypeQtyProcessor:
    """
    원본 C# TypeQtyProcessor 완전 재현.
    Widget 설정(RTFSummaryPopupJson)의 setting 배열로부터
    (category, warehouse_status) → 분류타입 매핑을 구축합니다.
    """

    def __init__(self):
        self._type_dict: dict[str, dict[str, str]] = {}

    def set_category_dict(self, setting_list: list[dict]):
        """
        C# SetCategoryDict 완전 재현.
        setting_list: RTFSummaryPopupJson.setting 배열
        각 항목: { category, plan_type, apply_early, apply_on_time, apply_late, apply_short, apply_excluded }

        C# 키: PascalCase warehouse_status ("Early", "OnTime", "Late", "Remain", "Short")
        C# GetWidgetCategory: "Early"→"early", "OnTime"→"on_time" 등으로 plan_type 매칭
        dict 키는 원래 PascalCase type name
        """
        self._type_dict = {}

        # C# 순서: (PascalCase type, lowercase plan_type)
        type_pairs = [
            ("Early", EARLY),
            ("OnTime", ON_TIME),
            ("Late", LATE),
            ("Remain", REMAIN),
            ("Short", SHORT),
        ]

        for pascal_type, plan_type_val in type_pairs:
            # setting에서 plan_type == plan_type_val 인 항목들 필터
            options = [s for s in setting_list if s.get("plan_type") == plan_type_val]

            for option in options:
                category = option.get("category", "")
                if category not in self._type_dict:
                    self._type_dict[category] = {}

                d = self._type_dict[category]
                # C# uses pascal_type ("Early" etc.) as key
                if option.get("apply_early"):
                    d[pascal_type] = EARLY
                elif option.get("apply_on_time"):
                    d[pascal_type] = ON_TIME
                elif option.get("apply_late"):
                    d[pascal_type] = LATE
                elif option.get("apply_short"):
                    d[pascal_type] = SHORT
                else:
                    d[pascal_type] = UPCOMING

    def get_type(self, category: str, status: str | None) -> str | None:
        """
        C# GetType 완전 재현.
        (category, warehouse_status) → EARLY/ON_TIME/LATE/SHORT/UPCOMING or None
        """
        if not status:
            return None

        d = self._type_dict.get(category)
        if d is None:
            return None

        return d.get(status)


# ══════════════════════════════════════════════════════════
# DateHelper (C# 완전 재현)
# ══════════════════════════════════════════════════════════

def get_week_date(year: str, week: str) -> str:
    """C# DateHelper.GetWeekDate: "{year}-01-01 00:00:{week}" """
    return f"{year}-01-01 00:00:{week}"


def get_week_date_from_yyyy_ww(date_str: str | None) -> str:
    """C# DateHelper.GetWeekDateFrom_YYYY_WW"""
    if not date_str or len(date_str) != 7:
        return ""
    year = date_str[:4]
    week = date_str[5:7]
    return get_week_date(year, week)


def get_month_date(year: str, month: str) -> str:
    """C# DateHelper.GetMonthDate: "{year}-{month}-01 00:00:00" """
    return f"{year}-{month}-01 00:00:00"


def get_month_date_from_yyyy_mm(date_str: str | None) -> str:
    """C# DateHelper.GetMonthDateFrom_YYYY_MM"""
    if not date_str or len(date_str) != 7:
        return ""
    year = date_str[:4]
    month = date_str[5:7]
    return get_month_date(year, month)


def get_date_format(aggregate_type: str, row: dict) -> str:
    """C# RarRtfReportProcessor.GetDateFormat"""
    if aggregate_type == WEEK:
        return get_week_date_from_yyyy_ww(row.get("dueWeek"))
    else:
        return get_month_date_from_yyyy_mm(row.get("dueMonth"))


def get_key(aggregate_type: str, summary_type: str, row: dict) -> str:
    """C# RarRtfReportProcessor.GetKey"""
    key = get_date_format(aggregate_type, row)

    if summary_type == CUST:
        key += (row.get("custID") or "")
    elif summary_type == ITEMGROUP:
        key += (row.get("itemGroupID") or "")
    elif summary_type == DEMANDTYPE:
        key += (row.get("prod_type") or row.get("PROD_TYPE") or "")
    elif summary_type == REGION:
        pa = row.get("production_area") or ""
        if pa:
            key += pa

    return key


# ══════════════════════════════════════════════════════════
# IRtfType 필터링/정렬 (C# 완전 재현)
# ══════════════════════════════════════════════════════════

def is_invalid_summary(summary_type: str, row: dict, valid_set: set | None) -> bool:
    """C# IRtfType.IsInvalid — Summary에서 유효하지 않은 행 필터링"""
    if valid_set is None:
        return False

    if summary_type == CUST:
        return (row.get("custID") or "") not in valid_set
    elif summary_type == ITEMGROUP:
        return (row.get("itemGroupID") or "") not in valid_set
    elif summary_type == REGION:
        return (row.get("production_area") or "") not in valid_set
    elif summary_type == DEMANDTYPE:
        return (row.get("demand_type") or row.get("DEMAND_TYPE") or "") not in valid_set

    return False


def is_invalid_detail(
    summary_type: str, row: dict, params: dict, valid_set: set | None
) -> bool:
    """C# IRtfType.IsInvalidDetail — Detail에서 유효하지 않은 행 필터링"""
    # 타입별 유효성 검사
    if valid_set is not None:
        if summary_type == CUST:
            if (row.get("custID") or "") not in valid_set:
                return True
        elif summary_type == ITEMGROUP:
            if (row.get("itemGroupID") or "") not in valid_set:
                return True
        elif summary_type == REGION:
            if (row.get("production_area") or "") not in valid_set:
                return True
        elif summary_type == DEMANDTYPE:
            if (row.get("prod_type") or row.get("PROD_TYPE") or "") not in valid_set:
                return True

    due_week = params.get("dueWeek")
    due_month = params.get("dueMonth")

    # SUBTOTAL 또는 TOTAL이면 필터 없음 (Period가 아닌 type은 여기서 통과)
    if summary_type != "PERIOD":
        if due_week in (SUBTOTAL, TOTAL) or due_month in (SUBTOTAL, TOTAL):
            return False

    # 기간 필터 (C# IsInvalidDetail)
    aggregate_type = params.get("aggregateType")
    if aggregate_type == WEEK:
        if due_week and due_week != TOTAL:
            if due_week != row.get("dueWeek"):
                return True
    else:
        if due_month and due_month != TOTAL:
            if due_month != row.get("dueMonth"):
                return True

    return False


def sort_summary_results(summary_type: str, infos: list[dict]) -> list[dict]:
    """C# IRtfType.CompareResult — Summary 결과 정렬"""
    if summary_type == CUST:
        return sorted(infos, key=lambda x: (
            1 if x.get("custID") == TOTAL else 0,
            1 if not x.get("custID") else 0,
            x.get("custID") or "",
            0 if x.get("due") == TOTAL else 1,
            x.get("due") or "",
        ))
    elif summary_type == ITEMGROUP:
        return sorted(infos, key=lambda x: (
            1 if x.get("itemGroupID") == TOTAL else 0,
            1 if not x.get("itemGroupID") else 0,
            x.get("itemGroupID") or "",
            0 if x.get("due") == TOTAL else 1,
            x.get("due") or "",
        ))
    elif summary_type == REGION:
        return sorted(infos, key=lambda x: (
            1 if x.get("region") == TOTAL else 0,
            1 if not x.get("region") else 0,
            x.get("region") or "",
            0 if x.get("due") == TOTAL else 1,
            x.get("due") or "",
        ))
    elif summary_type == DEMANDTYPE:
        return sorted(infos, key=lambda x: (
            1 if x.get("demandType") == TOTAL else 0,
            1 if not x.get("demandType") else 0,
            x.get("demandType") or "",
            0 if x.get("due") == TOTAL else 1,
            x.get("due") or "",
        ))
    else:
        # Period (default)
        return sorted(infos, key=lambda x: (
            1 if x.get("due") == TOTAL else 0,
            x.get("due") or "",
        ))


# ══════════════════════════════════════════════════════════
# Ratio 계산 (C# DTO 속성 완전 재현)
# ══════════════════════════════════════════════════════════

def calc_summary_ratios(info: dict) -> dict:
    """C# RarRtfInfo의 computed property 계산"""
    dq = round(info.get("_demandQty", 0), 2)
    rq = round(info.get("_rtfQty", 0), 2)
    oq = round(info.get("_onTimeQty", 0), 2)
    lq_raw = round(info.get("_lateQty", 0), 2)
    lq = 0 if lq_raw == 0 else lq_raw

    info["demandQty"] = dq
    info["rtfQty"] = rq
    info["onTimeQty"] = oq
    info["lateQty"] = lq

    # C#: Math.Floor((rtfQty / demandQty) * 1000) / 10
    info["rtfRatio"] = 0 if dq == 0 else math.floor((rq / dq) * 1000) / 10
    info["onTimeRatio"] = 0 if dq == 0 else math.floor((oq / dq) * 1000) / 10
    info["lateRatio"] = info["rtfRatio"] - info["onTimeRatio"]

    return info


def calc_detail_ratios(info: dict) -> dict:
    """C# RarRtfReportDetail의 computed property 계산"""
    dq = round(info.get("_demandQty", 0), 2)
    rq = round(info.get("_rtfQty", 0), 2)
    oq = round(info.get("_onTimeQty", 0), 2)
    lq = round(info.get("_lateQty", 0), 2)

    info["demandQty"] = dq
    info["rtfQty"] = rq
    info["onTimeQty"] = oq
    info["lateQty"] = lq

    # C# shortQty: Math.Round(_demandQty - _rtfQty, 2, MidpointRounding.AwayFromZero)
    sq_raw = round(info["_demandQty"] - info["_rtfQty"], 2)
    sq = 0 if sq_raw == 0 else sq_raw
    info["shortQty"] = sq

    # C# rtfRatio: _demandQty==0||_rtfQty==0 ? 0 : (shortQty==0 ? 100 : Floor((_rtfQty/_demandQty)*1000)/10)
    if dq == 0 or rq == 0:
        info["rtfRatio"] = 0
    elif sq == 0:
        info["rtfRatio"] = 100
    else:
        info["rtfRatio"] = math.floor((rq / dq) * 1000) / 10

    # C# onTimeRatio: Floor((onTimeQty / demandQty) * 1000) / 10
    info["onTimeRatio"] = 0 if dq == 0 else math.floor((oq / dq) * 1000) / 10

    # C# lateRatio: Round(rtfRatio - onTimeRatio, 2)
    info["lateRatio"] = round(info["rtfRatio"] - info["onTimeRatio"], 2)

    return info


# ══════════════════════════════════════════════════════════
# 서비스 클래스
# ══════════════════════════════════════════════════════════

class RtfReportService:
    """RTF Report 비즈니스 로직"""

    def __init__(self):
        self.repository = RtfReportRepository()

    def dispatch(self, project_id: str, api_url: str, params: dict) -> dict:
        plan_ver = params.get("planVer", "")
        partition_key = (
            f"{project_id}@{plan_ver[:6]}" if len(plan_ver) >= 6 else project_id
        )

        try:
            handler = self._get_handler(api_url)
            if not handler:
                return {
                    "success": False,
                    "error": f"Unknown API URL: {api_url}",
                    "data": [],
                }

            result = handler(partition_key, plan_ver, params)

            if isinstance(result, dict) and "success" in result:
                return result

            data = result
            return {
                "success": True,
                "count": len(data),
                "data": data,
            }

        except Exception as e:
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "data": [],
            }

    def _get_handler(self, api_url: str):
        routes = {
            # ── 필터 쿼리 ──
            "ComCustInRtf": self._handle_customers,
            "ComItemGroupInRtf": self._handle_item_groups,
            "RarRtfReport/GetRegions": self._handle_regions,
            "RarRtfReport/GetDemandTypes": self._handle_demand_types,
            "RarRtfReport/GetProdTypes": self._handle_prod_types,
            # ── 핵심 데이터 (C# in-memory 처리 재현) ──
            "RarRtfReport/Main2": self._handle_main,
            "RarRtfReport/Detail2": self._handle_detail,
            "RarRtfReport/Short": self._handle_short,
            "RarRtfReport/PlanEndDate": self._handle_plan_end_date,
            # ── Phase 2: 신규 엔드포인트 ──
            "RarPeggingReport/DemandInfo": self._handle_demand_info,
            "RarPeggingReport/PegInfoDetail": self._handle_peg_info_detail,
            "RarPlanByProd/Detail2": self._handle_prod_detail2,
            "rarPlanByProd/DemandSummary": self._handle_demand_summary,
            "RarPlanByProd/Summary": self._handle_plan_by_prod_summary,
            "RarPlanByProd/Detail": self._handle_plan_by_prod_detail,
            "RarPlanByProd/Wip": self._handle_wip,
            "RarPlanByProd/GetBufferPlanTarget": self._handle_buffer_plan_target,
            "RarPlanByRes/GetProps": self._handle_get_props,
            "odlReport": self._handle_odl_report,
            # ── Widget 설정 ──
            "PlanDashboard/GetRTFSummaryPopup": self._handle_get_rtf_summary_popup,
            "PlanDashboard/SaveWidgetValue": self._handle_save_widget_value,
        }
        return routes.get(api_url)

    # ══════════════════════════════════════════════════════════
    # 필터 핸들러
    # ══════════════════════════════════════════════════════════

    def _handle_customers(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        return self.repository.get_customers(project_id, plan_ver)

    def _handle_item_groups(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        return self.repository.get_item_groups(project_id, plan_ver)

    def _handle_regions(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        prop_ids = self.repository.get_prop_ids(project_id, plan_ver)
        prop_id = prop_ids.get("productionAreaPropID")
        return self.repository.get_regions(project_id, plan_ver, prop_id)

    def _handle_demand_types(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        return self.repository.get_demand_types(project_id, plan_ver)

    def _handle_prod_types(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        prop_ids = self.repository.get_prop_ids(project_id, plan_ver)
        prop_id = prop_ids.get("prodTypePropID")
        return self.repository.get_prod_types(project_id, plan_ver, prop_id)

    # ══════════════════════════════════════════════════════════
    # Main2 — C# GetSummary 완전 재현
    # ══════════════════════════════════════════════════════════

    def _handle_main(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """
        C# RarRtfReportProcessor.GetSummary 완전 재현.

        1. raw 행 조회
        2. Widget 설정으로 TypeQtyProcessor 구성
        3. Plan End Date 조회
        4. 행 분류 및 집계 (메모리 처리)
        5. 정렬 후 반환
        """
        setting = self._get_widget_setting(project_id, plan_ver, params)
        is_default_uom = params.get("uomType", DEFAULT_UOM) == DEFAULT_UOM
        is_lot_type = setting.get("rtfStd") == LOT

        type_proc = TypeQtyProcessor()
        type_proc.set_category_dict(setting.get("setting", []))

        # Summary type 결정
        summary_type = (params.get("summary") or "").upper()
        aggregate_type = params.get("aggregateType", "")

        # 유효 필터셋 결정
        valid_set = self._get_valid_set(summary_type, params)

        # raw 데이터 조회
        shipment_plans = self.repository.get_raw_shipment_plans(
            project_id, plan_ver, params
        )
        end_date = self._get_plan_end_date(project_id, plan_ver)

        infos: dict[str, dict] = {}
        demands: set[str] = set()
        demand_dict: dict[str, float] = {}

        # Phase 1: LOT가 아닌 경우 demand별 RTF 수량 사전 계산 (C# 완전 재현)
        if not is_lot_type:
            for row in shipment_plans:
                due_date = self._parse_due_date(row.get("dueDate"))
                if due_date is None:
                    continue

                category = AFTER_PLAN if due_date >= end_date else WITHIN_PLAN
                ws = row.get("WAREHOUSE_STATUS") or row.get("warehouse_status")
                typ = type_proc.get_type(category, ws)
                if not typ:
                    continue

                did = row.get("demandID") or ""
                if did not in demand_dict:
                    demand_dict[did] = 0

                demand_dict[did] += self._get_rtf_qty(row, typ, is_default_uom)

        # Phase 2: 집계 (C# 완전 재현)
        for row in shipment_plans:
            due_date = self._parse_due_date(row.get("dueDate"))
            if due_date is None:
                continue

            category = AFTER_PLAN if due_date >= end_date else WITHIN_PLAN
            ws = row.get("WAREHOUSE_STATUS") or row.get("warehouse_status")
            typ = type_proc.get_type(category, ws)
            if not typ:
                continue

            if is_invalid_summary(summary_type, row, valid_set):
                continue

            key = get_key(aggregate_type, summary_type, row)
            due_str = get_date_format(aggregate_type, row)

            if key not in infos:
                infos[key] = self._create_summary_info(
                    1, due_str, row, summary_type, is_total=False
                )

            if TOTAL not in infos:
                infos[TOTAL] = self._create_summary_info(
                    2, TOTAL, row, summary_type, is_total=True
                )

            info = infos[key]
            total_info = infos[TOTAL]

            did = row.get("demandID") or ""
            if did not in demands:
                demands.add(did)
                dq = row.get("demandQty") or 0
                info["demandCnt"] = info.get("demandCnt", 0) + 1
                info["_demandQty"] = info.get("_demandQty", 0) + float(dq)
                total_info["demandCnt"] = total_info.get("demandCnt", 0) + 1
                total_info["_demandQty"] = total_info.get("_demandQty", 0) + float(dq)

            # LOT가 아닌 경우 demand RTF 체크
            if not is_lot_type:
                if did in demand_dict:
                    rtf = round(demand_dict[did], 4)
                    if float(row.get("demandQty") or 0) > rtf:
                        continue

            qty = float(row.get("qty", 0))
            self._update_rtf_qty(info, qty, typ)
            self._update_rtf_qty(total_info, qty, typ)

        # Ratio 계산 및 반환
        result_list = [calc_summary_ratios(v) for v in infos.values()]
        return sort_summary_results(summary_type, result_list)

    # ══════════════════════════════════════════════════════════
    # Detail2 — C# GetDetail 완전 재현
    # ══════════════════════════════════════════════════════════

    def _handle_detail(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """
        C# RarRtfReportProcessor.GetDetail 완전 재현.

        1. raw 행 조회
        2. Widget 설정으로 분류
        3. demandID별 집계
        4. 정렬: OrderBy(rtfRatio).ThenBy(lateRatio==0 ? MaxValue : lateRatio)
                 .ThenBy(dueDate).ThenBy(demandID)
        5. prodStatus 필터
        """
        setting = self._get_widget_setting(project_id, plan_ver, params)

        uom_type = params.get("uomType")
        if not uom_type:
            is_default_uom = setting.get("uomType", DEFAULT_UOM) == DEFAULT_UOM
        else:
            is_default_uom = uom_type == DEFAULT_UOM

        is_lot_type = setting.get("rtfStd") == LOT

        type_proc = TypeQtyProcessor()
        type_proc.set_category_dict(setting.get("setting", []))

        summary_type = (params.get("summary") or "").upper()
        valid_set = self._get_valid_set(summary_type, params)

        shipment_plans = self.repository.get_raw_shipment_plans(
            project_id, plan_ver, params
        )
        end_date = self._get_plan_end_date(project_id, plan_ver)

        demand_dict: dict[str, float] = {}

        # Phase 1: LOT가 아닌 경우 demand별 RTF 수량 사전 계산
        if not is_lot_type:
            for row in shipment_plans:
                due_date = self._parse_due_date(row.get("dueDate"))
                if due_date is None:
                    continue

                category = AFTER_PLAN if due_date >= end_date else WITHIN_PLAN
                ws = row.get("WAREHOUSE_STATUS") or row.get("warehouse_status")
                typ = type_proc.get_type(category, ws)
                if not typ:
                    continue

                did = row.get("demandID") or ""
                if did not in demand_dict:
                    demand_dict[did] = 0
                demand_dict[did] += self._get_rtf_qty(row, typ, is_default_uom)

        # Phase 2: demandID별 집계
        infos: dict[str, dict] = {}

        for row in shipment_plans:
            due_date = self._parse_due_date(row.get("dueDate"))
            if due_date is None:
                continue

            category = AFTER_PLAN if due_date >= end_date else WITHIN_PLAN
            ws = row.get("WAREHOUSE_STATUS") or row.get("warehouse_status")
            typ = type_proc.get_type(category, ws)
            if not typ:
                continue

            if is_invalid_detail(summary_type, row, params, valid_set):
                continue

            did = row.get("demandID") or ""

            if did not in infos:
                # C# RarRtfReportDetail 초기화
                raw_due = row.get("dueDate") or ""
                try:
                    dt = datetime.strptime(raw_due, "%Y%m%d")
                    formatted_due = "{} (-{}, +{})".format(
                        dt.strftime("%Y-%m-%d"),
                        int(row.get("maxEarlinessDay") or 0),
                        int(row.get("maxLatenessDay") or 0),
                    )
                except (ValueError, TypeError):
                    formatted_due = raw_due

                infos[did] = {
                    "demandID": did,
                    "demandPriority": row.get("DEMAND_PRIORITY") or row.get("demand_priority"),
                    "custID": row.get("custID"),
                    "itemGroupID": row.get("itemGroupID"),
                    "itemID": row.get("itemID"),
                    "itemName": row.get("itemName"),
                    "itemLabel": row.get("item_label"),
                    "siteID": row.get("siteID"),
                    "siteName": row.get("siteName"),
                    "dueWeek": get_week_date_from_yyyy_ww(row.get("dueWeek")),
                    "qtyUom": row.get("qtyUom"),
                    "demand_type": row.get("demand_type") or row.get("DEMAND_TYPE"),
                    "item_type": row.get("item_type") or row.get("ITEM_TYPE"),
                    "prod_type": row.get("prod_type") or row.get("PROD_TYPE"),
                    "item_size_type": row.get("item_size_type") or row.get("ITEM_SIZE_TYPE"),
                    "item_spec": row.get("item_spec") or row.get("ITEM_SPEC"),
                    "maxEarlinessDay": row.get("maxEarlinessDay"),
                    "maxLatenessDay": row.get("maxLatenessDay"),
                    "dueDate": formatted_due,
                    "_demandQty": float(row.get("demandQty") or 0),
                    "_rtfQty": 0.0,
                    "_onTimeQty": 0.0,
                    "_lateQty": 0.0,
                    "_earlyQty": 0.0,
                    "prop_json": row.get("prop_json"),
                }

            info = infos[did]

            # LOT가 아닌 경우 demand RTF 체크
            if not is_lot_type:
                if did in demand_dict:
                    rtf = round(demand_dict[did], 4)
                    if float(row.get("demandQty") or 0) > rtf:
                        continue

            qty = float(row.get("raw_qty", 0)) if is_default_uom else float(row.get("raw_conv_qty", 0))
            self._update_detail_qty(info, qty, typ)

        # Ratio 계산
        result_list = [calc_detail_ratios(v) for v in infos.values()]

        # C# 정렬: OrderBy(rtfRatio).ThenBy(lateRatio==0 ? MaxValue : lateRatio)
        #          .ThenBy(dueDate).ThenBy(demandID)
        MAX_VALUE = 2147483647  # int.MaxValue
        result_list.sort(key=lambda x: (
            x.get("rtfRatio", 0),
            MAX_VALUE if x.get("lateRatio", 0) == 0 else x.get("lateRatio", 0),
            x.get("dueDate", ""),
            x.get("demandID", ""),
        ))

        # prodStatus 필터링 (C# 완전 재현)
        prod_status = params.get("prodStatus", "")
        if prod_status and prod_status.lower() != "default":
            ps = prod_status.lower()
            if ps == "short":
                result_list = [x for x in result_list if (x.get("shortQty") or 0) >= 1]
            elif ps == "late":
                result_list = [
                    x for x in result_list
                    if (x.get("shortQty") or 0) == 0 and (x.get("lateQty") or 0) >= 1
                ]
            elif ps == "on_time":
                result_list = [
                    x for x in result_list
                    if x.get("onTimeQty") == x.get("demandQty")
                ]

        return result_list

    # ══════════════════════════════════════════════════════════
    # Helper methods
    # ══════════════════════════════════════════════════════════

    @staticmethod
    def _parse_due_date(due_date_str: str | None) -> datetime | None:
        """yyyyMMdd 문자열을 datetime으로 파싱"""
        if not due_date_str:
            return None
        try:
            # raw dueDate는 yyyyMMdd 형식
            return datetime.strptime(due_date_str[:8], "%Y%m%d")
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_rtf_qty(row: dict, typ: str, is_default_uom: bool) -> float:
        """C# GetRTFQty 완전 재현"""
        qty = float(row.get("raw_qty", 0)) if is_default_uom else float(row.get("raw_conv_qty", 0))
        if typ in (EARLY, ON_TIME, LATE):
            return qty
        return 0

    @staticmethod
    def _update_rtf_qty(info: dict, qty: float, typ: str):
        """C# UpdateRarRtfReport2 (Summary) 완전 재현"""
        if typ == EARLY:
            info["_onTimeQty"] = info.get("_onTimeQty", 0) + qty
            info["_rtfQty"] = info.get("_rtfQty", 0) + qty
        elif typ == ON_TIME:
            info["_onTimeQty"] = info.get("_onTimeQty", 0) + qty
            info["_rtfQty"] = info.get("_rtfQty", 0) + qty
        elif typ == LATE:
            info["_lateQty"] = info.get("_lateQty", 0) + qty
            info["_rtfQty"] = info.get("_rtfQty", 0) + qty
        # SHORT: nothing

    @staticmethod
    def _update_detail_qty(info: dict, qty: float, typ: str):
        """C# UpdateRarRtfReport2 (Detail) 완전 재현"""
        if typ == EARLY:
            info["_onTimeQty"] = info.get("_onTimeQty", 0) + qty
            info["_rtfQty"] = info.get("_rtfQty", 0) + qty
        elif typ == ON_TIME:
            info["_onTimeQty"] = info.get("_onTimeQty", 0) + qty
            info["_rtfQty"] = info.get("_rtfQty", 0) + qty
        elif typ == LATE:
            info["_lateQty"] = info.get("_lateQty", 0) + qty
            info["_rtfQty"] = info.get("_rtfQty", 0) + qty

    @staticmethod
    def _create_summary_info(
        group_idx: int, due: str, row: dict, summary_type: str,
        is_total: bool = False
    ) -> dict:
        """C# RarRtfInfo 생성자 재현"""
        info = {
            "demandID": row.get("demandID"),
            "groupIdx": group_idx,
            "due": due,
            "demandCnt": 0,
            "_demandQty": 0.0,
            "_rtfQty": 0.0,
            "_onTimeQty": 0.0,
            "_lateQty": 0.0,
            "qtyUom": row.get("qtyUom"),
        }

        if is_total:
            info["custID"] = TOTAL
            info["itemGroupID"] = TOTAL
            info["demandType"] = TOTAL
            info["region"] = TOTAL
        else:
            info["custID"] = row.get("custID")
            info["itemGroupID"] = row.get("itemGroupID")
            info["demandType"] = row.get("demand_type") or row.get("DEMAND_TYPE")
            info["region"] = row.get("production_area")

        return info

    @staticmethod
    def _get_valid_set(summary_type: str, params: dict) -> set | None:
        """summary type에 따른 유효 필터셋 결정"""
        if summary_type == CUST:
            customers = params.get("customers")
            return set(customers) if customers else None
        elif summary_type == ITEMGROUP:
            groups = params.get("itemGroupIDs")
            return set(groups) if groups else None
        elif summary_type == REGION:
            regions = params.get("regions")
            return set(regions) if regions else None
        elif summary_type == DEMANDTYPE:
            types = params.get("demandTypes")
            return set(types) if types else None
        return None

    def _get_widget_setting(
        self, project_id: str, plan_ver: str, params: dict
    ) -> dict:
        """Widget 설정 조회"""
        user_id = params.get("userID", "")
        return get_rtf_summary_popup(project_id, user_id, plan_ver)

    def _get_plan_end_date(
        self, project_id: str, plan_ver: str
    ) -> datetime:
        """Plan End Date 조회"""
        rows = self.repository.get_plan_end_date(project_id, plan_ver)
        if rows and rows[0].get("plan_end_date"):
            val = rows[0]["plan_end_date"]
            if isinstance(val, datetime):
                return val
            if isinstance(val, str):
                for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(val, fmt)
                    except ValueError:
                        continue
        # 기본값: 먼 미래
        return datetime(2099, 12, 31)

    # ══════════════════════════════════════════════════════════
    # 기타 핸들러 (변경 없음)
    # ══════════════════════════════════════════════════════════

    def _handle_short(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        demand_id = params.get("demandID", "")
        uom_type = params.get("uomType", "DEFAULT")
        return self.repository.get_short(
            project_id, plan_ver, demand_id, uom_type
        )

    def _handle_plan_end_date(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        return self.repository.get_plan_end_date(project_id, plan_ver)

    def _handle_demand_info(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        demand_id = params.get("demandID", "")
        return self.repository.get_demand_info(
            project_id, plan_ver, demand_id
        )

    def _handle_peg_info_detail(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        demand_id = params.get("demandID", "")
        uom_type = params.get("uomType", "DEFAULT")
        return self.repository.get_peg_info_detail(
            project_id, plan_ver, demand_id, uom_type
        )

    def _handle_prod_detail2(
        self, project_id: str, plan_ver: str, params: dict
    ) -> dict:
        """
        C# RarPlanDetailProcessor.GetDetails 완전 재현.

        detailType = "oper_group_id" (항상 oper_group 모드)
        1. GetDemands → demand별 item_id/site_id/buffer_id
        2. 각 demand에 대해 GetDetail 호출
        3. SetTotalQty → usedTotalQty 계산
        """
        demand_id = params.get("demandID", "")
        uom_type = params.get("uomType", "DEFAULT")
        is_default_uom = uom_type != "CONVERSION"

        demands = self.repository.get_demands(
            project_id, plan_ver, demand_id
        )
        result: list[dict] = []

        for demand in demands:
            d_item = demand.get("item_id", "")
            d_site = demand.get("site_id", "")
            d_buffer = demand.get("buffer_id", "")

            detail_rows = self._get_detail_for_demand(
                project_id, plan_ver, demand_id,
                d_item, d_site, d_buffer, is_default_uom,
            )
            result.extend(detail_rows)

        # C# controller returns { detail, period }
        period = self.repository.get_prod_detail2_section(
            project_id, plan_ver, demand_id
        )

        if any(r.get("planDate") for r in result):
            return {"success": True, "data": {"detail": result, "period": period}}
        else:
            return {"success": True, "data": {"detail": None, "period": period}}

    def _get_detail_for_demand(
        self, project_id: str, plan_ver: str, demand_id: str,
        item_id: str, site_id: str, buffer_id: str,
        is_default_uom: bool,
    ) -> list[dict]:
        """C# RarPlanDetailProcessor.GetDetail (per demand)"""
        repo = self.repository

        # 1) WIP dict: key=(item_id|site_id|buffer_id|oper_id) → wip_qty
        wip_dict: dict[str, float] = {}
        wips = repo.get_wip_for_detail(
            project_id, plan_ver, item_id, site_id, buffer_id
        )
        for w in wips:
            key = _create_key(
                w.get("item_id") or "", w.get("site_id") or "",
                w.get("buffer_id") or "", w.get("oper_id") or "",
            )
            wip_dict[key] = wip_dict.get(key, 0) + float(w.get("wip_qty") or 0)

        # 2) Peg dict: key=(item_id|site_id|buffer_id|oper_id) → peg_qty
        peg_dict: dict[str, float] = {}
        pegs = repo.get_peg_info_for_detail(
            project_id, plan_ver, demand_id, is_default_uom
        )
        for p in pegs:
            key = _create_key(
                p.get("item_id") or "", p.get("site_id") or "",
                p.get("buffer_id") or "", p.get("oper_id") or "",
            )
            peg_dict[key] = peg_dict.get(key, 0) + float(p.get("peg_qty") or 0)

        # 3) Buffer dict: buffer_id → buffer_seq
        buffer_dict: dict[str, int] = {}
        buffers_data = repo.get_buffer_masters(project_id, plan_ver)
        for b in buffers_data:
            buffer_dict[b.get("buffer_id", "")] = int(b.get("buffer_seq") or 0)

        # 4) Oper group dict: oper_id → oper_group_id
        oper_group_dict: dict[str, str] = {}
        opers_data = repo.get_oper_masters(project_id, plan_ver)
        for o in opers_data:
            ogid = o.get("oper_group_id")
            if ogid:
                oper_group_dict[o.get("oper_id", "")] = ogid

        # 5) BOM network → bom_path_dict
        bom_network = repo.get_bom_network(
            project_id, plan_ver, item_id, site_id, buffer_id
        )
        routing_ids = list(set(
            r.get("routing_id") or "" for r in bom_network
            if r.get("routing_id")
        ))
        routing_oper_dict: dict[str, list[str]] = {}
        if routing_ids:
            routing_opers = repo.get_routing_opers(
                project_id, plan_ver, routing_ids
            )
            for ro in routing_opers:
                rid = ro.get("routing_id", "")
                oid = ro.get("oper_id", "")
                routing_oper_dict.setdefault(rid, []).append(oid)

        # Build bom_path_dict: key → {item_id, site_id, buffer_id, oper_id, buffer_seq}
        bom_path_dict: dict[str, dict] = {}

        for bom in bom_network:
            rid = bom.get("routing_id", "")
            oper_list = routing_oper_dict.get(rid)

            if oper_list:
                for oper_id_val in oper_list:
                    self._add_bom_path(
                        bom_path_dict, bom, oper_id_val, True, buffer_dict
                    )
                    self._add_bom_path(
                        bom_path_dict, bom, None, False, buffer_dict
                    )
            else:
                self._add_bom_path(
                    bom_path_dict, bom, None, True, buffer_dict
                )
                self._add_bom_path(
                    bom_path_dict, bom, None, False, buffer_dict
                )

        if not bom_path_dict:
            return []

        # 6) Item dict for items in bom_path
        all_item_ids = list(set(
            v["item_id"] for v in bom_path_dict.values() if v.get("item_id")
        ))
        item_dict: dict[str, str] = {}
        if all_item_ids:
            items_data = repo.get_item_masters_by_ids(
                project_id, plan_ver, all_item_ids
            )
            for it in items_data:
                item_dict[it.get("item_id", "")] = it.get("item_type", "")

        # 7) Prod plan dict from rpt_oper_group_plan
        prod_dict: dict[str, dict[str, dict]] = {}
        min_date = None
        max_date = None

        oper_plans = repo.get_oper_group_plans(
            project_id, plan_ver, demand_id
        )
        for row in oper_plans:
            r_item = row.get("item_id") or ""
            r_site = row.get("site_id") or ""
            r_buffer = row.get("buffer_id") or ""
            r_oper = row.get("oper_id") or ""
            r_plan_date = row.get("plan_date") or ""

            key = _create_key(r_item, r_site, r_buffer, r_oper)

            if key not in prod_dict:
                prod_dict[key] = {}

            dt = _parse_date_yyyymmdd(r_plan_date)
            if dt is None:
                continue

            if min_date is None or dt < min_date:
                min_date = dt
            if max_date is None or dt > max_date:
                max_date = dt

            date_key = dt.strftime("%Y-%m-%d")
            plan_month = dt.strftime("%Y-%m")

            qty = float(row.get("out_plan_qty") or 0) if is_default_uom \
                else float(row.get("out_plan_conv_qty") or 0)

            if date_key not in prod_dict[key]:
                prod_dict[key][date_key] = {
                    "itemID": r_item,
                    "siteID": r_site,
                    "bufferID": r_buffer,
                    "bufferSeq": int(row.get("buffer_seq") or 0),
                    "operID": r_oper,
                    "operGroupID": oper_group_dict.get(r_oper),
                    "resID": None,
                    "itemType": row.get("item_type") or "",
                    "planDate": date_key,
                    "planWeek": date_key,
                    "planMonth": plan_month,
                    "outPlanQty": 0,
                    "wipQty": 0,
                    "pegQty": 0,
                    "usedTotalQty": 0,
                }
            prod_dict[key][date_key]["outPlanQty"] += qty

        # 8) Generate results: iterate bom_path × date range
        result: list[dict] = []

        for bom_key, info in bom_path_dict.items():
            wip_qty = wip_dict.get(bom_key, 0)
            peg_qty = peg_dict.get(bom_key, 0)

            if bom_key not in prod_dict:
                prod_dict[bom_key] = {}

            date_dict = prod_dict[bom_key]

            if min_date is None or max_date is None or min_date > max_date:
                entry = self._create_prod_summary(
                    info, None, None, None, oper_group_dict, item_dict
                )
                result.append(entry)
                continue

            dt = min_date
            while dt <= max_date:
                dt_str = dt.strftime("%Y-%m-%d")
                plan_month = dt.strftime("%Y-%m")

                if dt_str not in date_dict:
                    entry = self._create_prod_summary(
                        info, dt_str, plan_month, dt_str,
                        oper_group_dict, item_dict,
                    )
                    date_dict[dt_str] = entry

                value = date_dict[dt_str]
                value["wipQty"] = wip_qty
                value["pegQty"] = peg_qty
                result.append(value)

                dt = dt + _ONE_DAY

        # 9) SetTotalQty
        for bom_key in bom_path_dict:
            if bom_key in prod_dict:
                total = sum(
                    v.get("outPlanQty", 0) for v in prod_dict[bom_key].values()
                )
                for v in prod_dict[bom_key].values():
                    v["usedTotalQty"] = total

        return result

    @staticmethod
    def _add_bom_path(
        bom_path_dict: dict, bom: dict, oper_id: str | None,
        is_from: bool, buffer_dict: dict,
    ):
        """C# AddBomPath"""
        if is_from:
            b_item = bom.get("from_item_id") or ""
            b_site = bom.get("from_site_id") or ""
            b_buffer = bom.get("from_buffer_id") or ""
        else:
            b_item = bom.get("to_item_id") or ""
            b_site = bom.get("to_site_id") or ""
            b_buffer = bom.get("to_buffer_id") or ""

        b_seq = buffer_dict.get(b_buffer, 0)

        # C# logic: remove entry without oper first, then add with oper
        key_no_oper = _create_key(b_item, b_site, b_buffer, "")
        key_with_oper = _create_key(b_item, b_site, b_buffer, oper_id or "")

        if oper_id:
            bom_path_dict.pop(key_no_oper, None)

        if key_with_oper not in bom_path_dict:
            bom_path_dict[key_with_oper] = {
                "item_id": b_item,
                "site_id": b_site,
                "buffer_id": b_buffer,
                "oper_id": oper_id or "",
                "buffer_seq": b_seq,
            }

    @staticmethod
    def _create_prod_summary(
        info: dict, plan_date: str | None, plan_month: str | None,
        plan_week: str | None, oper_group_dict: dict, item_dict: dict,
    ) -> dict:
        """C# CreateSummary"""
        oper_id = info.get("oper_id", "")
        item_id = info.get("item_id", "")
        return {
            "itemID": item_id,
            "siteID": info.get("site_id", ""),
            "bufferID": info.get("buffer_id", ""),
            "bufferSeq": info.get("buffer_seq", 0),
            "operID": oper_id,
            "operGroupID": oper_group_dict.get(oper_id),
            "resID": None,  # C# CreateDetailItem always passes null for resID
            "planDate": plan_date,
            "planMonth": plan_month,
            "planWeek": plan_week,
            "outPlanQty": 0,
            "wipQty": 0,
            "pegQty": 0,
            "usedTotalQty": 0,
            "itemType": item_dict.get(item_id, ""),
        }

    # ══════════════════════════════════════════════════════════
    # DemandSummary — C# CalculateDemandSummary 완전 재현
    # ══════════════════════════════════════════════════════════

    def _handle_demand_summary(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """C# RarPlanSummaryProcessor.CalculateDemandSummary 완전 재현"""
        demand_ids = params.get("demandIDs", [])
        if not demand_ids:
            return []

        summary_dict = self._build_summary_dict(project_id, plan_ver, params)
        if not summary_dict:
            return []

        # Per-demand: wipQty, pegQty, pegRatio
        for key, s in summary_dict.items():
            s["wipQty"] = self.repository.get_wip_qty_by_isb(
                project_id, plan_ver,
                s["demandItemID"], s["demandSiteID"], s["demandBufferID"],
            )
            peg_qty = self.repository.get_peg_qty_from_demand_plan_isb(
                project_id, plan_ver,
                s["demandID"], s["demandItemID"], s["demandSiteID"], s["demandBufferID"],
            )
            s["pegQty"] = peg_qty

            if not peg_qty or peg_qty == 0:
                s["pegRatio"] = 0
            else:
                wip = s["wipQty"] or 0
                if wip == 0:
                    s["pegRatio"] = 0
                else:
                    s["pegRatio"] = round((peg_qty / wip) * 100)

        # Remove internal field
        for s in summary_dict.values():
            s.pop("_dueDate", None)

        return list(summary_dict.values())

    # ══════════════════════════════════════════════════════════
    # Summary — C# CalculateSummary 완전 재현
    # ══════════════════════════════════════════════════════════

    def _handle_plan_by_prod_summary(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        """C# RarPlanSummaryProcessor.CalculateSummary + Controller 후처리 완전 재현"""
        item_ids = params.get("itemIDs", [])
        customers = params.get("customers", [])
        demand_ids = params.get("demandIDs", [])
        if not item_ids and not customers and not demand_ids:
            return []

        summary_dict = self._build_summary_dict(project_id, plan_ver, params)
        if not summary_dict:
            return []

        # custDict
        cust_ids = [s["custID"] for s in summary_dict.values() if s.get("custID")]
        cust_dict = self.repository.get_cust_names(project_id, plan_ver, cust_ids) if cust_ids else {}

        for key, s in summary_dict.items():
            # dateDiff
            if s.get("shipmentDate"):
                try:
                    ship_dt = datetime.strptime(s["shipmentDate"], "%Y-%m-%d")
                    due_dt = s.get("_dueDate")
                    if due_dt:
                        s["dateDiff"] = (ship_dt - due_dt).days
                except (ValueError, TypeError):
                    pass

            # shortQty, rtfRatio
            demand_qty = s.get("demandQty") or 0
            shipment_qty = s.get("shipmentQty") or 0
            s["shortQty"] = demand_qty - shipment_qty
            if demand_qty and demand_qty != 0:
                s["rtfRatio"] = round((shipment_qty / demand_qty) * 100)
            else:
                s["rtfRatio"] = 0

            # custName
            if s.get("custID") and s["custID"] in cust_dict:
                s["custName"] = cust_dict[s["custID"]]

            # Controller: clear dates if rtfRatio <= 0
            if (s.get("rtfRatio") or 0) <= 0:
                s["warehousingDate"] = None
                s["shipmentDate"] = None
                s["dateDiff"] = None

        # Remove internal field
        for s in summary_dict.values():
            s.pop("_dueDate", None)

        return list(summary_dict.values())

    # ── Summary 공통 ──

    def _build_summary_dict(
        self, project_id: str, plan_ver: str, params: dict
    ) -> dict[str, dict]:
        """
        C# SetSummaryUsingDemand + SetSummaryUsingSafetyStockDemand
        + SetSummaryUsingShipmentPlan 공통 처리
        """
        summary_dict: dict[str, dict] = {}

        # 1. SetSummaryUsingDemand
        demands = self.repository.get_demands_for_summary(
            project_id, plan_ver, params
        )
        for d in demands:
            key = d.get("demand_id") or ""
            due_str = d.get("due_date") or ""
            due_dt = _parse_date_yyyy_mm_dd(due_str)
            if due_dt is None:
                continue
            if key in summary_dict:
                continue
            summary_dict[key] = {
                "demandID": key,
                "demandItemID": d.get("item_id") or "",
                "demandItemName": d.get("demand_item_name") or "",
                "demandSiteID": d.get("site_id") or "",
                "demandBufferID": d.get("buffer_id") or "",
                "demandQty": float(d.get("demand_qty") or 0),
                "dueDate": due_dt,
                "custID": d.get("cust_id"),
                "onTimeQty": 0,
                "lateQty": 0,
                "shipmentQty": 0,
                "warehousingDate": None,
                "shipmentDate": None,
                "_dueDate": due_dt,  # internal for dateDiff calc
            }

        # 2. SetSummaryUsingSafetyStockDemand
        ss_demands = self.repository.get_safety_stock_demands_for_summary(
            project_id, plan_ver, params
        )
        for sd in ss_demands:
            key = sd.get("demand_id") or ""
            if key in summary_dict:
                continue
            due_str = sd.get("due_date") or ""
            due_dt = _parse_date_yyyy_mm_dd(due_str) or _parse_date_yyyymmdd(due_str)
            summary_dict[key] = {
                "demandID": key,
                "demandItemID": sd.get("item_id") or "",
                "demandItemName": "",
                "demandSiteID": sd.get("site_id") or "",
                "demandBufferID": sd.get("buffer_id") or "",
                "demandQty": float(sd.get("demand_qty") or 0),
                "dueDate": due_dt,
                "custID": sd.get("cust_id"),
                "onTimeQty": 0,
                "lateQty": 0,
                "shipmentQty": 0,
                "warehousingDate": None,
                "shipmentDate": None,
                "_dueDate": due_dt,
            }

        if not summary_dict:
            return summary_dict

        # 3. SetSummaryUsingShipmentPlan
        demand_id_list = list(summary_dict.keys())
        shipments = self.repository.get_shipment_plans_for_summary(
            project_id, plan_ver, demand_id_list
        )
        for plan in shipments:
            did = plan.get("demand_id") or ""
            if did not in summary_dict:
                continue
            s = summary_dict[did]

            s["onTimeQty"] += float(plan.get("on_time_qty") or 0)
            s["lateQty"] += float(plan.get("late_qty") or 0)
            s["shipmentQty"] += float(plan.get("shipment_qty") or 0)

            # Max shipmentDate (yyyyMMdd → yyyy-MM-dd)
            raw_ship = plan.get("shipment_date") or ""
            ship_parsed = _parse_date_yyyymmdd(raw_ship)
            if ship_parsed:
                ship_str = ship_parsed.strftime("%Y-%m-%d")
                if s["shipmentDate"] is None or s["shipmentDate"] < ship_str:
                    s["shipmentDate"] = ship_str

            # Max warehousingDate (yyyyMMdd → yyyy-MM-dd)
            raw_wh = plan.get("warehouse_in_date") or ""
            wh_parsed = _parse_date_yyyymmdd(raw_wh)
            if wh_parsed:
                wh_str = wh_parsed.strftime("%Y-%m-%d")
                if s["warehousingDate"] is None or s["warehousingDate"] < wh_str:
                    s["warehousingDate"] = wh_str

        # Convert dueDate datetime → string for JSON
        for s in summary_dict.values():
            if isinstance(s.get("dueDate"), datetime):
                s["dueDate"] = s["dueDate"].strftime("%Y-%m-%d")

        return summary_dict

    def _handle_plan_by_prod_detail(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        demand_id = params.get("demandID", "")
        return self.repository.get_plan_by_prod_detail(
            project_id, plan_ver, demand_id
        )

    def _handle_wip(
        self, project_id: str, plan_ver: str, _params: dict
    ) -> list[dict]:
        return self.repository.get_wip(project_id, plan_ver)

    def _handle_buffer_plan_target(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        return self.repository.get_buffer_plan_target(
            project_id, plan_ver, params
        )

    def _handle_get_props(
        self, project_id: str, plan_ver: str, params: dict
    ) -> dict:
        """C# GetPropDict — 단일 dict 반환"""
        item_id = params.get("itemID", "")
        return self.repository.get_item_props(
            project_id, plan_ver, item_id
        )

    def _handle_odl_report(
        self, project_id: str, plan_ver: str, params: dict
    ) -> list[dict]:
        return self.repository.get_odl_report(
            project_id, plan_ver, params
        )

    def _handle_get_rtf_summary_popup(
        self, project_id: str, plan_ver: str, params: dict
    ) -> dict:
        user_id = params.get("userID", "")
        data = get_rtf_summary_popup(project_id, user_id, plan_ver)
        return {
            "success": True,
            "data": data,
        }

    def _handle_save_widget_value(
        self, project_id: str, plan_ver: str, params: dict
    ) -> dict:
        rows = params.get("_rows", [])
        if not rows:
            rows = [params]
        count = save_widget_value(project_id, rows)
        return {
            "success": True,
            "count": count,
        }
