/**
 * Store/API 어댑터 레이어
 *
 * 스토어: hostData inject + 백엔드 API로 부족한 데이터 보충
 * API: 프록시 대상(BomMap 등)만 APS 백엔드, 나머지 전부 커스텀 백엔드
 */
import { api, getProjectId } from "@/api/client";
import { useHostData } from "@/composables/useHostStores";
import { computed, effectScope, reactive, ref, watch } from "vue";
import dayjs from "dayjs";

// ── Base URLs ──
const CUSTOM_BASE = () => `/api/custom/backend/${getProjectId()}`;
const APS_BASE = () => `/api/aps/backend/${getProjectId()}`;

// ── APS 프록시 대상 (이 목록만 APS 백엔드로, 나머지 전부 커스텀 백엔드) ──
const PROXY_ROUTES = [
  "RarBomMapViewNew",  // BomMap API 전체
  "downloadBigData",   // 엑셀 대량 다운로드
  "PlmPlanExecute",    // Freeze Plan (제외 범위)
  "PlmSysOperPlan",    // Frozen Period (제외 범위)
];

// ── 커스텀 백엔드 오버라이드 (PROXY_ROUTES보다 우선) ──
const CUSTOM_OVERRIDE_ROUTES = [
  "RarBomMapViewNew/GetBomMapIsbInfo",  // ISB 상세 정보 (Trino 직접 구현)
];

// ══════════════════════════════════════════════════════════
// API Functions
// ══════════════════════════════════════════════════════════

/**
 * apiCall — 원본 APS의 apiCall 대체
 * PROXY_ROUTES에 해당하면 APS 프록시, 나머지 전부 커스텀 백엔드
 */
export async function apiCall(options: {
  url: string;
  param?: any;
  method?: string;
}): Promise<any> {
  const { url, param } = options;

  // 커스텀 백엔드 오버라이드 확인 (PROXY_ROUTES보다 우선)
  const isCustomOverride = CUSTOM_OVERRIDE_ROUTES.some((r) => url === r || url.startsWith(r + "/"));

  // APS 프록시 대상 → nginx가 dev.mozart-cloud.com으로 직접 프록시 (브라우저 쿠키 전달)
  // 원본 C# 컨트롤러의 HTTP method를 그대로 전달해야 함
  if (!isCustomOverride && PROXY_ROUTES.some((r) => url.startsWith(r))) {
    const fullUrl = `${APS_BASE()}/${url}`;
    const method = (options.method || "POST").toUpperCase();

    if (method === "GET") {
      return api.get(fullUrl, { params: param });
    } else if (method === "PUT") {
      return api.put(fullUrl, param);
    } else if (method === "DELETE") {
      return api.delete(fullUrl, { data: param });
    }
    return api.post(fullUrl, param);
  }

  // 나머지 전부 → 커스텀 백엔드 Trino SQL
  // URL 경로에 API 이름을 포함시켜 네트워크 탭에서 식별 가능하게 함
  const customUrl = `${CUSTOM_BASE()}/rtf-report/${url}`;
  if (Array.isArray(param)) {
    return api.post(customUrl, { _rows: param });
  }
  return api.post(customUrl, param);
}

/**
 * autoTransaction — 원본과 동일 (apiCall 위임)
 */
export async function autoTransaction(options: {
  url: string;
  param?: any;
  method?: string;
}) {
  return apiCall(options);
}

/**
 * downloadBigData — 대용량 엑셀 다운로드 (프록시 경유)
 */
export async function downloadBigData(options: {
  column_map: any;
  file_name: string;
  data_method: string;
  data_parameter: string;
  api_key: string;
}) {
  return api.post(`${APS_BASE()}/downloadBigData`, options);
}

// ══════════════════════════════════════════════════════════
// Store Adapters
// ══════════════════════════════════════════════════════════

/**
 * usePlanCycleStore — 원본 APS의 usePlanCycleStore 대체
 *
 * Host hostData에서 planVer/fromDate/toDate를 읽고,
 * 백엔드 /planCycleSource API를 호출해 나머지 속성을 보충.
 * storeToRefs 호환 reactive store 반환.
 */
