/**
 * Load Factor By Oper Group API & Composable
 *
 * 공정 그룹별 부하율 분석 페이지의 데이터 계층.
 */
import { api, getProjectId } from "@/api/client";
import { ref } from "vue";

// ===== API Base URL =====

const BASE_URL = () => `/api/custom/backend/${getProjectId()}/load-factor`;

// ===== Types =====

export interface OperGroup {
  oper_group_id: string;
  oper_group_name: string;
  oper_group_seq: number;
}

export interface LoadFactorMainParams {
  planVer: string;
  fromDate: string;
  toDate: string;
  operGroupIDs: string[];
  includeUndefinedCapa: boolean;
}

export interface LoadFactorGroupParams {
  planVer: string;
  fromDate: string;
  toDate: string;
  operGroupIDs: string[];
}

export interface LoadFactorDetailParams {
  planVer: string;
  fromDate: string;
  toDate: string;
  operGroupIDs: string[];
  includeUndefinedCapa: boolean;
}

export interface LoadFactorMainRow {
  oper_group_id: string;
  capa: number;
  plan_qty: number;
  str_rate: number;
  base_line: number;
}

export interface LoadFactorGroupRow {
  oper_group_id: string;
  item_group_id: string;
  date: string;
  plan_qty: number;
  capa: number;
  str_rate: number;
  base_line: number;
  sort_order: number;
}

export interface LoadFactorDetailRow {
  oper_group_id: string;
  str_date: string;
  capa: number;
  str_qty: number;
  outer_str_area: number;
  str_rate: number;
  item_id: string;
  item_group_id: string;
  demand_id: string;
  due_date: string;
  oper_id: string;
}

// ===== API Functions =====

export const fetchOperGroups = (planVer: string) =>
  api.get<{ success: boolean; data: OperGroup[] }>(`${BASE_URL()}/oper-groups?planVer=${planVer}`);

export const fetchMain = (params: LoadFactorMainParams) =>
  api.post<{ success: boolean; data: LoadFactorMainRow[] }>(`${BASE_URL()}/main`, params);

export const fetchGroup = (params: LoadFactorGroupParams) =>
  api.post<{ success: boolean; data: LoadFactorGroupRow[] }>(`${BASE_URL()}/group`, params);

export const fetchDetail = (params: LoadFactorDetailParams) =>
  api.post<{ success: boolean; data: LoadFactorDetailRow[] }>(`${BASE_URL()}/detail`, params);

// ===== Composable =====

export function useLoadFactorByOperGroup() {
  // Filter state
  const fromDate = ref<string>("");
  const toDate = ref<string>("");
  const includeUndefinedCapa = ref(true);
  const selectedOperGroups = ref<string[]>([]);
  const selectedOperGroupId = ref<string | null>(null);

  // Data sources
  const operGroupSource = ref<OperGroup[]>([]);
  const mainData = ref<LoadFactorMainRow[]>([]);
  const groupData = ref<LoadFactorGroupRow[]>([]);
  const detailData = ref<LoadFactorDetailRow[]>([]);

  // Loading states
  const loading = ref(false);
  const groupLoading = ref(false);
  const detailLoading = ref(false);

  // Committed filter state (frozen on search)
  const committedFromDate = ref("");
  const committedToDate = ref("");
  const committedIncludeUndefinedCapa = ref(true);

  function commitFilters() {
    committedFromDate.value = fromDate.value;
    committedToDate.value = toDate.value;
    committedIncludeUndefinedCapa.value = includeUndefinedCapa.value;
  }

  async function loadOperGroups(planVer: string) {
    try {
      const res = await fetchOperGroups(planVer);
      if (res.success) {
        operGroupSource.value = res.data;
        selectedOperGroups.value = res.data.map((g) => g.oper_group_id);
      }
    } catch (e) {
      console.error("공정그룹 목록 조회 오류:", e);
    }
  }

  async function loadMain(planVer: string) {
    loading.value = true;
    commitFilters();
    try {
      const res = await fetchMain({
        planVer,
        fromDate: committedFromDate.value,
        toDate: committedToDate.value,
        operGroupIDs: selectedOperGroups.value,
        includeUndefinedCapa: committedIncludeUndefinedCapa.value,
      });
      if (res.success) {
        mainData.value = res.data;
      }
    } catch (e) {
      console.error("부하율 요약 조회 오류:", e);
    } finally {
      loading.value = false;
    }
  }

  async function loadGroup(planVer: string, operGroupId: string) {
    groupLoading.value = true;
    selectedOperGroupId.value = operGroupId;
    try {
      const res = await fetchGroup({
        planVer,
        fromDate: committedFromDate.value,
        toDate: committedToDate.value,
        operGroupIDs: [operGroupId],
      });
      if (res.success) {
        groupData.value = res.data;
      }
    } catch (e) {
      console.error("일별 부하 조회 오류:", e);
    } finally {
      groupLoading.value = false;
    }
  }

  async function loadDetail(planVer: string, operGroupId: string) {
    detailLoading.value = true;
    try {
      const res = await fetchDetail({
        planVer,
        fromDate: committedFromDate.value,
        toDate: committedToDate.value,
        operGroupIDs: [operGroupId],
        includeUndefinedCapa: committedIncludeUndefinedCapa.value,
      });
      if (res.success) {
        detailData.value = res.data;
      }
    } catch (e) {
      console.error("부하 상세 조회 오류:", e);
    } finally {
      detailLoading.value = false;
    }
  }

  function reset() {
    mainData.value = [];
    groupData.value = [];
    detailData.value = [];
    selectedOperGroupId.value = null;
  }

  return {
    // Filters
    fromDate,
    toDate,
    includeUndefinedCapa,
    selectedOperGroups,
    selectedOperGroupId,
    // Data
    operGroupSource,
    mainData,
    groupData,
    detailData,
    // Loading
    loading,
    groupLoading,
    detailLoading,
    // Methods
    loadOperGroups,
    loadMain,
    loadGroup,
    loadDetail,
    commitFilters,
    reset,
  };
}
