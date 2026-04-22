/**
 * Re-Execute Plan API & Composable
 *
 * 계획 재실행 페이지의 데이터 계층.
 * APS ReExecutePlan.ts를 custom-ui-templates 패턴으로 포팅.
 */
import { api, getProjectId } from "@/api/client";
import { useQtyUomQuery } from "@/composables/useQtyUomQuery";
import { CollectionView } from "@vmscloud/moz-wijmo-grid/wijmo";
import dayjs, { type Dayjs } from "dayjs";
import { useTranslation } from "i18next-vue";
import {
  computed,
  onMounted,
  type Ref,
  ref,
  shallowRef,
  toRaw,
  watch,
} from "vue";

// ===== API Base URL =====

const BASE_URL = () => `/api/custom/backend/${getProjectId()}/re-execute-plan`;

// ===== Types =====

export interface InboundItemType {
  projectID: string;
  inboundScenarioID: string | null;
  inboundScenarioName: string;
  newInboundScenarioID: string | null;
  newInboundScenarioName: string | null;
  description: string | null;
  createDatetime: string | null;
  createUserID: string | null;
  updateDatetime: string | null;
  updateUserID: string | null;
}

export interface ExecutionFlowMasterType {
  execution_flow_id: string;
  inbound_scenario_id?: string;
  engine_scenario_id?: string;
  [key: string]: any;
}

export interface ScenarioMasterType {
  projectID: string;
  scenarioID: string;
  scenarioName: string;
  newScenarioID: any;
  scenarioType: string;
  description: any;
  createDatetime: any;
  createUser: any;
  updateDatetime: any;
  updateUser: any;
}

// ===== API Functions =====

export const fetchMain = (params: any) =>
  api.post<{ data: any[]; actStartDate: string; actEndDate: string }>(
    `${BASE_URL()}/main`,
    params,
  );

export const fetchRegions = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/regions?planVer=${planVer}`);

export const fetchOperGroups = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/oper-groups?planVer=${planVer}`);

export const fetchOperSource = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/opers?planVer=${planVer}`);

export const fetchBuffers = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/buffers?planVer=${planVer}`);

// ===== C# 백엔드 직접 호출 (Host 환경) =====
// ===== C# APS 프록시 API (Python BE 경유) =====
export const fetchDemandSource = (params: any) =>
  api.post<any>(`${BASE_URL()}/proxy/demand-source`, params);

export const fetchPlanCycleInfo = (planVer?: string) => {
  const pv = planVer ?? "";
  return api.get<{ data: any }>(
    `${BASE_URL()}/plan-cycle-info?planVer=${encodeURIComponent(pv)}`,
  );
};

export const fetchExecutionFlows = (params?: any) =>
  api.post<any>(`${BASE_URL()}/proxy/execution-flows`, params ?? {});

export const fetchScenarioList = (params?: any) =>
  api.post<any>(`${BASE_URL()}/proxy/scenarios`, params ?? {});

export const fetchScenarioConfig = (scenarioID: string) =>
  api.post<any>(`${BASE_URL()}/proxy/scenario-config`, { scenarioID });

export const fetchScenarioModules = (params: { scenarioID: string }) =>
  api.post<any>(`${BASE_URL()}/proxy/scenario-modules`, params);

// 원본 ExecutionFlowMasterDetailSummary 가 inbound 탭 트리/데이터 스토리지 그리드에 쓰는
// PlmInboundScenarioMaster/Config 프록시. inboundScenarioID 기준 option tree 반환.
export const fetchInboundScenarioConfig = (params: {
  inboundScenarioID: string;
  planVer?: string;
}) => api.post<any>(`${BASE_URL()}/proxy/inbound-scenario-config`, params);

export const fetchDemandVer = (params: { planCycleID: string }) => {
  const pc = params?.planCycleID ?? "";
  return api.get<{ data: any[] }>(
    `${BASE_URL()}/demand-vers?planCycleID=${encodeURIComponent(pc)}`,
  );
};

export const fetchNewDemandVer = (params: { demand_ver: string }) =>
  api.post<any>(`${BASE_URL()}/proxy/demand-ver-latest`, params);

export const fetchDemandVerValidCheck = (params: { demand_ver: string }) =>
  api.post<any>(`${BASE_URL()}/proxy/demand-ver-check`, params);

export const fetchInbound = (params?: any) =>
  api.post<any>(`${BASE_URL()}/proxy/inbound`, params ?? {});

export const fetchPlanVerInfo = (params?: any) =>
  api.post<any>(`${BASE_URL()}/proxy/plan-ver-info`, params ?? {});

export const postReExecutePlan = (params: any) =>
  api.post<any>(`${BASE_URL()}/proxy/execute`, params);

export const fetchCustInRtf = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/customers?planVer=${planVer}`);

export const fetchItemGroupInRtf = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/item-groups?planVer=${planVer}`);

export const fetchDemandTypes = (planVer: string) =>
  api.get<{ data: any[] }>(`${BASE_URL()}/demand-types?planVer=${planVer}`);

// ===== Composable =====

