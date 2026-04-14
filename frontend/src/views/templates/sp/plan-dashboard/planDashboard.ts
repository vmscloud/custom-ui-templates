/**
 * Plan Dashboard API 호출 및 데이터 관리
 */
import { api, getProjectId } from "@/api/client";
import { ref, computed, type Ref } from "vue";

// ===== Utils =====

/**
 * 비율 배열을 소수점 2자리로 반올림하고, 총합이 100이 되도록 보정
 * 가장 큰 값에서 잔차를 보정한다.
 */
export function normalizeRatios(values: number[]): number[] {
  const rounded = values.map((v) => Math.round(v * 100) / 100);
  const sum = rounded.reduce((a, b) => a + b, 0);
  const diff = Math.round((100 - sum) * 100) / 100;
  if (diff !== 0 && rounded.length > 0) {
    // 가장 큰 값에 잔차 보정
    let maxIdx = 0;
    for (let i = 1; i < rounded.length; i++) {
      if (rounded[i] > rounded[maxIdx]) maxIdx = i;
    }
    rounded[maxIdx] = Math.round((rounded[maxIdx] + diff) * 100) / 100;
  }
  return rounded;
}

/** 단일 값 소수점 2자리 반올림 */
export function round2(v: number): number {
  return Math.round(v * 100) / 100;
}

// ===== Types =====

/** 공통 API 응답 */
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

/** RTF 요약 — frozen / actual / plan 공통 구조 */
export interface RTFSummary {
  demandQty: number;
  earlyQty: number;
  earlyRatio: number;
  ontimeQty: number;
  ontimeRatio: number;
  lateQty: number;
  lateRatio: number;
  shortQty: number;
  shortRatio: number;
  rtfQty: number;
  rtfRatio: number;
  upcomingQty: number;
  upcomingRatio: number;
  qtyUom: string;
  uomType: string;
}

/** Oper Group 가동률 데이터 */
export interface OperGroupCapaRow {
  [key: string]: any;
}

/** Res Group 보고서 행 */
export interface ResGroupReportRow {
  [key: string]: any;
}

/** 생산 보고서 요약 행 */
export interface ProdReportSummaryRow {
  [key: string]: any;
}

/** 생산 보고서 상세 행 */
export interface ProdReportDetailRow {
  [key: string]: any;
}

/** 표준 요약 보고서 행 */
export interface StdSummaryReportRow {
  [key: string]: any;
}

/** 오류 로그 요약 행 */
export interface ErrorLogSummaryRow {
  [key: string]: any;
}

/** Short 로그 요약 행 */
export interface ShortLogSummaryRow {
  [key: string]: any;
}

/** Pegging 보고서 요약 행 */
export interface PeggingReportSummaryRow {
  [key: string]: any;
}

/** Pegging 보고서 사유 행 */
export interface PeggingReportReasonRow {
  [key: string]: any;
}

/** OTD Summary 응답 */
export interface OTDSummary {
  qtyUom: string;
  uomType: string;
  periodType: string;
  frozenVer: string;
  frozenQty: number;
  planQty: number;
  actQty: number;
  list: OTDSummaryRow[];
}

/** OTD Summary 행 */
export interface OTDSummaryRow {
  category: string;
  type: string; // "FROZEN" | "PLAN" | "ACT"
  total_qty: number;
  origin_total_qty: number;
  current_due_bucket_prod_qty: number;
  previous_due_bucket_prod_qty: number;
  next_due_bucket_prod_qty: number;
  after_next_due_bucket_prod_qty: number;
  [key: string]: any;
}

/** /dashboard 응답 data 페이로드 */
export interface DashboardData {
  frozenVer: string;
  rtfSummary: {
    frozen: RTFSummary;
    actual: RTFSummary;
    plan: RTFSummary;
  };
  operGroupCapa: OperGroupCapaRow[];
  resGroupReport: ResGroupReportRow[];
  prodReport: {
    summary: ProdReportSummaryRow[];
    detail: ProdReportDetailRow[];
  };
  otdSummary: OTDSummary;
  stdSummaryReport: StdSummaryReportRow[];
  errorLogSummary: ErrorLogSummaryRow[];
  shortLogSummary: ShortLogSummaryRow[];
  peggingReport: {
    summary: PeggingReportSummaryRow[];
    reasons: PeggingReportReasonRow[];
  };
}

