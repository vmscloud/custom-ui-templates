/**
 * Demand Distribution API 호출 및 데이터 관리
 */
import { api, getProjectId } from "@/api/client";
import { ref, computed, type Ref, type ComputedRef } from "vue";

// ===== Types =====

/**
 * Demand Version 데이터 타입
 */
export interface DemandVersion {
  project_id: string;
  plan_cycle_id: string;
  demand_ver: string;
  demand_type: string | null;
  description: string | null;
  fix_datetime: string | null;
  create_datetime: string;
  create_user: string;
  update_datetime: string;
  update_user: string;
  display_text: string;
}

/**
 * Demand Distribution 헤더 타입
 */
export interface DemandDistributionHeader {
  columnName: string;
  displayText: string;
  category: string;
}

/**
 * Demand Distribution 데이터 타입
 */
export interface DemandDistributionData {
  item_id: string;
  item_name: string | null;
  cust_id: string | null;
  due_date: string;
  item_group_id: string | null;
  item_size_type: string | null;
  prod_type: string | null;
  qty: number;
  item_cnt: number;
  qty_uom: string | null;
  total?: number;
  prop01?: string;
  prop02?: string;
  prop03?: string;
  prop04?: string;
  prop05?: string;
  prop06?: string;
  prop07?: string;
  prop08?: string;
  prop09?: string;
  prop10?: string;
  [key: string]: string | number | null | undefined;
}

/**
 * Demand Version 응답 타입
 */
export interface DemandVersionResponse {
  success: boolean;
  count: number;
  data: DemandVersion[];
  message?: string;
  error?: string;
}

/**
 * Demand Distribution 응답 타입
 */
export interface DemandDistributionResponse {
  success: boolean;
  count: number;
  data: DemandDistributionData[];
  headers: DemandDistributionHeader[];
  message?: string;
  error?: string;
}

/**
 * 컬럼 메타데이터 응답 타입
 */
export interface ColumnMetadataResponse {
  success: boolean;
  count: number;
  data: DemandDistributionHeader[];
  error?: string;
}

/**
 * UOM Preference 응답 타입
 */
export interface UomPreferenceResponse {
  success: boolean;
  uomType: string;
  error?: string;
}

/**
 * Demand Distribution 조회 파라미터
 */
export interface DemandDistributionParams {
  demandVer: string;
  aggregateType: "WEEK" | "MONTH" | "YEAR";
  summary: "sum" | "count";
  uomType: string;
  columns: string[];
  showStack?: boolean;
}

// ===== API Functions =====

/**
 * Demand Version 목록 조회
 */
export async function fetchDemandVersions(
  projectId?: string,
): Promise<DemandVersionResponse> {
  return api.get<DemandVersionResponse>(
    `/api/custom/backend/${projectId ?? getProjectId()}/demand/demand-versions`,
  );
}

/**
 * Demand Distribution 데이터 조회
 */
export async function fetchDemandDistribution(
  params: DemandDistributionParams,
  projectId?: string,
): Promise<DemandDistributionResponse> {
  return api.post<DemandDistributionResponse>(
    `/api/custom/backend/${projectId ?? getProjectId()}/demand/demand-distribution`,
    params,
  );
}

/**
 * 컬럼 메타데이터 조회
 */
export async function fetchColumnMetadata(
  projectId?: string,
): Promise<ColumnMetadataResponse> {
  return api.get<ColumnMetadataResponse>(
    `/api/custom/backend/${projectId ?? getProjectId()}/demand/demand-distribution-columns`,
  );
}

/**
 * UOM Preference 조회
 */
export async function fetchUomPreference(
  userId: string,
  menuId?: string,
  projectId?: string,
): Promise<UomPreferenceResponse> {
  return api.get<UomPreferenceResponse>(
    `/api/custom/backend/${projectId ?? getProjectId()}/demand/uom-preference`,
    {
      params: {
        user_id: userId,
        menu_id: menuId,
      },
    },
  );
}

// ===== Composable =====

/**
 * Demand Distribution 컴포저블
 */
