/**
 * OnTime Rescheduled Plan Result API & Composable
 *
 * Replan RTF 납기준수율 분석 페이지의 데이터 계층.
 * 기존 APS 뷰의 apiCall/vue-query 패턴을 custom API(axios) 기반으로 전환.
 */
import { api, getProjectId } from "@/api/client";
import { ref, computed, type Ref } from "vue";

// ===== API Base URLs =====

const REPLAN_RTF_URL = () =>
  `/api/custom/backend/${getProjectId()}/replan-rtf`;
const RTF_REPORT_URL = () =>
  `/api/custom/backend/${getProjectId()}/rtf-report`;
const FREEZE_URL = () =>
  `/api/custom/backend/${getProjectId()}/freeze`;
const DASHBOARD_URL = () =>
  `/api/custom/backend/${getProjectId()}/plan-dashboard`;

// ===== Types =====

/** 공통 API 응답 */
export interface ApiResponse<T = any> {
  success: boolean;
  count?: number;
  data: T;
  message?: string;
  error?: string;
}

/** Replan RTF 요약 행 */
export interface ReplanRtfSummary {
  due: string;
  custID: string;
  itemGroupID: string;
  prodType: string;
  demandCnt: number;
  demandQty: number;
  earlyQty: number;
  onTimeQty: number;
  lateQty: number;
  shortQty: number;
  ratio_rtf: number;
  ratio_early: number;
  ratio_ontime: number;
  ratio_late: number;
  ratio_short: number;
  [key: string]: any;
}

/** Replan RTF 상세 행 */
export interface ReplanRtfDetail {
  demandID: string;
  itemID: string;
  itemLabel: string;
  custID: string;
  demandQty: number;
  earlyQty: number;
  onTimeQty: number;
  lateQty: number;
  shortQty: number;
  rtfQty: number;
  ratio_rtf: number;
  ratio_early: number;
  ratio_ontime: number;
  ratio_late: number;
  ratio_short: number;
  dueDate: string;
  dueWeek: string;
  showDetailCol?: string;
  [key: string]: any;
}

/** 생산 상세 응답 */
export interface ProdDetailResponse {
  detail: ProdDetailRow[];
  period: string[];
}

/** 생산 상세 행 */
export interface ProdDetailRow {
  item_id: string;
  oper_group_id: string;
  oper_id: string;
  site_id: string;
  item_type: string;
  wip_qty: number;
  peg_qty: number;
  total_prod_qty: number;
  prod_qty: number;
  plan_date: string;
  plan_month: string;
  [key: string]: any;
}

/** Short 사유 행 */
export interface ShortData {
  short_type: string;
  short_category: string;
  short_reason: string;
  short_qty: number;
  qty_uom: string;
  [key: string]: any;
}

/** Demand Summary */
export interface DemandSummaryData {
  demand_qty: number;
  shipment_qty: number;
  wip_qty: number;
  peg_qty: number;
  peg_ratio: number;
  warehousing_date: string;
  shipment_date: string;
  [key: string]: any;
}

/** 필터 옵션 */
export interface FilterOption {
  value: string;
  label?: string;
  [key: string]: any;
}

/** Frozen 상태 */
export interface FrozenStatus {
  frozen_plan_ver: string | null;
  is_frozen_plan: boolean;
  frozen_desc: string;
  frozen_period_desc: string;
  plan_cycle_id: string;
  [key: string]: any;
}

// ===== 요청 파라미터 타입 =====

export interface ReplanSummaryParams {
  planVer: string;
  aggregateType: string;
  summary: string;
  customers?: string[];
  itemGroupIDs?: string[];
  prodTypes?: string[];
  prodStatus?: string | null;
  uomType: string;
  productionArea?: string | null;
}

export interface ReplanDetailParams {
  planVer: string;
  aggregateType: string;
  summary: string;
  dueMonth?: string;
  dueWeek?: string;
  customers?: string[];
  itemGroupIDs?: string[];
  prodTypes?: string[];
  prodStatus?: string | null;
  uomType: string;
  productionArea?: string | null;
}

export interface ReplanProdDetailParams {
  planVer: string;
  demandID: string;
  uomType: string;
}

export interface FreezeExecuteParams {
  planCycleID: string;
  planVer: string;
  createUser: string;
  description: string;
}

// ===== API Functions =====

