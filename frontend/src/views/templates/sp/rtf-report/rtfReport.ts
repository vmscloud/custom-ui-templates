/**
 * RTF Report API 호출 및 데이터 관리
 */
import { api, getProjectId } from "@/api/client";
import { ref, type Ref } from "vue";

// ===== Types =====

/** 공통 API 응답 */
export interface ApiResponse<T = any> {
  success: boolean;
  count: number;
  data: T[];
  message?: string;
  error?: string;
}

/** RTF 요약 그리드 데이터 */
export interface RtfSummaryData {
  due: string;
  custID: string;
  itemGroupID: string;
  region: string;
  demandType: string;
  demandCnt: number;
  demandQty: number;
  rtfQty: number;
  qtyUom: string;
  onTimeRatio: number;
  onTimeQty: number;
  lateRatio: number;
  lateQty: number;
  rtfRatio: number;
  group_name?: string;
  [key: string]: any;
}

/** RTF 상세 그리드 데이터 */
export interface RtfDetailData {
  demandID: string;
  custID: string;
  onTimeRatio: number;
  lateRatio: number;
  rtfRatio: number;
  _short_detail: string;
  itemGroupID: string;
  itemID: string;
  itemName: string;
  dueWeek: string;
  dueDate: string;
  demandQty: number;
  onTimeQty: number;
  lateQty: number;
  rtfQty: number;
  shortQty: number;
  qtyUom: string;
  demand_type: string;
  item_type: string;
  prod_type: string;
  item_size_type: string;
  item_spec: string;
  [key: string]: any;
}

/** Short(부족) 사유 데이터 */
export interface RtfShortData {
  short_type: string;
  short_category: string;
  short_reason: string;
  short_qty: number;
  qty_uom: string;
  [key: string]: any;
}

/** 생산계획 피벗 데이터 */
export interface RtfProdDetailData {
  item_id: string;
  buffer_seq: number;
  buffer_id: string;
  oper_group_id: string;
  oper_id: string;
  site_id: string;
  item_type: string;
  wip_qty: number;
  peg_qty: number;
  used_total_qty: number;
  out_plan_qty: number;
  plan_date: string;
  plan_month: string;
  [key: string]: any;
}

/** 수요 요약 메트릭 */
export interface RtfDemandSummaryData {
  demand_qty: number;
  shipment_qty: number;
  wip_qty: number;
  peg_qty: number;
  peg_ratio: number;
  warehousing_date: string;
  shipment_date: string;
  [key: string]: any;
}

/** 필터 옵션 아이템 */
export interface FilterOption {
  value: string;
  label?: string;
  [key: string]: any;
}

/** 속성 컬럼 정의 */
export interface PropColumn {
  columnName: string;
  displayText: string;
  category: string | null;
}

// ===== 요청 파라미터 타입 =====

export interface RtfSummaryParams {
  planVer: string;
  aggregateType: string;
  summary: string;
  customers: string[];
  itemGroupIDs: string[];
  regions: string[];
  demandTypes: string[];
  prodStatus: string;
  uomType: string;
}

export interface RtfDetailParams {
  planVer: string;
  aggregateType: string;
  summary: string;
  groupKey?: string;
  dueMonth?: string;
  dueWeek?: string;
  customers: string[];
  itemGroupIDs: string[];
  regions: string[];
  demandTypes: string[];
  prodStatus: string;
  uomType: string;
}

export interface RtfDemandParams {
  planVer: string;
  demandID: string;
  uomType?: string;
}

export interface RtfBomMapParams {
  planVer: string;
  demandID: string;
  onlyTargetBom?: boolean;
  uomType?: string;
}

export interface RtfItemPropsParams {
  planVer: string;
  itemID: string;
}

// ===== API Functions =====

const BASE_URL = () =>
  `/api/custom/backend/${getProjectId()}/rtf-report`;

// --- 핵심 데이터 API ---

export const fetchSummary = (params: RtfSummaryParams) =>
  api.post<ApiResponse<RtfSummaryData>>(`${BASE_URL()}/summary`, params);

export const fetchDetail = (params: RtfDetailParams) =>
  api.post<ApiResponse<RtfDetailData>>(`${BASE_URL()}/detail`, params);

export const fetchShort = (params: RtfDemandParams) =>
  api.post<ApiResponse<RtfShortData>>(`${BASE_URL()}/short`, params);