export const useReExecutePlanQuery = (
  planVer: Ref<string>,
  planCycleID: Ref<string>,
  _fromDate: any,
  _toDate: any,
) => {
  const { t } = useTranslation();

  const operGroupSource = ref<any>([]);
  const operGroups = ref<any>([]);

  const operSource = ref<any>([]);
  const opers = ref<any>([]);

  const bufferSource = ref<any>([]);
  const buffers = ref<any>([]);

  const planVerSource = ref<any>([]);
  const targetPlanVerData = ref<any>();

  const isAdvancedOption = ref<boolean>(false);
  const executionFlowSource = ref<ExecutionFlowMasterType[]>([]);

  /**
   * 조회조건
   */
  const summaryType = ref<string>("itemGroup");
  const summarySource = ref<any[]>([
    { label: t("text-upper-item_group"), value: "itemGroup" },
    { label: t("text-upper-customer"), value: "cust" },
    { label: t("text-upper-region"), value: "region" },
    { label: t("text-upper-demand_type"), value: "demandType" },
  ]);

  // Customer filter
  const custParam = ref<any[]>([]);
  const custSource = ref<any[]>([]);
  const custIsSuccess = ref(false);

  // ItemGroup filter
  const itemGroup = ref<any[]>([]);
  const itemGroupSource = ref<any[]>([]);
  const itemGroupIsSuccess = ref(false);

  // Region filter
  const region = ref<any[]>([]);
  const regionSource = ref<any[]>([]);
  const regionIsSuccess = ref(false);

  // DemandType filter
  const demandType = ref<any[]>([]);
  const demandTypeSource = ref<any[]>([]);
  const demandTypeIsSuccess = ref(false);

  // UOM — 원본 useQtyUomQuery와 동일한 초기화(URL qtyUOM → localStorage → defaultValue)
  const { uomType, qtyUOMSource } = useQtyUomQuery(
    ["DEFAULT", "CONVERSION"],
    "DEFAULT",
    { menuID: "reExecutePlanUomType" },
  );

  const widgetSummarySource = ref<any[]>([
    { label: t("text-upper-item_group"), value: "itemGroup" },
    { label: t("text-upper-customer"), value: "cust" },
    { label: t("text-upper-region"), value: "region" },
    { label: t("text-upper-demand_type"), value: "demandType" },
  ]);

  const viewPointSource = ref<any[]>([
    { label: t("text-upper-customer"), value: "cust" },
    { label: t("text-upper-item_group"), value: "itemGroup" },
    { label: t("text-upper-region"), value: "region" },
    { label: t("text-upper-demand_type"), value: "demandType" },
  ]);

  const breakdownValue = ref<string>("OPER");
  const breakdownSearchSource = ref<any[]>([
    { label: t("text-oper"), value: "OPER" },
    { label: t("text-oper-group"), value: "OPERGROUP" },
    { label: t("text-buffer"), value: "BUFFER" },
  ]);

  const breakdownSource = ref<any[]>([
    { label: t("text-oper"), value: "OPER" },
    { label: t("text-oper-group"), value: "OPERGROUP" },
    { label: t("text-buffer"), value: "BUFFER" },
  ]);

  /**
   * 계획 재실행 메뉴
   */
  const demandSource = ref<any[]>();
  const selectedDemandList = shallowRef<any[]>([]);

  const pivotDataSource = shallowRef<any[]>([]);
  const fullDataSource = shallowRef<any[]>([]);

  // propColumns (simplified)
  const propColumns = ref<any[]>([]);

  // 공유 CollectionView
  const sharedCollectionView = shallowRef<CollectionView | null>(null);
  const isCollectionViewInitialized = ref<boolean>(false);

  // 그리드 참조 공유
  const mainGrid = ref<any>(null);
  const popupGrid = ref<any>(null);

  // ExtendGrid 인스턴스 참조 공유
  const mainExtendGrid = ref<any>(null);
  const popupExtendGrid = ref<any>(null);

  // computed 강제 업데이트용 트리거
  const updateTrigger = ref(0);

  // 원본 column filter 함수 보관
  const originalColumnFilter = ref<((item: any) => boolean) | null>(null);

  // CollectionView 초기화
  const initializeSharedCollectionView = () => {
    if (!demandSource.value?.length) {
      return;
    }

    demandSource.value.forEach((item, index) => {
      const ridKey = "_RID";
      if (item && !item[ridKey]) {
        item[ridKey] = `original_${item.demand_id || index}`;
      }
    });

    if (sharedCollectionView.value) {
      sharedCollectionView.value.sourceCollection = demandSource.value;
      sharedCollectionView.value.refresh();
    } else {
      sharedCollectionView.value = new CollectionView(demandSource.value);
    }

    isCollectionViewInitialized.value = true;
  };

  const sharedDataSource = computed(
    () => sharedCollectionView.value || demandSource.value,
  );

  // 팝업 전용 CollectionView
  const popupCollectionView = shallowRef<CollectionView | null>(null);

  const initializePopupCollectionView = () => {
    if (demandSource.value && demandSource.value.length > 0) {
      popupCollectionView.value = new CollectionView(demandSource.value);
      return;
    }
    console.warn("demandSource가 없어서 popupCollectionView 초기화 불가");
  };

  const showEditedData = ref<boolean>(false);

  const applyPopupFilter = () => {
    if (!popupCollectionView.value) {
      console.warn("popupCollectionView가 없어서 필터 적용 불가");
      return;
    }

    if (!showEditedData.value) {
      popupCollectionView.value.filter = null;
      popupCollectionView.value.refresh();
    } else {
      if (
        mainExtendGrid.value &&
        mainExtendGrid.value.updated &&
        mainExtendGrid.value.updated.size > 0
      ) {
        const updatedRIDs = new Set(mainExtendGrid.value.updated.keys());
        const ridKey = "_RID";
        popupCollectionView.value.filter = (item: any) =>
          item[ridKey] && updatedRIDs.has(item[ridKey]);
        popupCollectionView.value.refresh();
      } else {
        popupCollectionView.value.filter = () => false;
        popupCollectionView.value.refresh();
      }
    }
  };

  const popupDataSource = computed(() => demandSource.value);

  const applyPopupGridFilter = (gridRef: any) => {
    if (!gridRef || !gridRef.collectionView) return;

    const cv = gridRef.collectionView;

    if (!showEditedData.value) {
      const filterStr = cv.filter?.toString() || "";
      const isOurFilter =
        filterStr.includes("isUpdated") || filterStr.includes("_RID");

      if (!isOurFilter && cv.filter && typeof cv.filter === "function") {
        originalColumnFilter.value = cv.filter;
      } else if (!isOurFilter && !cv.filter) {
        originalColumnFilter.value = null;
      } else if (isOurFilter) {
        if (originalColumnFilter.value) {
          cv.filter = originalColumnFilter.value;
        } else {
          cv.filter = null;
        }
      }
    } else {
      if (
        mainExtendGrid.value &&
        mainExtendGrid.value.updated &&
        mainExtendGrid.value.updated.size > 0
      ) {
        const updatedRIDs = new Set(mainExtendGrid.value.updated.keys());
        const ridKey = "_RID";

        cv.filter = (item: any) => {
          const isUpdated = item[ridKey] && updatedRIDs.has(item[ridKey]);
          if (originalColumnFilter.value) {
            return isUpdated && originalColumnFilter.value(item);
          }
          return isUpdated;
        };
      } else {
        cv.filter = () => false;
      }
    }

    cv.refresh();
  };

  /**
   * API 호출
   */

  const mainQueryIsPending = ref(false);

  // 원본(lb/re-execute-plan)은 TanStack useQuery 의 isPending 을 바로 쓰지만,
  //   그 경우 HTTP fetch 가 끝난 직후 스피너가 사라져 Wijmo PivotEngine 이 동기 집계하는
  //   수초 동안 빈 화면으로 보이는 UX 불만이 있다. isPivotRendering 은 "fetch 시작 ~
  //   pivot 의 첫 loadedRows" 구간만 덮는 보조 플래그. watchdog 없이 loadedRows 에만 의존.
  const isPivotRendering = ref(false);

  const onLoad = async () => {
    await onMainLoad();
    await loadPlanVerInfo();
  };

  const isPageFetching = computed(() => mainQueryIsPending.value);

  /**
   * 계획 재실행 POPUP
   */

  const isOpen = ref<boolean>(false);

  const toggle = () => {
    isOpen.value = !isOpen.value;
  };

  const open = () => {
    isOpen.value = true;
  };

  const close = () => {
    isOpen.value = false;
  };

  const verInfoIsOpen = ref<boolean>(false);

  const openVerInfo = () => {
    verInfoIsOpen.value = true;
  };

  const closeVerInfo = () => {
    verInfoIsOpen.value = false;
  };

  const currentStep = ref<1 | 2>(1);

  // 수정된 데이터만 필터링하는 computed
  const editedDemandSource = computed(() => {
    updateTrigger.value;

    if (!showEditedData.value) {
      return sharedDataSource.value;
    }

    if (
      mainExtendGrid.value &&
      mainExtendGrid.value.updated &&
      sharedDataSource.value
    ) {
      const updatedRIDs = new Set(mainExtendGrid.value.updated.keys());
      const sourceArray =
        (sharedDataSource.value as any)?.items || sharedDataSource.value;
      const ridKey = "_RID";
      const filteredData = sourceArray?.filter(
        (item: any) => item[ridKey] && updatedRIDs.has(item[ridKey]),
      );
      return filteredData;
    }

    return [];
  });

  const alwaysEditedData = computed(() => {
    updateTrigger.value;

    if (
      mainExtendGrid.value &&
      mainExtendGrid.value.updated &&
      demandSource.value
    ) {
      const updatedRIDs = new Set(mainExtendGrid.value.updated.keys());
      const sourceArray = demandSource.value;
      const ridKey = "_RID";
      const filteredData = sourceArray?.filter((item: any) => {
        const hasRID = !!item?.[ridKey];
        const isUpdated = updatedRIDs.has(item?.[ridKey]);
        return hasRID && isUpdated;
      });
      return filteredData;
    }

    return [];
  });

  /**
   * util 함수
   */

  const getDaysUntilEndOfMonth = (today: Date) => {
    const year = today.getFullYear();
    const month = today.getMonth();
    const endOfMonth = new Date(year, month + 1, 0);
    const daysRemaining =
      Math.ceil(
        (endOfMonth.getTime() - today.getTime()) / (1000 * 60 * 60 * 24),
      ) + 1;
    return String(daysRemaining);
  };

  const initNoExecution = (): InboundItemType => ({
    projectID: "",
    inboundScenarioID: null,
    inboundScenarioName: t("text-use_aps_data"),
    newInboundScenarioID: null,
    newInboundScenarioName: null,
    description: null,
    createDatetime: null,
    createUserID: null,
    updateDatetime: null,
    updateUserID: null,
  });

  const inboundSource = ref<InboundItemType[]>([initNoExecution()]);

  const nowDayjs = dayjs();
  const nowTimeStr = nowDayjs.format("HH:mm");

  const reExecuteState = ref<{
    executionFlowID: string | null;
    planCycleID: string;
    startDate: Dayjs;
    planStartTime: string;
    period: string | number;
    demandVer: string;
    demandDesc: string;
    viewDemandDetail: boolean;
    scenarioID: string | null;
    viewScenarioDetail: boolean;
    planDesc: string;
    inboundScenarioID: string | null;
    outboundScenarioID: string | null;
    useInboundYN: boolean;
    useReservation: boolean;
    editSummary: {
      dueDateCnt: number;
      demandPriorityCnt: number;
      delayCnt: number;
      shorteningCnt: number;
      maxDueDateCnt: number;
    };
  }>({
    executionFlowID: null,
    planCycleID: "",
    startDate: nowDayjs,
    planStartTime: nowTimeStr,
    period: getDaysUntilEndOfMonth(nowDayjs.toDate()),
    demandVer: "",
    demandDesc: "",
    viewDemandDetail: false,
    scenarioID: null,
    viewScenarioDetail: false,
    planDesc: "",
    inboundScenarioID: null,
    outboundScenarioID: null,
    useInboundYN: true,
    useReservation: false,
    editSummary: {
      dueDateCnt: 0,
      demandPriorityCnt: 0,
      delayCnt: 0,
      shorteningCnt: 0,
      maxDueDateCnt: 0,
    },
  });

  watch(
    () => reExecuteState.value.startDate,
    (newVal) => {
      // newVal은 Dayjs. getDaysUntilEndOfMonth는 Date를 기대하므로 변환.
      const dateObj =
        newVal && typeof (newVal as any).toDate === "function"
          ? (newVal as any).toDate()
          : newVal instanceof Date
            ? newVal
            : new Date(newVal as any);
      reExecuteState.value.period = getDaysUntilEndOfMonth(dateObj);
    },
  );

  /**
   * 계획 재실행을 위한 최신 PlanCycle 정보 조회
   */

  const currentPlanCycleSource = ref<any>({});

  const loadPlanCycleInfo = async () => {
    if (!planVer.value) return;
    try {
      const result = await fetchPlanCycleInfo(planVer.value);
      if (result && result.data) {
        currentPlanCycleSource.value = result.data;
        reExecuteState.value.planCycleID = result.data?.plan_cycle_id ?? "";
      } else {
        currentPlanCycleSource.value = {};
        reExecuteState.value.planCycleID = "";
      }
    } catch {
      console.error("PlanCycleInfo 조회 오류");
      currentPlanCycleSource.value = {};
      reExecuteState.value.planCycleID = "";
    }
  };

  const loadExecutionFlows = async () => {
    try {
      const result = await fetchExecutionFlows();
      if (result && result.data?.length) {
        executionFlowSource.value = toRaw(result.data).filter(
          (item: ExecutionFlowMasterType) =>
            item.inbound_scenario_id || item.engine_scenario_id,
        );
        reExecuteState.value.executionFlowID =
          result.data[0].execution_flow_id || null;
      } else {
        executionFlowSource.value = [];
      }
    } catch {
      console.error("ExecutionFlow 조회 오류");
      executionFlowSource.value = [];
    }
  };

  const scenarioList = ref<ScenarioMasterType[]>([]);

  const loadScenarioList = async () => {
    try {
      const result = await fetchScenarioList();
      if (result && result.data) {
        scenarioList.value = result.data;
        scenarioList.value.unshift({
          projectID: "",
          scenarioID: null as unknown as string,
          scenarioName: t("text-no_execution"),
          newScenarioID: null as unknown as any,
          scenarioType: "Default",
          description: null as unknown as any,
          createDatetime: null as unknown as any,
          createUser: null as unknown as any,
          updateDatetime: null as unknown as any,
          updateUser: null as unknown as any,
        });
        reExecuteState.value.scenarioID = result.data[0]?.scenarioID || null;
      } else {
        scenarioList.value = [];
        reExecuteState.value.scenarioID = null;
      }
    } catch {
      console.error("ScenarioList 조회 오류");
    }
  };

  const scenarioConfigSource = shallowRef<any[]>([]);

  const loadScenarioConfig = async (scenarioIDOverride?: string) => {
    const scenarioID =
      scenarioIDOverride ?? reExecuteState.value.scenarioID ?? "";
    if (!scenarioID) {
      scenarioConfigSource.value = [];
      return;
    }
    try {
      const result = await fetchScenarioConfig(scenarioID);
      if (result && result.data) {
        scenarioConfigSource.value = result.data;
      } else {
        scenarioConfigSource.value = [];
      }
    } catch {
      console.error("ScenarioConfig 조회 오류");
    }
  };

  watch(
    () => reExecuteState.value.scenarioID,
    async (newVal) => {
      if (newVal) {
        await loadScenarioConfig();
      } else {
        scenarioConfigSource.value = [];
      }
    },
  );

  /**
   * 수요 정보 버전 조회
   */

  const demandVerSource = shallowRef<any[]>([]);
  const demandSetText = computed(() => {
    if (demandVerSource.value.length) {
      const initDemand =
        demandVerSource.value[demandVerSource.value.length - 1];
      return `${initDemand.demand_ver}-R${demandVerSource.value.length.toString().padStart(3, "0")}`;
    }
    return "";
  });

  const getDemandSourceIsPending = ref(false);

  const loadDemandSource = async (param: any) => {
    if (!param) return;
    getDemandSourceIsPending.value = true;
    try {
      const result = await fetchDemandSource(param);
      if (result && result.data) {
        const headers = result.data.headers ?? [];
        const schemaName = param?.schema_name || "Demand";
        const dataArray = result.data[schemaName] || [];

        if (headers.length) {
          propColumns.value = headers.map((h: any) => ({
            binding: h.binding || h.key,
            header: h.header || h.label,
            dataType: h.dataType,
            width: h.width || "*",
            align: h.align || "left",
          }));
        }

        if (dataArray.length) {
          demandSource.value = dataArray;
        } else {
          demandSource.value = [];
          propColumns.value = [];
        }
      } else {
        demandSource.value = [];
        propColumns.value = [];
      }
    } catch {
      console.error("DemandSource 조회 오류");
      demandSource.value = [];
      propColumns.value = [];
    } finally {
      getDemandSourceIsPending.value = false;
    }
  };

  // Oper Group / Oper / Buffer loading flags
  const getOperGroupSourceIsSuccess = ref(false);
  const getOperSourceIsSuccess = ref(false);
  const getBufferSourceIsSuccess = ref(false);

  const loadOperGroupSource = async (param: any) => {
    if (!param) return;
    const pv =
      typeof param === "string" ? param : param?.planVer || planVer.value;
    if (!pv) return; // planVer 미정 상태에서 fetch/flag 변경 방지
    try {
      const result = (await fetchOperGroups(pv)) as any;
      if (result?.success && result?.data?.length) {
        operGroupSource.value = result.data;
        operGroups.value = operGroupSource.value.map(
          (item: any) => item.oper_group_id,
        );
        getOperGroupSourceIsSuccess.value = true;
      } else {
        operGroupSource.value = [];
        operGroups.value = [];
        getOperGroupSourceIsSuccess.value = true;
      }
    } catch {
      console.error("OperGroupSource 조회 오류");
      operGroupSource.value = [];
      operGroups.value = [];
    }
  };

  const loadOperSource = async (param: any) => {
    if (!param) return;
    const pv =
      typeof param === "string"
        ? param
        : param?.plan_ver || param?.planVer || planVer.value;
    if (!pv) return;
    try {
      const result = (await fetchOperSource(pv)) as any;
      if (result.data && result.data.length) {
        operSource.value = result.data;
        opers.value = operSource.value.map((item: any) => item.oper_id);
        getOperSourceIsSuccess.value = true;
      } else {
        operSource.value = [];
        opers.value = [];
        getOperSourceIsSuccess.value = true;
      }
    } catch {
      console.error("OperSource 조회 오류");
      operSource.value = [];
      opers.value = [];
    }
  };

  const loadBufferSource = async (param: any) => {
    if (!param) return;
    const pv =
      typeof param === "string"
        ? param
        : param?.plan_ver || param?.planVer || planVer.value;
    if (!pv) return;
    try {
      const result = (await fetchBuffers(pv)) as any;
      if (result.data && result.data.length) {
        bufferSource.value = result.data;
        buffers.value = bufferSource.value.map((item: any) => item.buffer_id);
        getBufferSourceIsSuccess.value = true;
      } else {
        bufferSource.value = [];
        buffers.value = [];
        getBufferSourceIsSuccess.value = true;
      }
    } catch {
      console.error("BufferSource 조회 오류");
      bufferSource.value = [];
      buffers.value = [];
    }
  };

  const loadDemandVer = async (param: any) => {
    if (!param.planCycleID) return;
    try {
      const result = await fetchDemandVer(param);
      if (result && result.data && result.data.length) {
        demandVerSource.value = result.data;
      } else {
        demandVerSource.value = [];
      }
    } catch {
      console.error("DemandVer 조회 오류");
      demandVerSource.value = [];
    }
  };

  const loadInbound = async () => {
    try {
      const result = await fetchInbound();
      if (result && result?.data) {
        if (result?.data?.details) {
          inboundSource.value = [initNoExecution(), ...result.data.details];
        }
      } else {
        inboundSource.value = [initNoExecution()];
      }
    } catch {
      console.error("Inbound 조회 오류");
      inboundSource.value = [initNoExecution()];
    }
  };

  // widget 설정
  const initWidgetSetting = ref<any>();
  const viewPointWidget = ref<any[]>([
    "itemGroup",
    "cust",
    "region",
    "demandType",
  ]);
  const breakdownWidget = ref<any>(breakdownSource.value[0]);

  const reExecutePlanMutation = async (param: any) => {
    try {
      const result = await postReExecutePlan(param);
      if (result && result.data) {
        console.log("계획이 재실행 되었습니다");
      }
    } catch {
      console.error("계획 재실행 중 오류가 발생했습니다");
    }
  };

  const scenarioModuleDataSource = shallowRef<any[]>([]);
  const phaseColumns = ref<
    {
      binding: string | number;
      header: string;
      width: string | number;
    }[]
  >([]);

  const loadScenarioModules = async (param: { scenarioID: string }) => {
    try {
      const result = await fetchScenarioModules(param);
      if (result && result.data && result.data.length > 0) {
        scenarioModuleDataSource.value = result.data;
      } else {
        scenarioModuleDataSource.value = [];
      }
    } catch {
      console.error("ScenarioModule 조회 오류");
      scenarioModuleDataSource.value = [];
    }
  };

  // inbound 탭 tree/data_storage 그리드 데이터.
  //   원본 ExecutionFlowMasterDetailSummary: inboundID 바뀔 때 PlmInboundScenarioMaster/Config 호출,
  //   응답을 Category/Menu 로 트리화해서 표시한다. 우리는 원본과 달리 다국어 키 변환(menuType==='Category'→
  //   t(optionID), 'cfg_*'→t('text-global-upper-*') 등)은 템플릿에서 직접 다루지 않고 원본 데이터 형태 그대로
  //   넘긴다 (i18n 키 매핑은 필요 시 별도 유틸로).
  const inboundItemOptions = shallowRef<any>({});

  const loadInboundItemOptions = async (inboundScenarioID: string) => {
    if (!inboundScenarioID) {
      inboundItemOptions.value = {};
      return;
    }
    try {
      const result = await fetchInboundScenarioConfig({
        inboundScenarioID,
        ...(planVer.value ? { planVer: planVer.value } : {}),
      });
      if (result && result.data) {
        const raw = result.data;
        const list: any[] = Array.isArray(raw.list) ? [...raw.list] : [];
        // 원본 menuListToTree 와 동일: multilingual(i18n 키 변환) + Y/N→boolean + Category 트리화
        const root: Record<string, any> = {};
        list.forEach((item) => {
          if (item.menuType === "Category") {
            root[item.menuID] = item;
            item.multilingual = t(item.optionID);
          }
          if (item.optionID?.startsWith("cfg_")) {
            item.multilingual = t(
              item.optionID.replace("cfg_", "text-global-upper-"),
            );
          }
          if (item.optionID?.startsWith("ope_")) {
            item.multilingual = t(
              item.optionID.replace("ope_", "text-global-upper-"),
            );
          }
          item.optionValue = item?.optionValue === "Y";
        });

        list
          .filter((item) => item.menuType === "Menu")
          .forEach((item) => {
            const parent = root[item.menuID];
            const childIdx = list.findIndex(
              (m) => m.optionID === item.optionID,
            );
            if (!parent || childIdx < 0) return;
            const childData = list.splice(childIdx, 1);
            parent.children = parent.children ?? [];
            parent.children.push(...childData);
            parent.children.sort(
              (x: any, y: any) => (x.seq ?? 0) - (y.seq ?? 0),
            );
            if (parent.children.some((c: any) => c.optionValue)) {
              parent.optionValue = true;
            }
          });
        list.sort((a, b) => (a.seq ?? 0) - (b.seq ?? 0));

        inboundItemOptions.value = {
          ...raw,
          list: list.filter((item) => item.optionID),
        };
      } else {
        inboundItemOptions.value = {};
      }
    } catch {
      console.error("InboundItemOptions 조회 오류");
      inboundItemOptions.value = {};
    }
  };

  watch(
    () => reExecuteState.value.inboundScenarioID,
    (newVal) => {
      loadInboundItemOptions(newVal ?? "");
    },
  );

  // executionFlow 선택 기반(Simple 모드)일 때도 inboundID가 바뀌면 로드되도록, 선택된 flow
  // 에서 도출되는 inboundID를 감시한다.
  watch(
    () => {
      const flow = executionFlowSource.value.find(
        (f) => f.execution_flow_id === reExecuteState.value.executionFlowID,
      );
      return flow?.inbound_scenario_id || null;
    },
    (newVal) => {
      if (!reExecuteState.value.inboundScenarioID) {
        loadInboundItemOptions(newVal ?? "");
      }
    },
  );

  const isDuplicated = ref<boolean>(false);

  const checkDemandVerValid = async (param: { demand_ver: string }) => {
    try {
      const result = await fetchDemandVerValidCheck(param);
      if (result.data && result.data.length > 0) {
        isDuplicated.value = true;
      } else {
        isDuplicated.value = false;
      }
    } catch {
      console.error("DemandVer 유효성 검사 오류");
      isDuplicated.value = false;
    }
  };

  const autoDemandVer = ref<string>("");

  const loadNewDemandVer = async (param: { demand_ver: string }) => {
    try {
      const result = await fetchNewDemandVer(param);
      if (result.data) {
        autoDemandVer.value = result.data.demand_ver;
      } else {
        autoDemandVer.value = "";
      }
    } catch {
      console.error("NewDemandVer 조회 오류");
      autoDemandVer.value = "";
    }
  };

  // loadParams — operGroupIDs는 마스터(odv_oper_group_master) 기반 리스트로 항상 명시 전송.
  //  우리 Iceberg 복사본에 마스터에 없는 가상 oper_group_id(예: '#Undefined')가 섞여 있어서
  //  빈 배열을 보내면 원본에 없는 가상 그룹이 포함되어 값이 부풀어 오름.
  //  마스터 리스트로 IN 필터를 걸면 원본과 동일한 집합이 집계됨.
  const loadParams = computed(() => ({
    planVer: planVer.value,
    planCycleID: planCycleID.value,
    summaryType: "OPERGROUP" as "OPERGROUP" | "BUFFER",
    aggregateType: summaryType.value,
    summary: summaryType.value as
      | "cust"
      | "itemGroup"
      | "region"
      | "demandType",
    ...(summaryType.value === "cust" && {
      customers: Array.from(new Set([...custParam.value])),
    }),
    ...(summaryType.value === "itemGroup" && {
      itemGroupIDs: itemGroup.value,
    }),
    ...(summaryType.value === "region" && { regions: region.value }),
    ...(summaryType.value === "demandType" && {
      demandTypes: demandType.value,
    }),
    uomType: uomType.value,
    operGroupIDs: operGroups.value,
  }));

  const addPrefix = (value: string) => {
    if (value === "FROZEN") return "1_FROZEN";
    if (value === "PLAN") return "2_PLAN";
    if (value === "DIFF") return "3_DIFF";
    return value;
  };

  const actStartDate = ref<string>("");
  const actEndDate = ref<string>("");

  const onMainLoad = async () => {
    // 마스터가 아직 로드되지 않은 상태에서 호출되면 operGroupIDs=[]로 전송돼
    // 백엔드가 전체(가상 그룹 포함) row를 집계해 값이 부풀어 오른다. 마스터 대기.
    if (!planVer.value) return;
    if (!operGroupSource.value.length) return;
    mainQueryIsPending.value = true;
    isPivotRendering.value = true;
    try {
      const result = (await fetchMain(loadParams.value)) as any;
      const pivotRows = result?.pivotData ?? result?.data ?? [];
      const demandRows = result?.demandData ?? [];

      if (pivotRows.length) {
        const processedData = pivotRows.map((value: any) => ({
          ...value,
          plan_type: addPrefix(value.plan_type),
        }));

        pivotDataSource.value = processedData.filter(
          (item: any) => item.date !== "TOTAL",
        );

        fullDataSource.value = processedData;

        actStartDate.value = result?.actStartDate ?? "";
        actEndDate.value = result?.actEndDate ?? "";

        // demandData도 세팅
        if (demandRows.length) {
          demandSource.value = demandRows;
        }
      } else {
        pivotDataSource.value = [];
        fullDataSource.value = [];
        actStartDate.value = "";
        actEndDate.value = "";
      }
    } catch {
      console.error("Main 데이터 조회 오류");
      pivotDataSource.value = [];
      actStartDate.value = "";
      actEndDate.value = "";
      isPivotRendering.value = false; // 에러 시 스피너 해제
    } finally {
      mainQueryIsPending.value = false;
      // 데이터 없음 → 집계할 게 없으니 즉시 해제. 있으면 pivotOnInitialized/loadedRows 에서 해제.
      if (!pivotDataSource.value?.length) {
        isPivotRendering.value = false;
      }
    }
  };

  // Load filter data
  const loadCustData = async () => {
    if (!planVer.value) return;
    try {
      const result = await fetchCustInRtf(planVer.value);
      if (result?.data?.length) {
        custSource.value = result.data;
        custParam.value = custSource.value.map((item: any) => item.cust_id);
        custIsSuccess.value = true;
      } else {
        custSource.value = [];
        custIsSuccess.value = true;
      }
    } catch {
      console.error("Customer 조회 오류");
      custIsSuccess.value = false;
    }
  };

  const loadItemGroupData = async () => {
    if (!planVer.value) return;
    try {
      const result = await fetchItemGroupInRtf(planVer.value);
      if (result?.data?.length) {
        itemGroupSource.value = result.data;
        itemGroup.value = itemGroupSource.value.map(
          (item: any) => item.item_group_id ?? item.item_group,
        );
        itemGroupIsSuccess.value = true;
      } else {
        itemGroupSource.value = [];
        itemGroupIsSuccess.value = true;
      }
    } catch {
      console.error("ItemGroup 조회 오류");
      itemGroupIsSuccess.value = false;
    }
  };

  const loadRegionData = async () => {
    if (!planVer.value) return;
    try {
      const result = await fetchRegions(planVer.value);
      if (result?.data?.length) {
        regionSource.value = result.data.map((item: any) => {
          if (!item) {
            return {
              id: item,
              text: t("고객 미지정"),
              value: item,
            };
          }
          return { id: item, text: item, value: item };
        });
        region.value = regionSource.value.map((item: any) => item.value);
        regionIsSuccess.value = true;
      } else {
        regionSource.value = [];
        regionIsSuccess.value = true;
      }
    } catch {
      console.error("Region 조회 오류");
      regionIsSuccess.value = false;
    }
  };

  const loadDemandTypeData = async () => {
    if (!planVer.value) return;
    try {
      const result = await fetchDemandTypes(planVer.value);
      if (result?.data?.length) {
        demandTypeSource.value = result.data.map((item: any) => ({
          value: item,
        }));
        demandType.value = demandTypeSource.value.map(
          (item: any) => item.value,
        );
        demandTypeIsSuccess.value = true;
      } else {
        demandTypeSource.value = [];
        demandTypeIsSuccess.value = true;
      }
    } catch {
      console.error("DemandType 조회 오류");
      demandTypeIsSuccess.value = false;
    }
  };

  // 특정 PlanCycle의 planVer GET — 원본: apiCall({ url: 'PlmPlanExecute', method: 'GET' })
  const loadPlanVerInfo = async () => {
    try {
      const result = await fetchPlanVerInfo();
      if (result && result.data?.length) {
        planVerSource.value = result.data;
        targetPlanVerData.value = result.data.filter(
          (item: any) => item.planVer === planVer.value,
        );

        if (targetPlanVerData.value.length) {
          const scenario = scenarioList.value.find(
            (item: any) =>
              item.scenarioID === targetPlanVerData.value[0].scenarioID,
          );
          reExecuteState.value.scenarioID = scenario?.scenarioID ?? null;

          const inbound =
            inboundSource.value.find(
              (item: any) =>
                item.inboundScenarioID ===
                targetPlanVerData.value[0].inboundScenarioID,
            ) || initNoExecution();
          reExecuteState.value.inboundScenarioID = inbound.inboundScenarioID;
        }
      } else {
        planVerSource.value = [];
        targetPlanVerData.value = {};
      }
    } catch {
      console.error("PlanVerInfo 조회 오류");
    }
  };

  onMounted(async () => {
    await loadExecutionFlows();
    await loadPlanCycleInfo();
    await loadOperGroupSource({
      plan_ver: planVer.value,
      schema_name: "OperGroupMaster",
    });
    await loadOperSource({
      plan_ver: planVer.value,
      schema_name: "OperMaster",
    });
    await loadBufferSource({
      plan_ver: planVer.value,
      schema_name: "BufferMaster",
    });
    await loadDemandVer({
      planCycleID: reExecuteState.value.planCycleID,
    });
    await loadScenarioList();
    await loadInbound();
    await loadDemandSource({
      plan_ver: planVer.value,
      schema_name: "Demand",
    });
    await loadScenarioModules({
      scenarioID: reExecuteState.value.scenarioID ?? "",
    });
    await loadPlanVerInfo();

    await Promise.all([
      loadCustData(),
      loadItemGroupData(),
      loadRegionData(),
      loadDemandTypeData(),
    ]);
  });

  watch(planVer, async (newValue) => {
    if (newValue) {
      // plan cycle 정보 먼저 확보 → planCycleID 세팅되어야 demandVer도 조회 가능
      await loadPlanCycleInfo();
      await loadDemandVer({
        planCycleID: reExecuteState.value.planCycleID,
      });
      await loadOperGroupSource({
        plan_ver: planVer.value,
        schema_name: "OperGroupMaster",
      });
      await loadOperSource({
        plan_ver: planVer.value,
        schema_name: "OperMaster",
      });
      await loadBufferSource({
        plan_ver: planVer.value,
        schema_name: "BufferMaster",
      });
      await Promise.all([
        loadCustData(),
        loadItemGroupData(),
        loadRegionData(),
        loadDemandTypeData(),
      ]);
    }
  });

  // 팝업 오픈 시: 선택 플로우에 해당하는 engine config / module / inbound tree 재조회.
  //   원본(ExecutionFlowMasterDetailSummary) 은 팝업 sub 컴포넌트 마운트 시 immediate watch 로
  //   호출되는데, 우리는 composable 스코프에서 watch 해서 ID 가 이미 onMounted 때 세팅되면
  //   watch 가 다시 발사되지 않아 팝업 열 때 상세가 비어있었다.
  const resolveActiveInboundID = () => {
    if (isAdvancedOption.value) {
      return reExecuteState.value.inboundScenarioID ?? "";
    }
    const flow = executionFlowSource.value.find(
      (f) => f.execution_flow_id === reExecuteState.value.executionFlowID,
    ) as any;
    return flow?.inbound_scenario_id ?? "";
  };
  const resolveActiveScenarioID = () => {
    if (isAdvancedOption.value) {
      return reExecuteState.value.scenarioID ?? "";
    }
    const flow = executionFlowSource.value.find(
      (f) => f.execution_flow_id === reExecuteState.value.executionFlowID,
    ) as any;
    return flow?.engine_scenario_id ?? flow?.scenario_id ?? "";
  };

  const reloadExecutionFlowDetail = async () => {
    const scenarioID = resolveActiveScenarioID();
    const inboundID = resolveActiveInboundID();
    await Promise.all([
      scenarioID
        ? (async () => {
            await loadScenarioConfig(scenarioID);
            await loadScenarioModules({ scenarioID });
          })()
        : Promise.resolve().then(() => {
            scenarioConfigSource.value = [];
            scenarioModuleDataSource.value = [];
          }),
      loadInboundItemOptions(inboundID),
    ]);
  };

  watch(isOpen, async (newVal) => {
    if (newVal) {
      await loadNewDemandVer({
        demand_ver:
          demandVerSource.value[demandVerSource.value.length - 1]?.demand_ver,
      });
      // 팝업 오픈 시점에 현재 선택된 flow 기준으로 3탭 상세 재조회
      await reloadExecutionFlowDetail();
    }
  });

  // 선택 플로우/모드 변경에도 상세 재조회 (simple↔advanced 토글 포함)
  watch(
    [
      () => reExecuteState.value.executionFlowID,
      () => isAdvancedOption.value,
    ],
    async () => {
      if (isOpen.value) {
        await reloadExecutionFlowDetail();
      }
    },
  );

  watch(
    () => reExecuteState.value.scenarioID,
    async (newVal) => {
      if (newVal) {
        await loadScenarioConfig();
        await loadScenarioModules({ scenarioID: newVal ?? "" });
      }
    },
  );

  return {
    isAdvancedOption,
    executionFlowSource,

    // 조회조건
    summarySource,
    summaryType,
    custSource,
    custParam,
    itemGroupSource,
    itemGroup,
    regionSource,
    region,
    demandTypeSource,
    demandType,
    qtyUOMSource,
    uomType,

    custIsSuccess,
    itemGroupIsSuccess,
    regionIsSuccess,
    demandTypeIsSuccess,

    // api 호출
    mainQueryIsPending,
    isPivotRendering,
    onLoad,
    loadParams,
    isPageFetching,

    // 계획 재실행 메뉴
    demandSource,
    selectedDemandList,
    pivotDataSource,
    fullDataSource,
    actStartDate,
    actEndDate,

    // 시나리오
    scenarioList,
    scenarioConfigSource,
    loadScenarioConfig,

    // 공유 CollectionView 관련
    sharedCollectionView,
    initializeSharedCollectionView,
    sharedDataSource,
    popupCollectionView,
    initializePopupCollectionView,
    applyPopupFilter,
    applyPopupGridFilter,
    popupDataSource,

    // 그리드 참조 공유
    mainGrid,
    popupGrid,

    // ExtendGrid 인스턴스 공유
    mainExtendGrid,
    popupExtendGrid,
    updateTrigger,

    // 계획 재실행 Pop 기능
    isOpen,
    toggle,
    open,
    close,

    // Step1
    currentStep,
    showEditedData,
    editedDemandSource,
    alwaysEditedData,
    reExecuteState,
    loadExecutionFlows,

    // 최신 planCycle 정보
    currentPlanCycleSource,

    // demandVer 정보
    demandVerSource,
    demandSetText,

    // inbound
    inboundSource,

    // widget 설정
    initWidgetSetting,
    viewPointSource,
    breakdownSource,
    widgetSummarySource,
    viewPointWidget,
    breakdownWidget,

    loadDemandSource,
    getDemandSourceIsPending,

    reExecutePlanMutation,
    scenarioModuleDataSource,
    phaseColumns,
    inboundItemOptions,

    checkDemandVerValid,
    isDuplicated,

    loadNewDemandVer,
    autoDemandVer,

    breakdownSearchSource,
    breakdownValue,

    operGroupSource,
    operGroups,
    operSource,
    opers,
    bufferSource,
    buffers,

    getOperGroupSourceIsSuccess,
    getOperSourceIsSuccess,
    getBufferSourceIsSuccess,
    loadOperGroupSource,
    loadOperSource,
    loadBufferSource,

    verInfoIsOpen,
    openVerInfo,
    closeVerInfo,

    // propColumns
    propColumns,
  };
};

export type IReExecutePlanQuery = ReturnType<typeof useReExecutePlanQuery>;