// --- Replan RTF APIs ---

export const fetchSummary = (params: ReplanSummaryParams) =>
  api.post<ApiResponse<ReplanRtfSummary[]>>(`${REPLAN_RTF_URL()}/summary`, params);

export const fetchDetail = (params: ReplanDetailParams) =>
  api.post<ApiResponse<ReplanRtfDetail[]>>(`${REPLAN_RTF_URL()}/detail`, params);

export const fetchProdDetail = (params: ReplanProdDetailParams) =>
  api.post<ApiResponse<ProdDetailResponse>>(`${REPLAN_RTF_URL()}/prod-detail`, params);

export const fetchProdTypes = (planVer: string) =>
  api.get<ApiResponse<FilterOption[]>>(`${REPLAN_RTF_URL()}/filters/prod-types`, {
    params: { planVer },
  });

// --- Reuse RTF Report APIs ---

export const fetchShort = (params: { planVer: string; demandID: string; uomType?: string }) =>
  api.post<ApiResponse<ShortData[]>>(`${RTF_REPORT_URL()}/short`, params);

export const fetchDemandSummary = (params: { planVer: string; demandIDs: string[]; uomType?: string }) =>
  api.post<ApiResponse<DemandSummaryData[]>>(`${RTF_REPORT_URL()}/demand-summary`, params);

export const fetchDemandInfo = (params: { planVer: string; demandID: string }) =>
  api.post<ApiResponse>(`${RTF_REPORT_URL()}/demand-info`, params);

export const fetchPegInfo = (params: { planVer: string; demandID: string }) =>
  api.post<ApiResponse>(`${RTF_REPORT_URL()}/peg-info`, params);

export const fetchBomMap = (params: { planVer: string; demandID: string; onlyTargetBom?: boolean; uomType?: string }) =>
  api.post<ApiResponse>(`${RTF_REPORT_URL()}/bom-map`, params);

export const fetchItemProps = (params: { planVer: string; itemID: string }) =>
  api.post<ApiResponse>(`${RTF_REPORT_URL()}/item-props`, params);

export const fetchDemandRecord = (params: { planVer: string; demandID: string }) =>
  api.post<ApiResponse>(`${RTF_REPORT_URL()}/demand-record`, params);

export const fetchBufferPlanTarget = (params: { planVer: string; demandID: string }) =>
  api.post<ApiResponse>(`${RTF_REPORT_URL()}/buffer-plan-target`, params);

// --- Filter APIs ---

export const fetchFilterCustomers = (planVer: string) =>
  api.get<ApiResponse<FilterOption[]>>(`${RTF_REPORT_URL()}/filters/customers`, {
    params: { plan_ver: planVer },
  });

export const fetchFilterItemGroups = (planVer: string) =>
  api.get<ApiResponse<FilterOption[]>>(`${RTF_REPORT_URL()}/filters/item-groups`, {
    params: { plan_ver: planVer },
  });

// --- Freeze APIs ---

export const fetchFrozenStatus = (planCycleID: string) =>
  api.get<ApiResponse<FrozenStatus[]>>(`${FREEZE_URL()}/status`, {
    params: { planCycleID },
  });

export const updateFrozenDesc = (params: { planCycleID: string; description: string }) =>
  api.put<ApiResponse>(`${FREEZE_URL()}/description`, params);

export const executeFreeze = (params: FreezeExecuteParams) =>
  api.post<ApiResponse>(`${FREEZE_URL()}/execute`, params);

export const cancelFreeze = (params: { planCycleID: string; planVer: string; createUser: string }) =>
  api.post<ApiResponse>(`${FREEZE_URL()}/cancel`, params);

export const fetchFrozenPeriod = (params: { plan_ver: string }) =>
  api.post<ApiResponse>(`${FREEZE_URL()}/period`, params);

// --- Widget Settings APIs (reuse plan-dashboard) ---

export const fetchWidgetSettings = (userId: string, menuId: string) =>
  api.get<ApiResponse>(`${DASHBOARD_URL()}/settings`, {
    params: { userId, menuId },
  });

export const saveWidgetSettings = (params: { userId: string; menuId: string; widgetId: string; widgetValue: string }) =>
  api.put<ApiResponse>(`${DASHBOARD_URL()}/settings`, params);

// ===== Composable =====