/** 위젯 설정 단건 */
export interface WidgetSetting {
  userId: string;
  menuId: string;
  widgetId: string;
  widgetValue: string;
  [key: string]: any;
}

// ===== 요청 파라미터 타입 =====

export interface DashboardParams {
  planVer: string;
  region: string;
  detailRegion: string;
  aggregateType: string;
  userId: string;
  menuId: string;
  regions?: string[];
  productionArea?: string;
}

export interface RtfDetailParams {
  planVer: string;
  region?: string;
  detailRegion?: string;
  aggregateType?: string;
  [key: string]: any;
}

export interface ResGroupParams {
  planVer: string;
  resGroupIDs: string[];
  weekPeriod: number;
  [key: string]: any;
}

export interface ProdReportParams {
  planVer: string;
  [key: string]: any;
}

export interface SettingsSaveParams {
  userId: string;
  menuId: string;
  widgetId: string;
  widgetValue: string;
}

// ===== 응답 타입 별칭 =====

export type DashboardResponse = ApiResponse<DashboardData>;
export type SettingsResponse = ApiResponse<WidgetSetting[]>;

// ===== API Functions =====

const BASE_URL = () =>
  `/api/custom/backend/${getProjectId()}/plan-dashboard`;

export const fetchDashboard = (params: DashboardParams) =>
  api.post<DashboardResponse>(`${BASE_URL()}/dashboard`, params);

export const fetchRtfDetail = (params: RtfDetailParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/rtf-detail`, params);

export const fetchOtdSummary = (params: { planVer: string; dataType?: string; productionArea?: string; otdType?: string }) =>
  api.post<ApiResponse>(`${BASE_URL()}/otd-summary`, params);

export const fetchResGroupReport = (params: ResGroupParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/res-group-report`, params);

export const fetchProdReport = (params: ProdReportParams) =>
  api.post<ApiResponse>(`${BASE_URL()}/prod-report`, params);

export const fetchSettings = (userId: string, menuId?: string) =>
  api.get<SettingsResponse>(`${BASE_URL()}/settings`, {
    params: { userId, menuId: menuId || "/pa/PlanDashboard" },
  });

export const saveSettings = (params: SettingsSaveParams) =>
  api.put<ApiResponse>(`${BASE_URL()}/settings`, params);

export const fetchFrozenVer = (planVer: string) =>
  api.get<ApiResponse<{ frozenVer: string }>>(`${BASE_URL()}/frozen-ver`, {
    params: { planVer },
  });

// ===== Composable =====

