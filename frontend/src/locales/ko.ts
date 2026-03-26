/**
 * 한국어 번역 리소스
 * APS 원본과 동일한 키 체계 사용
 */
export default {
  // === 공통 ===
  "text-total": "전체",
  "text-description": "설명",
  "text-warning": "경고",
  "text-category": "분류",
  "text-qty_uom": "단위",
  "text-item_id": "제품 코드",
  "text-item_group": "제품 그룹",
  "text-item_type": "제품 유형",
  "text-cust_name": "고객 이름",
  "text-prod_type": "생산 유형",
  "text-demand_qty": "수요 수량",
  "text-aggregate_type": "납기 기준",
  "text-summary_type": "요약",
  "MOZ-DATA_EMPTY": "데이터 없음",

  // === 생산 상태 ===
  "text-short-prod": "생산 차질",
  "text-late_production": "지연 생산",
  "text-on_time_production": "정시 생산",
  "text-isu_early_prod": "조기 생산",

  // === 지역/상세 필터 ===
  "text-isu_region": "지역",
  "text-isu_detail": "상세",
  "text-isu_entire": "전체",
  "text-isu_region_daegu": "대구",
  "text-isu_region_hk": "HK",
  "text-isu_hk_final_prod": "HK 완제",
  "text-isu_hk_semi_prod": "HK 반제",
  "text-prod_status": "생산 상태",

  // === RTF 관련 ===
  "text-isu_rtf_rate": "생산 비율",
  "text-isu_early": "조기",
  "text-isu_ontime": "정시",
  "text-isu_late": "지연",
  "text-isu_short": "차질",
  "text-isu_otd_expected_rate": "납기 준수율",
  "text-isu_otd_expected_qty": "납기 준수량",
  "text-isu_prod_qty": "생산 수량",
  "text-isu_early_ontime_late": "(조기 + 정시 + 지연)",
  "text-isu_mo_id": "주문 코드",
  "text-simple_short_reason": "차질 사유",
  "text-isu_used_total": "사용 합계",

  // === Sub1 컬럼 ===
  "text-due_month": "납기(월)",
  "text-due_week": "납기(주)",
  "text-customer": "고객",

  // === Sub2 Short 팝업 ===
  "text-short-reason-detail-view": "Short 사유 상세",
  "text-short_type": "Short 유형",
  "text-short_category": "차질 사유 그룹",
  "text-short_reason": "생산 차질 사유",
  "text-short_qty": "생산 차질 수량",
  "text-short_detail_info": "생산 차질 상세 정보",
  "text-isb_id": "제품-사이트-버퍼 코드",
  "text-bom_id": "BOM 코드",
  "text-routing_id": "라우팅 코드",
  "text-oper_id": "공정 코드",
  "text-res_id": "설비 코드",
  "text-view_detail": "상세 보기",

  // === Detail (Pivot) ===
  "text-oper_group_id": "공정 그룹",
  "text-site_id": "사이트",
  "text-prod_qty": "생산량",
  "text-plan_date": "계획일",
  "text-plan_month": "계획 월",

  // === 확정 (Freeze) ===
  "text-frozen": "확정",
  "text-frozen_cancel": "확정 취소",
  "text-plan_freeze": "계획 확정",
  "text-plan_freeze_info_management": "계획 확정 정보 관리",
  "text-info_frozen_plan_ver": "확정 계획: {{planVer}} ({{planCycle}})",
  "text-repeat_freeze": "아래 정보로 확정 처리 하시겠습니까?",
  "text-repeat_modify_desc": "확정 계획에 대한 설명을 수정할 수 있습니다.",
  "text-plan_cycle": "생산 계획 주기",
  "text-frozen_plan_version": "확정 계획 버전",
  "text-frozen_plan_period": "확정 계획 기간",
  "text-frozen_officer": "확정 처리 담당자",
  "text-confirm_cancel_popup_info": "확정 정보가 모두 삭제됩니다. 확정 계획을 취소하시겠습니까?",

  // === 위젯 설정 팝업 ===
  "text-popup-rtf_aggregate_type_setting": "집계 기준 설정",
  "desc-rtf_aggregate_type_setting": "RTF 집계 기준을 LOT 또는 DEMAND 단위로 설정합니다.",
  "text-popup-qty_uom_setting": "수량 UOM 설정",
  "desc-qty_uom_setting": "표시할 수량 UOM을 선택합니다.",

  // === 수요 정보 팝업 ===
  "text-demand_info": "수요 정보",
  "text-demand_id": "수요 ID",
  "text-due_date": "납기일",

  // === Peg / BOM 팝업 ===
  "text-peg_info_detail": "Peg 정보 상세",
  "text-peg_qty": "Peg 수량",
  "text-bom_structure": "BOM 구조",

  // === 토스트 메시지 ===
  "msg-toast-get_error": "에러가 발생 했습니다.",
  "msg-toast-save_error": "저장 중 에러가 발생 했습니다.",
  "msg-toast-plan_ver_frozen": "계획이 확정되었습니다.",
  "msg-toast-frozen_cancel": "확정 취소되었습니다.",
} as const;