export const fetchProdDetail = (params: RtfDemandParams) =>
  api.post<ApiResponse<RtfProdDetailData>>(`${BASE_URL()}/prod-detail`, params);

export const fetchBufferPlanTarget = (params: { planVer: string; demandID: string }) =>
  api.post<ApiResponse>(`${BASE_URL()}/buffer-plan-target`, params);

export const fetchDemandSummary = (params: { planVer: string; demandIDs: string[]; uomType?: string }) =>
  api.post<ApiResponse<RtfDemandSummaryData>>(`${BASE_URL()}/demand-summary`, params);

export const fetchDemandInfo = (params: RtfDemandParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/demand-info`, params);

export const fetchPegInfo = (params: RtfDemandParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/peg-info`, params);

export const fetchBomMap = (params: RtfBomMapParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/bom-map`, params);

export const fetchItemProps = (params: RtfItemPropsParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/item-props`, params);

export const fetchDemandRecord = (params: RtfDemandParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/demand-record`, params);

// --- 필터 API ---

export const fetchFilterCustomers = (planVer: string) =>
  api.get<ApiResponse<FilterOption>>(`${BASE_URL()}/filters/customers`, {
    params: { plan_ver: planVer },
  });

export const fetchFilterItemGroups = (planVer: string) =>
  api.get<ApiResponse<FilterOption>>(`${BASE_URL()}/filters/item-groups`, {
    params: { plan_ver: planVer },
  });

export const fetchFilterRegions = (planVer: string) =>
  api.get<ApiResponse<FilterOption>>(`${BASE_URL()}/filters/regions`, {
    params: { plan_ver: planVer },
  });

export const fetchFilterDemandTypes = (planVer: string) =>
  api.get<ApiResponse<FilterOption>>(`${BASE_URL()}/filters/demand-types`, {
    params: { plan_ver: planVer },
  });

export const fetchFilterPropColumns = (planVer: string) =>
  api.get<ApiResponse<PropColumn>>(`${BASE_URL()}/filters/prop-columns`, {
    params: { plan_ver: planVer },
  });

// ===== Composable =====

export function useRtfReport() {
  // === 필터 상태 (UI 바인딩용 — 사용자가 자유롭게 변경) ===
  const summaryType = ref<string>("itemGroup");
  const aggType = ref<string>("MONTH");
  const uomType = ref<string>("DEFAULT");
  const prodStatus = ref<string>("default");
  const selectedCustomers = ref<string[]>([]);
  const selectedItemGroups = ref<string[]>([]);
  const selectedRegions = ref<string[]>([]);
  const selectedDemandTypes = ref<string[]>([]);

  // === 확정(committed) 조회조건 스냅샷 — 조회 실행 시점에만 갱신 ===
  const committedSummaryType = ref<string>("itemGroup");
  const committedAggType = ref<string>("MONTH");
  const committedUomType = ref<string>("DEFAULT");
  const committedProdStatus = ref<string>("default");
  const committedCustomers = ref<string[]>([]);
  const committedItemGroups = ref<string[]>([]);
  const committedRegions = ref<string[]>([]);
  const committedDemandTypes = ref<string[]>([]);

  // === 필터 소스 ===
  const customerSource: Ref<any[]> = ref([]);
  const itemGroupSource: Ref<any[]> = ref([]);
  const regionSource: Ref<any[]> = ref([]);
  const demandTypeSource: Ref<any[]> = ref([]);
  const propColumns: Ref<PropColumn[]> = ref([]);

  // === 데이터 상태 ===
  const summaryData: Ref<RtfSummaryData[]> = ref([]);
  const detailData: Ref<RtfDetailData[]> = ref([]);
  const shortData: Ref<RtfShortData[]> = ref([]);
  const prodDetailData: Ref<RtfProdDetailData[]> = ref([]);
  const demandSummaryData: Ref<RtfDemandSummaryData[]> = ref([]);
  const demandInfoData: Ref<any[]> = ref([]);
  const pegInfoData: Ref<any[]> = ref([]);
  const bomMapData: Ref<any[]> = ref([]);
  const itemPropsData: Ref<any[]> = ref([]);
  const demandRecordData: Ref<any[]> = ref([]);
  const bufferPlanTargetData: Ref<any[]> = ref([]);

  // === 선택 상태 ===
  const selectedDemandID = ref<string>("");
  const selectedSummaryItem = ref<RtfSummaryData | null>(null);

  // === UI 상태 ===
  const loading = ref(false);
  const detailLoading = ref(false);
  const prodDetailLoading = ref(false);
  const error = ref<string | null>(null);

  // === 스냅샷 확정 ===

  function commitFilters() {
    committedSummaryType.value = summaryType.value;
    committedAggType.value = aggType.value;
    committedUomType.value = uomType.value;
    committedProdStatus.value = prodStatus.value;
    committedCustomers.value = [...selectedCustomers.value];
    committedItemGroups.value = [...selectedItemGroups.value];
    committedRegions.value = [...selectedRegions.value];
    committedDemandTypes.value = [...selectedDemandTypes.value];
  }

  // === 필터 로드 ===

  async function loadFilters(planVer: string) {
    try {
      const [custRes, itemGroupRes, regionRes, demandTypeRes, propRes] =
        await Promise.all([
          fetchFilterCustomers(planVer),
          fetchFilterItemGroups(planVer),
          fetchFilterRegions(planVer),
          fetchFilterDemandTypes(planVer),
          fetchFilterPropColumns(planVer),
        ]);

      if (custRes.success) {
        customerSource.value = custRes.data;
        selectedCustomers.value = custRes.data.map((c: any) => c.cust_id);
      }
      if (itemGroupRes.success) {
        itemGroupSource.value = itemGroupRes.data;
        selectedItemGroups.value = itemGroupRes.data.map((g: any) => g.item_group);
      }
      if (regionRes.success) {
        regionSource.value = regionRes.data;
        selectedRegions.value = regionRes.data.map((r: any) => r.value);
      }
      if (demandTypeRes.success) {
        demandTypeSource.value = demandTypeRes.data;
        selectedDemandTypes.value = demandTypeRes.data.map((d: any) => d.value);
      }
      if (propRes.success) propColumns.value = propRes.data;
    } catch (e) {
      console.error("필터 데이터 로드 오류:", e);
    }
  }

  // === 핵심 데이터 로드 ===

  async function loadSummary(planVer: string) {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetchSummary({
        planVer,
        aggregateType: committedAggType.value,
        summary: committedSummaryType.value,
        customers: committedCustomers.value,
        itemGroupIDs: committedItemGroups.value,
        regions: committedRegions.value,
        demandTypes: committedDemandTypes.value,
        prodStatus: committedProdStatus.value,
        uomType: committedUomType.value,
      });
      if (res.success) {
        // group_name 필드 추가 (Summary 그리드 그룹핑용)
        const groupField: Record<string, string> = {
          itemGroup: "itemGroupID",
          cust: "custID",
          region: "region",
          demandType: "demandType",
        };
        const gf = groupField[committedSummaryType.value] || "itemGroupID";
        summaryData.value = res.data.map((r: any) => ({
          ...r,
          group_name: r[gf] ?? "",
        }));
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

  async function loadDetail(planVer: string, item: RtfSummaryData) {
    detailLoading.value = true;
    selectedSummaryItem.value = item;

    // 요약 유형에 따라 그룹 키 결정
    const groupKeyMap: Record<string, string> = {
      itemGroup: (item as any).itemGroupID,
      cust: (item as any).custID,
      region: (item as any).region,
      demandType: (item as any).demandType,
      due: (item as any).due,
    };
    const groupKey = groupKeyMap[committedSummaryType.value] || "";

    try {
      const res = await fetchDetail({
        planVer,
        aggregateType: committedAggType.value,
        summary: committedSummaryType.value,
        groupKey,
        dueMonth: committedAggType.value === "MONTH" && item.due !== "[SUB TOTAL]" && item.due !== "[TOTAL]" ? item.due : undefined,
        dueWeek: committedAggType.value === "WEEK" && item.due !== "[SUB TOTAL]" && item.due !== "[TOTAL]" ? item.due : undefined,
        customers: committedCustomers.value,
        itemGroupIDs: committedItemGroups.value,
        regions: committedRegions.value,
        demandTypes: committedDemandTypes.value,
        prodStatus: committedProdStatus.value,
        uomType: committedUomType.value,
      });
      if (res.success) {
        detailData.value = res.data;
        // 첫 번째 행의 demandID를 선택
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

  async function loadShort(planVer: string, demandID: string) {
    try {
      const res = await fetchShort({
        planVer,
        demandID,
        uomType: committedUomType.value,
      });
      if (res.success) shortData.value = res.data;
    } catch (e) {
      console.error("Short 사유 조회 오류:", e);
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
        // 백엔드가 { detail: [...], period: [...] } 구조로 반환
        prodDetailData.value = res.data?.detail ?? res.data ?? [];
      }
    } catch (e) {
      console.error("생산 상세 조회 오류:", e);
    } finally {
      prodDetailLoading.value = false;
    }
  }

  async function loadDemandSummary(planVer: string, demandIDs: string[]) {
    try {
      const res = await fetchDemandSummary({ planVer, demandIDs, uomType: uomType.value });
      if (res.success) demandSummaryData.value = res.data;
    } catch (e) {
      console.error("수요 요약 조회 오류:", e);
    }
  }

  async function loadDemandInfo(planVer: string, demandID: string) {
    try {
      const res = await fetchDemandInfo({ planVer, demandID, uomType: uomType.value });
      if (res.success) demandInfoData.value = res.data;
    } catch (e) {
      console.error("수요 정보 조회 오류:", e);
    }
  }

  async function loadPegInfo(planVer: string, demandID: string) {
    try {
      const res = await fetchPegInfo({ planVer, demandID, uomType: uomType.value });
      if (res.success) pegInfoData.value = res.data;
    } catch (e) {
      console.error("Peg 정보 조회 오류:", e);
    }
  }

  async function loadBomMap(
    planVer: string,
    demandID: string,
    onlyTargetBom = true,
  ) {
    try {
      const res = await fetchBomMap({
        planVer,
        demandID,
        onlyTargetBom,
        uomType: committedUomType.value,
      });
      if (res.success) bomMapData.value = res.data;
    } catch (e) {
      console.error("BOM 구조 조회 오류:", e);
    }
  }

  async function loadItemProps(planVer: string, itemID: string) {
    try {
      const res = await fetchItemProps({ planVer, itemID });
      if (res.success) itemPropsData.value = res.data;
    } catch (e) {
      console.error("품목 속성 조회 오류:", e);
    }
  }

  async function loadDemandRecord(planVer: string, demandID: string) {
    try {
      const res = await fetchDemandRecord({ planVer, demandID });
      if (res.success) demandRecordData.value = res.data;
    } catch (e) {
      console.error("수요 레코드 조회 오류:", e);
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

  // === 상태 초기화 ===

  function reset() {
    summaryData.value = [];
    detailData.value = [];
    shortData.value = [];
    prodDetailData.value = [];
    demandSummaryData.value = [];
    demandInfoData.value = [];
    pegInfoData.value = [];
    bomMapData.value = [];
    itemPropsData.value = [];
    demandRecordData.value = [];
    bufferPlanTargetData.value = [];
    selectedDemandID.value = "";
    selectedSummaryItem.value = null;
    error.value = null;
  }

  return {
    // 필터 상태 (UI 바인딩)
    summaryType,
    aggType,
    uomType,
    prodStatus,
    selectedCustomers,
    selectedItemGroups,
    selectedRegions,
    selectedDemandTypes,

    // 확정 조회조건 스냅샷 (그리드/데이터용)
    committedSummaryType,
    committedAggType,
    committedUomType,
    committedProdStatus,

    // 필터 소스
    customerSource,
    itemGroupSource,
    regionSource,
    demandTypeSource,
    propColumns,

    // 데이터 상태
    summaryData,
    detailData,
    shortData,
    prodDetailData,
    demandSummaryData,
    demandInfoData,
    pegInfoData,
    bomMapData,
    itemPropsData,
    demandRecordData,
    bufferPlanTargetData,

    // 선택 상태
    selectedDemandID,
    selectedSummaryItem,

    // UI 상태
    loading,
    detailLoading,
    prodDetailLoading,
    error,

    // 메서드
    commitFilters,
    loadFilters,
    loadSummary,
    loadDetail,
    loadShort,
    loadProdDetail,
    loadDemandSummary,
    loadDemandInfo,
    loadPegInfo,
    loadBomMap,
    loadItemProps,
    loadDemandRecord,
    loadBufferPlanTarget,
    reset,
  };
}