// 싱글톤 캐시 — 원본 Pinia store처럼 동일 인스턴스를 반환
let _planCycleStoreInstance: ReturnType<typeof _createPlanCycleStore> | null = null;

function _createPlanCycleStore() {
  const hostData = useHostData();

  // 백엔드에서 가져온 planCycle 데이터
  const _planCycleSource = ref<any[]>([]);
  const _currentPlan = ref<any>(null);

  const projectId = computed(
    () => hostData.value?.projectInfo?.currentProjectID ?? ""
  );
  const hostPlanVer = computed(
    () => hostData.value?.planCycle?.planVer ?? ""
  );

  // ── 컴포넌트 라이프사이클과 분리된 effect scope ──
  // 싱글톤 스토어의 watcher가 생성 컴포넌트 unmount 시에도 살아남도록 detached scope 사용
  const scope = effectScope(true /* detached */);
  scope.run(() => {
    // hostData에서 planCycleSource가 이미 제공된 경우 (Dev 모드) 동기화
    watch(
      () => hostData.value?.planCycle?.planCycleSource,
      (source) => {
        if (source?.length && !_planCycleSource.value.length) {
          _planCycleSource.value = source;
        }
      },
      { immediate: true }
    );

    // projectId 변경 시 planCycleSource 재조회
    // (hostData에 이미 있으면 스킵 — DeveloperTool이 이미 fetch 했으므로)
    watch(
      projectId,
      async (pid) => {
        if (!pid) return;
        // Dev 모드에서 DeveloperTool이 이미 planCycleSource를 제공하면 중복 fetch 방지
        if (hostData.value?.planCycle?.planCycleSource?.length) {
          _planCycleSource.value = hostData.value.planCycle.planCycleSource;
          return;
        }
        try {
          const res: any = await api.post(
            `/api/custom/backend/${pid}/planCycleSource`
          );
          _planCycleSource.value = res?.data ?? [];
        } catch {
          _planCycleSource.value = [];
        }
      },
      { immediate: true }
    );

    // planVer 또는 source 변경 시 현재 plan 매칭
    watch(
      [hostPlanVer, _planCycleSource],
      ([pv, source]) => {
        if (!pv || !source?.length) {
          _currentPlan.value = null;
          return;
        }
        _currentPlan.value =
          source.find((p: any) => p.plan_ver === pv) ?? null;
      },
      { immediate: true }
    );
  });

  // hostData에 확장 속성이 있으면 (Dev 모드) 사용, 없으면 fetch 결과 사용
  const get = (fetchKey: string, hostKey?: string) =>
    computed(
      () =>
        _currentPlan.value?.[fetchKey] ??
        hostData.value?.planCycle?.[hostKey ?? fetchKey] ??
        ""
    );

  return reactive({
    $id: "planCycleStore",
    planVer: computed({
      get: () => hostPlanVer.value,
      set: (_v: string) => {
        /* controlled by host/devtool */
      },
    }),
    fromDate: computed({
      get: () => {
        const v = hostData.value?.planCycle?.fromDate;
        return v ? dayjs(v) : null;
      },
      set: (_v: any) => {},
    }),
    toDate: computed({
      get: () => {
        const v = hostData.value?.planCycle?.toDate;
        return v ? dayjs(v) : null;
      },
      set: (_v: any) => {},
    }),
    planCycleID: get("plan_cycle_id", "planCycleID"),
    planStartDate: get("plan_start_date", "planStartDate"),
    planPeriod: computed(
      () =>
        _currentPlan.value?.plan_period ??
        hostData.value?.planCycle?.planPeriod ??
        0
    ),
    planStatus: computed({
      get: () =>
        _currentPlan.value?.["plan_status"] ??
        hostData.value?.planCycle?.["planStatus"] ??
        "",
      set: (v: string) => {
        if (_currentPlan.value) {
          (_currentPlan.value as any).plan_status = v;
        }
      },
    }),
    demandVer: get("demand_ver", "demandVer"),
    currentPlanCycleSource: computed(
      () =>
        _currentPlan.value ??
        hostData.value?.planCycle?.currentPlanCycleSource ??
        null
    ),
    planCycleSource: computed(() =>
      _planCycleSource.value.length
        ? _planCycleSource.value
        : hostData.value?.planCycle?.planCycleSource ?? []
    ),
    updatePlanCycleStore(
      _cycleId: string,
      _keys: string[],
      _values: any[]
    ) {
      // stub — frozen plan 조작은 APS 프록시를 통해 처리
    },
    $patch(_data: any) {
      // stub
    },
    $subscribe(_cb: any) {
      // no-op
    },
  });
}