export type SummaryType = "itemGroup" | "cust" | "prodType";
export type ProdStatusType = "default" | "on_time" | "late" | "short" | "early";

export function useOnTimeRescheduledPlanResult() {
  // === Filter State ===
  const summaryType = ref<SummaryType>("itemGroup");
  const aggType = ref<string>("MONTH");
  const uomType = ref<string>("DEFAULT");
  const prodStatus = ref<ProdStatusType>("default");
  const region = ref<string>("default");
  const hkDetail = ref<string>("HK");

  // === Committed (snapshot) filters ===
  const committedSummaryType = ref<SummaryType>("itemGroup");
  const committedAggType = ref<string>("MONTH");
  const committedUomType = ref<string>("DEFAULT");
  const committedProdStatus = ref<ProdStatusType>("default");
  const committedCustomers = ref<string[]>([]);
  const committedItemGroups = ref<string[]>([]);
  const committedProdTypes = ref<string[]>([]);

  // === Selection State ===
  const selectedDemandID = ref<string>("");
  const selectedSummaryItem = ref<any>(null);

  // === Filter Sources ===
  const prodTypeSource: Ref<FilterOption[]> = ref([]);
  const customerSource: Ref<any[]> = ref([]);
  const itemGroupSource: Ref<any[]> = ref([]);

  // === Selected Filters ===
  const selectedCustomers = ref<string[]>([]);
  const selectedItemGroups = ref<string[]>([]);
  const selectedProdTypes = ref<string[]>([]);

  // === Data State ===
  const summaryData: Ref<ReplanRtfSummary[]> = ref([]);
  const detailData: Ref<ReplanRtfDetail[]> = ref([]);
  const prodDetailData: Ref<ProdDetailResponse | null> = ref(null);
  const shortData: Ref<ShortData[]> = ref([]);
  const shortLoading = ref(false);
  const demandSummaryData: Ref<DemandSummaryData[]> = ref([]);
  const demandInfoData: Ref<any[]> = ref([]);
  const pegInfoData: Ref<any[]> = ref([]);
  const bomMapData: Ref<any[]> = ref([]);
  const bufferPlanTargetData: Ref<any[]> = ref([]);

  // === Freeze State ===
  const frozenStatus: Ref<FrozenStatus | null> = ref(null);

  // === UI State ===
  const loading = ref(false);
  const detailLoading = ref(false);
  const prodDetailLoading = ref(false);
  const isZoomedDetail = ref(false);
  const error = ref<string | null>(null);

  // === Widget Settings ===
  const widgetSettings = ref<any>(null);

  // === Computed ===

  const productionArea = computed<string | null>(() => {
    if (region.value === "default") return null;
    if (region.value === "HK") return hkDetail.value;
    return region.value; // e.g. "대구"
  });

  // === Snapshot commit ===

  function commitFilters() {
    committedSummaryType.value = summaryType.value;
    committedAggType.value = aggType.value;
    committedUomType.value = uomType.value;
    committedProdStatus.value = prodStatus.value;
    committedCustomers.value = [...selectedCustomers.value];
    committedItemGroups.value = [...selectedItemGroups.value];
    committedProdTypes.value = [...selectedProdTypes.value];
  }

  // === Load Methods ===

  async function loadFilters(planVer: string) {
    try {
      const results = await Promise.all([
        fetchFilterCustomers(planVer),
        fetchFilterItemGroups(planVer),
        fetchProdTypes(planVer),
      ]);

      const [custRes, itemGroupRes, prodTypeRes] = results;

      if (custRes.success) {
        customerSource.value = custRes.data.filter((c: any) => c.cust_id != null);
        selectedCustomers.value = customerSource.value.map((c: any) => c.cust_id);
      }
      if (itemGroupRes.success) {
        itemGroupSource.value = itemGroupRes.data.filter((g: any) => g.item_group != null);
        selectedItemGroups.value = itemGroupSource.value.map((g: any) => g.item_group);
      }
      if (prodTypeRes.success) {
        prodTypeSource.value = prodTypeRes.data.filter((p: any) => p.value != null);
        selectedProdTypes.value = prodTypeSource.value.map((p: any) => p.value);
      }
    } catch (e) {
      console.error("필터 데이터 로드 오류:", e);
    }
  }

  async function loadSummary(planVer: string) {
    loading.value = true;
    error.value = null;
    try {
      const params: ReplanSummaryParams = {
        planVer,
        aggregateType: committedAggType.value,
        summary: committedSummaryType.value,
        prodStatus: committedProdStatus.value === "default" ? null : committedProdStatus.value,
        uomType: committedUomType.value,
        productionArea: productionArea.value,
      };

      // Attach filter arrays based on summary type
      if (committedSummaryType.value === "cust") {
        params.customers = committedCustomers.value;
      } else if (committedSummaryType.value === "itemGroup") {
        params.itemGroupIDs = committedItemGroups.value;
      } else if (committedSummaryType.value === "prodType") {
        params.prodTypes = committedProdTypes.value;
      }

      const res = await fetchSummary(params);
      if (res.success) {
        summaryData.value = res.data;
      } else {
        error.value = res.error || res.message || "요약 데이터 조회 실패";
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : "알 수 없는 오류";
      console.error("요약 데이터 조회 오류:", e);
    } finally {
      loading.value = false;
    }
  }

  async function loadDetail(planVer: string, item: any) {
    detailLoading.value = true;
    selectedSummaryItem.value = item;

    try {
      const params: ReplanDetailParams = {
        planVer,
        aggregateType: committedAggType.value,
        summary: committedSummaryType.value,
        prodStatus: committedProdStatus.value === "default" ? null : committedProdStatus.value,
        uomType: committedUomType.value,
        productionArea: productionArea.value,
      };

      // Due period
      if (item.due !== "[TOTAL]" && item.due !== "[SUB TOTAL]") {
        if (committedAggType.value === "MONTH") params.dueMonth = item.due;
        if (committedAggType.value === "WEEK") params.dueWeek = item.due;
      }

      // Filter group
      if (committedSummaryType.value === "cust") {
        params.customers = item.custID === "[TOTAL]" ? committedCustomers.value : [item.custID];
      } else if (committedSummaryType.value === "itemGroup") {
        params.itemGroupIDs = item.itemGroupID === "[TOTAL]" ? committedItemGroups.value : [item.itemGroupID];
      } else if (committedSummaryType.value === "prodType") {
        params.prodTypes = item.prodType === "[TOTAL]" ? committedProdTypes.value : [item.prodType];
      }

      const res = await fetchDetail(params);
      if (res.success) {
        detailData.value = res.data;
        if (res.data.length > 0) {
          selectedDemandID.value = res.data[0].demandID;
        }
      }
    } catch (e) {
      console.error("상세 데이터 조회 오류:", e);
    } finally {
      detailLoading.value = false;
    }
  }

  async function loadProdDetail(planVer: string, demandID: string) {
    prodDetailLoading.value = true;
    try {
      const res = await fetchProdDetail({
        planVer,
        demandID,
        uomType: committedUomType.value,
      });
      if (res.success) {
        prodDetailData.value = res.data;
      }
    } catch (e) {
      console.error("생산 상세 조회 오류:", e);
    } finally {
      prodDetailLoading.value = false;
    }
  }

  async function loadShort(planVer: string, demandID: string) {
    shortLoading.value = true;
    try {
      const res = await fetchShort({ planVer, demandID, uomType: committedUomType.value });
      if (res.success) shortData.value = res.data;
    } catch (e) {
      console.error("Short 사유 조회 오류:", e);
    } finally {
      shortLoading.value = false;
    }
  }

  async function loadDemandSummary(planVer: string, demandIDs: string[]) {
    try {
      const res = await fetchDemandSummary({ planVer, demandIDs, uomType: committedUomType.value });
      if (res.success) demandSummaryData.value = res.data;
    } catch (e) {
      console.error("수요 요약 조회 오류:", e);
    }
  }

  async function loadDemandInfo(planVer: string, demandID: string) {
    try {
      const res = await fetchDemandInfo({ planVer, demandID });
      if (res.success) demandInfoData.value = res.data;
    } catch (e) {
      console.error("수요 정보 조회 오류:", e);
    }
  }

  async function loadPegInfo(planVer: string, demandID: string) {
    try {
      const res = await fetchPegInfo({ planVer, demandID });
      if (res.success) pegInfoData.value = res.data;
    } catch (e) {
      console.error("Peg 정보 조회 오류:", e);
    }
  }

  async function loadBomMap(planVer: string, demandID: string) {
    try {
      const res = await fetchBomMap({ planVer, demandID, onlyTargetBom: true, uomType: committedUomType.value });
      if (res.success) bomMapData.value = res.data;
    } catch (e) {
      console.error("BOM 구조 조회 오류:", e);
    }
  }

  async function loadBufferPlanTarget(planVer: string, demandID: string) {
    try {
      const res = await fetchBufferPlanTarget({ planVer, demandID });
      if (res.success) bufferPlanTargetData.value = res.data;
    } catch (e) {
      console.error("버퍼 계획 조회 오류:", e);
    }
  }

  // === Freeze Methods ===

  async function loadFrozenStatus(planCycleID: string) {
    try {
      const res = await fetchFrozenStatus(planCycleID);
      if (res.success && res.data?.length > 0) {
        frozenStatus.value = res.data[0];
      } else {
        frozenStatus.value = null;
      }
    } catch (e) {
      console.error("Frozen 상태 조회 오류:", e);
      frozenStatus.value = null;
    }
  }

  async function executeFreezeAction(
    planCycleID: string,
    planVer: string,
    createUser: string,
    description: string,
  ) {
    try {
      const res = await executeFreeze({ planCycleID, planVer, createUser, description });
      if (res.success) {
        await loadFrozenStatus(planCycleID);
        return true;
      }
      return false;
    } catch (e) {
      console.error("계획 확정 실행 오류:", e);
      return false;
    }
  }

  async function cancelFreezeAction(
    planCycleID: string,
    planVer: string,
    createUser: string,
  ) {
    try {
      const res = await cancelFreeze({ planCycleID, planVer, createUser });
      if (res.success) {
        await loadFrozenStatus(planCycleID);
        return true;
      }
      return false;
    } catch (e) {
      console.error("확정 취소 오류:", e);
      return false;
    }
  }

  async function updateFrozenDescription(planCycleID: string, description: string) {
    try {
      const res = await updateFrozenDesc({ planCycleID, description });
      return res.success;
    } catch (e) {
      console.error("확정 설명 수정 오류:", e);
      return false;
    }
  }

  // === Widget Settings ===

  async function loadWidgetSettings(userId: string) {
    try {
      const res = await fetchWidgetSettings(userId, "/pa/OnTimeRescheduledPlanResult");
      if (res.success) {
        widgetSettings.value = res.data;
      }
    } catch (e) {
      console.error("위젯 설정 로드 오류:", e);
    }
  }

  // === Reset ===

  function reset() {
    summaryData.value = [];
    detailData.value = [];
    prodDetailData.value = null;
    shortData.value = [];
    demandSummaryData.value = [];
    demandInfoData.value = [];
    pegInfoData.value = [];
    bomMapData.value = [];
    bufferPlanTargetData.value = [];
    selectedDemandID.value = "";
    selectedSummaryItem.value = null;
    error.value = null;
  }

  return {
    // Filter state (UI binding)
    summaryType,
    aggType,
    uomType,
    prodStatus,
    region,
    hkDetail,
    selectedCustomers,
    selectedItemGroups,
    selectedProdTypes,

    // Committed snapshot
    committedSummaryType,
    committedAggType,
    committedUomType,
    committedProdStatus,

    // Filter sources
    prodTypeSource,
    customerSource,
    itemGroupSource,

    // Data state
    summaryData,
    detailData,
    prodDetailData,
    shortData,
    shortLoading,
    demandSummaryData,
    demandInfoData,
    pegInfoData,
    bomMapData,
    bufferPlanTargetData,

    // Selection state
    selectedDemandID,
    selectedSummaryItem,

    // Freeze state
    frozenStatus,

    // UI state
    loading,
    detailLoading,
    prodDetailLoading,
    isZoomedDetail,
    error,

    // Widget settings
    widgetSettings,

    // Computed
    productionArea,

    // Methods
    commitFilters,
    loadFilters,
    loadSummary,
    loadDetail,
    loadProdDetail,
    loadShort,
    loadDemandSummary,
    loadDemandInfo,
    loadPegInfo,
    loadBomMap,
    loadBufferPlanTarget,
    loadFrozenStatus,
    executeFreezeAction,
    cancelFreezeAction,
    updateFrozenDescription,
    loadWidgetSettings,
    reset,
  };
}