export function usePlanDashboard() {
  // === 필터 상태 ===
  const region = ref<string>("RTF_대구");
  const detailRegion = ref<string>("전체");
  const aggregateType = ref<string>("MONTH");

  // === 사용자 ID ===
  const userId = ref<string>("");

  // === region → API 파라미터 변환 ===
  const regionParams = computed(() => {
    if (region.value === "RTF") return [];
    return [region.value.replace("RTF_", "")];
  });

  const productionArea = computed(() => {
    switch (region.value) {
      case "RTF": return "";
      case "RTF_대구": return "대구";
      case "RTF_HK": {
        switch (detailRegion.value) {
          case "전체": return "HK";
          case "HK 완제": return "HK 완제";
          case "HK 반제": return "HK 반제";
          default: return "";
        }
      }
      case "RTF_APEX": return "APEX";
      default: return "";
    }
  });

  // === 대시보드 데이터 ===
  const dashboardData: Ref<DashboardData | null> = ref(null);
  const frozenVer = ref<string>("");

  // === 위젯 설정 ===
  const widgetSettings: Ref<Record<string, string>> = ref({});

  // === UI 상태 ===
  const loading = ref(false);
  const error = ref<string | null>(null);

  // === 대시보드 전체 조회 ===

  async function loadDashboard(planVer: string, uid?: string) {
    const resolvedUserId = uid || userId.value;
    loading.value = true;
    error.value = null;
    try {
      const res = await fetchDashboard({
        planVer,
        region: region.value,
        detailRegion: detailRegion.value,
        aggregateType: aggregateType.value,
        userId: resolvedUserId,
        menuId: "/pa/PlanDashboard",
        regions: regionParams.value,
        productionArea: productionArea.value,
      });
      if (res.success) {
        dashboardData.value = res.data;
        frozenVer.value = res.data.frozenVer;
      } else {
        error.value = res.error || res.message || "대시보드 조회 실패";
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : "알 수 없는 오류";
      console.error("대시보드 조회 오류:", e);
    } finally {
      loading.value = false;
    }
  }

  // === 위젯 설정 로드 ===

  async function loadSettings(uid?: string) {
    const resolvedUserId = uid || userId.value;
    try {
      const res = await fetchSettings(resolvedUserId);
      if (res.success && Array.isArray(res.data)) {
        const map: Record<string, string> = {};
        for (const item of res.data) {
          map[item.widgetId] = item.widgetValue;
        }
        widgetSettings.value = map;
      }
    } catch (e) {
      console.error("위젯 설정 로드 오류:", e);
    }
  }

  // === 위젯 설정 저장 ===

  async function saveSetting(uid: string, widgetId: string, widgetValue: string) {
    try {
      const res = await saveSettings({
        userId: uid,
        menuId: "/pa/PlanDashboard",
        widgetId,
        widgetValue,
      });
      if (res.success) {
        widgetSettings.value = { ...widgetSettings.value, [widgetId]: widgetValue };
      } else {
        console.error("위젯 설정 저장 실패:", res.error || res.message);
      }
    } catch (e) {
      console.error("위젯 설정 저장 오류:", e);
    }
  }

  // === 개별 패널 새로고침 ===

  async function refreshResGroup(planVer: string, resGroupIDs: string[], weekPeriod: number) {
    try {
      const res = await fetchResGroupReport({ planVer, resGroupIDs, weekPeriod });
      if (res.success && dashboardData.value) {
        dashboardData.value = {
          ...dashboardData.value,
          resGroupReport: res.data,
        };
      }
    } catch (e) {
      console.error("Res Group 새로고침 오류:", e);
    }
  }

  async function refreshProdReport(planVer: string) {
    try {
      const res = await fetchProdReport({ planVer });
      if (res.success && dashboardData.value) {
        dashboardData.value = {
          ...dashboardData.value,
          prodReport: res.data,
        };
      }
    } catch (e) {
      console.error("생산 보고서 새로고침 오류:", e);
    }
  }

  async function refreshOtdSummary(planVer: string, dataType: string = "ITEMGROUP", otdType: string = "ACT") {
    try {
      const res = await fetchOtdSummary({
        planVer,
        dataType,
        productionArea: productionArea.value,
        otdType,
      });
      if (res.success && dashboardData.value) {
        const key = otdType === "PLAN" ? "otdSummaryPlan" : "otdSummaryAct";
        dashboardData.value = {
          ...dashboardData.value,
          [key]: res.data,
        };
      }
    } catch (e) {
      console.error("OTD Summary 새로고침 오류:", e);
    }
  }

  // === 상태 초기화 ===

  function reset() {
    dashboardData.value = null;
    frozenVer.value = "";
    widgetSettings.value = {};
    error.value = null;
  }

  return {
    // 필터 상태
    region,
    detailRegion,
    aggregateType,

    // 사용자 ID
    userId,

    // 데이터 상태
    dashboardData,
    frozenVer,
    widgetSettings,

    // UI 상태
    loading,
    error,

    // 메서드
    loadDashboard,
    loadSettings,
    saveSetting,
    refreshOtdSummary,
    refreshResGroup,
    refreshProdReport,
    reset,
  };
}