export function useDemandDistribution() {
  // State
  const data: Ref<DemandDistributionData[]> = ref([]);
  const headers: Ref<DemandDistributionHeader[]> = ref([]);
  const demandVersions: Ref<DemandVersion[]> = ref([]);
  const columnMetadata: Ref<DemandDistributionHeader[]> = ref([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const count = ref(0);

  // Filter state
  const selectedDemandVer = ref<string>("");
  const aggregateType = ref<"WEEK" | "MONTH" | "YEAR">("WEEK");
  const summary = ref<"sum" | "count">("sum");
  const uomType = ref<string>("DEFAULT");
  const selectedColumns = ref<string[]>([]);

  // Computed - dynamic columns for grid/chart
  const dynamicHeaders: ComputedRef<DemandDistributionHeader[]> = computed(() =>
    headers.value.filter((h) => h.category !== "fixed"),
  );

  const fixedHeaders: ComputedRef<DemandDistributionHeader[]> = computed(() =>
    headers.value.filter((h) => h.category === "fixed"),
  );

  // Methods

  /**
   * Demand Version 목록 조회
   */
  async function loadDemandVersions() {
    try {
      const response = await fetchDemandVersions();
      if (response.success) {
        demandVersions.value = response.data;
      }
    } catch (e) {
      console.error("Demand Version 조회 오류:", e);
    }
  }

  /**
   * 컬럼 메타데이터 조회
   */
  async function loadColumnMetadata() {
    try {
      const response = await fetchColumnMetadata();
      if (response.success) {
        columnMetadata.value = response.data;
      }
    } catch (e) {
      console.error("컬럼 메타데이터 조회 오류:", e);
    }
  }

  /**
   * UOM Preference 조회
   */
  async function loadUomPreference(
    userId: string,
    menuId?: string,
  ) {
    try {
      const response = await fetchUomPreference(userId, menuId);
      if (response.success) {
        uomType.value = response.uomType;
      }
    } catch (e) {
      console.error("UOM Preference 조회 오류:", e);
    }
  }

  /**
   * Demand Distribution 데이터 조회
   */
  async function loadData() {
    if (!selectedDemandVer.value) {
      error.value = "Demand Version을 선택해주세요.";
      return;
    }

    loading.value = true;
    error.value = null;

    try {
      const response = await fetchDemandDistribution({
        demandVer: selectedDemandVer.value,
        aggregateType: aggregateType.value,
        summary: summary.value,
        uomType: uomType.value,
        columns: selectedColumns.value,
      });

      if (response.success) {
        data.value = response.data;
        headers.value = response.headers;
        count.value = response.count;
      } else {
        error.value = response.error || "데이터 조회 실패";
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : "알 수 없는 오류";
      console.error("Demand Distribution 조회 오류:", e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * 상태 초기화
   */
  function reset() {
    data.value = [];
    headers.value = [];
    count.value = 0;
    error.value = null;
  }

  return {
    // State
    data,
    headers,
    demandVersions,
    columnMetadata,
    loading,
    error,
    count,

    // Filters
    selectedDemandVer,
    aggregateType,
    summary,
    uomType,
    selectedColumns,

    // Computed
    dynamicHeaders,
    fixedHeaders,

    // Methods
    loadDemandVersions,
    loadColumnMetadata,
    loadUomPreference,
    loadData,
    reset,
  };
}

// ===== Utility Functions =====

/**
 * 날짜를 포맷팅된 문자열로 변환
 */
export function displayDateToFormat(
  date: string | Date,
  aggregateType: "day" | "week" | "month",
): string {
  const d = typeof date === "string" ? new Date(date) : date;

  switch (aggregateType) {
    case "day":
      return d.toLocaleDateString("ko-KR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    case "week": {
      const weekNum = Math.ceil(
        ((d.getTime() - new Date(d.getFullYear(), 0, 1).getTime()) / 86400000 +
          1) /
          7,
      );
      return `${d.getFullYear()}W${String(weekNum).padStart(2, "0")}`;
    }
    case "month":
    default:
      return d.toLocaleDateString("ko-KR", { year: "numeric", month: "short" });
  }
}