export function usePlanCycleStore() {
  if (!_planCycleStoreInstance) {
    _planCycleStoreInstance = _createPlanCycleStore();
  }
  return _planCycleStoreInstance;
}

/**
 * useProjectInfoStore — 원본 APS의 useProjectInfoStore 대체
 *
 * hostData에서 프로젝트/사용자 정보 + dateFormat 읽기.
 * formatGrid, convertToFormat, restoreDate 유틸리티 메서드 직접 구현.
 */
let _projectInfoStoreInstance: any = null;

export function useProjectInfoStore() {
  if (_projectInfoStoreInstance) return _projectInfoStoreInstance;

  const hostData = useHostData();
  const dateFormat = computed(
    () => hostData.value?.dateFormat ?? "YYYY-MM-DD"
  );

  _projectInfoStoreInstance = reactive({
    $id: "projectInfoStore",
    currentProjectID: computed(
      () => hostData.value?.projectInfo?.currentProjectID ?? ""
    ),
    currentProject: computed(
      () => hostData.value?.projectInfo?.currentProject ?? {}
    ),
    userInfo: computed(
      () => hostData.value?.projectInfo?.userInfo ?? {}
    ),
    isAdmin: computed(
      () => hostData.value?.projectInfo?.isAdmin ?? false
    ),

    /**
     * formatGrid — Wijmo 그리드 컬럼 포맷 문자열 반환
     */
    formatGrid(type: string): string {
      switch (type) {
        case "qty":
          return "G2";
        case "ratio":
          return "G1";
        case "priority":
          return "d";
        case "aggregate":
          return "F1";
        case "date": {
          return dateFormat.value
            .replace(/[YD]/g, (m: string) => m.toLowerCase())
            .replace(/\//g, `'/'`);
        }
        case "dateTime": {
          const fmt = dateFormat.value
            .replace(/[YD]/g, (m: string) => m.toLowerCase())
            .replace(/\//g, `'/'`);
          return `${fmt} HH:mm:ss`;
        }
        case "dateWeek": {
          return dateFormat.value
            .replace(/(MM-DD)|(MM\/DD)/gi, "Wss")
            .replace(/YYYY/gi, "yyyy")
            .replace(/(^[-/]+|[-/]+$)/g, "");
        }
        case "dateMonth": {
          return dateFormat.value
            .replace(/(MM-DD)|(MM\/DD)/gi, "MM")
            .replace(/YYYY/gi, "yyyy")
            .replace(/(^[-/]+|[-/]+$)/g, "");
        }
        default:
          return "";
      }
    },

    /**
     * convertToFormat — 값을 포맷 문자열로 변환
     */
    convertToFormat(type: string, value: any): string {
      if (value === null || value === undefined) return "";
      switch (type) {
        case "qty": {
          const num = Number(value);
          return isNaN(num)
            ? String(value)
            : num.toLocaleString(undefined, { maximumFractionDigits: 2 });
        }
        case "priority": {
          const num = Number(value);
          return isNaN(num) ? String(value) : String(Math.round(num));
        }
        case "ratio": {
          const num = Number(value);
          return isNaN(num) ? String(value) : `${num.toFixed(1)}%`;
        }
        case "aggregate": {
          const num = Number(value);
          return isNaN(num)
            ? String(value)
            : num.toLocaleString(undefined, { maximumFractionDigits: 2 });
        }
        case "date":
          return dayjs(value).format(dateFormat.value);
        case "dateDay":
          return dayjs(value).format(`${dateFormat.value} (ddd)`);
        case "dateTime":
          return dayjs(value).format(`${dateFormat.value} HH:mm:ss`);
        case "dateWeek": {
          const fmt = dateFormat.value.replace(
            /(MM-DD)|(MM\/DD)/gi,
            "Wss"
          );
          return dayjs(value).format(fmt);
        }
        case "dateMonth": {
          const fmt = dateFormat.value.replace(
            /(MM-DD)|(MM\/DD)/gi,
            "MM"
          );
          return dayjs(value).format(fmt);
        }
        default:
          return String(value ?? "");
      }
    },

    /**
     * restoreDate — 포맷된 날짜 문자열 → 구성요소 파싱
     */
    restoreDate(type: string, date: string): any {
      if (!date) return null;
      const fmt = dateFormat.value;
      const formatYear = (fmt.match(/Y/gi) || []).length;
      const yearIdx = fmt.match(/Y/i)?.index;

      if (type === "date") {
        const regEx = yearIdx
          ? `^(\\d{2})[-/](\\d{2})[-/](\\d{${formatYear}})$`
          : `^(\\d{${formatYear}})[-/](\\d{2})[-/](\\d{2})$`;
        const match = date.match(new RegExp(regEx));
        if (!match) return null;
        const year = match[yearIdx ? 3 : 1];
        const month = match[yearIdx ? 1 : 2];
        const day = match[yearIdx ? 2 : 3];
        return {
          year: formatYear === 4 ? year : `20${year}`,
          month,
          day,
        };
      }
      if (type === "dateMonth") {
        const regEx = yearIdx
          ? `^(\\d{2})[-/](\\d{${formatYear}})$`
          : `^(\\d{${formatYear}})[-/](\\d{2})$`;
        const match = date.match(new RegExp(regEx));
        if (!match) return null;
        const year = match[yearIdx ? 2 : 1];
        const month = match[yearIdx ? 1 : 2];
        return {
          year: formatYear === 4 ? year : `20${year}`,
          month,
        } as any;
      }
      if (type === "dateWeek") {
        const regEx = yearIdx
          ? `^W(\\d{2})[-/](\\d{${formatYear}})$`
          : `^(\\d{${formatYear}})[-/]W(\\d{2})$`;
        const match = date.match(new RegExp(regEx));
        if (!match) return null;
        const year = match[yearIdx ? 2 : 1];
        const week = match[yearIdx ? 1 : 2];
        return {
          year: formatYear === 4 ? year : `20${year}`,
          week,
        } as any;
      }
      return null;
    },

    getOptionInfo() {
      return {};
    },
  });
  return _projectInfoStoreInstance;
}

/**
 * useMenuStore — 원본 APS의 useMenuStore 대체
 */
let _menuStoreInstance: any = null;

export function useMenuStore() {
  if (_menuStoreInstance) return _menuStoreInstance;

  const hostData = useHostData();

  _menuStoreInstance = reactive({
    $id: "menuStore",
    currentMenu: computed(
      () =>
        hostData.value?.menu?.currentMenu ?? {
          menuID: "NewRtfReport",
          menuName: "menu-new_rtf_report",
          parentMenuName: "menu-sp",
          isWrite: false,
        }
    ),
    items: computed(() => hostData.value?.menu?.items ?? []),
    currentMenuId: computed(
      () => hostData.value?.menu?.currentMenuId ?? ""
    ),
    getNavis: ref([] as any[]),
  });
  return _menuStoreInstance;
}

/**
 * useProjectInfo — BomMap용 alias (useProjectInfoStore 위임)
 */
export function useProjectInfo() {
  return useProjectInfoStore();
}

// ══════════════════════════════════════════════════════════
// Local Adapters (Host에 없는 로컬 스토어)
// ══════════════════════════════════════════════════════════

export function useLoadStore() {
  const loading = ref(false);
  return reactive({
    loading,
    set(value: boolean) {
      loading.value = value;
    },
  });
}

export function useBroadcastMessage() {
  return reactive({
    sender: "",
    message: "",
    planVer: "",
    demandVer: "",
    planStartDate: "",
    planPeriod: "",
    planScenario: "",
    description: "",
    runTime: new Date(),
    planCycleID: "",
    $subscribe(_cb: any) {
      // no-op — broadcast not available in MF context
    },
  });
}

export function useTextareaValidation() {
  const showValidation = ref(false);
  return reactive({
    showValidation,
  });
}
