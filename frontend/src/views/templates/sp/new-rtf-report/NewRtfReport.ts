import {
  AggregateType,
  QtyUOMType,
  SummaryType,
  useAggTypeQuery,
  useCustInRtfQuery,
  useGetDemandTypesQuery,
  useGetRegionsQuery,
  useItemGroupInRtfQuery,
  useQtyUomQuery,
  useSummaryQuery,
} from './adapters/query';
import { apiCall } from './adapters/stores';
import { useProjectInfoStore } from './adapters/stores';
import { useLoaderParams, useProp } from './adapters/utils';
import { useSearchParam } from './adapters/utils';
import { showMessage } from '@moz-shared/utils';
import { useMutation, useQuery } from '@tanstack/vue-query';
import { debounce } from 'es-toolkit';
import { useTranslation } from 'i18next-vue';
import { computed, onBeforeMount, onMounted, Ref, ref } from 'vue';

export const useRtfReportQuery = (planVer: Ref<string>, planCycleID: Ref<string>, fromDate: any, toDate: any) => {
  const { t } = useTranslation();

  const demandID = ref('');

  /** @todo vue 3.5 업데이트하면 useTemplateRef으로 리팩토링 */
  const refSub1 = ref();
  /** @todo vue 3.5 업데이트하면 useTemplateRef으로 리팩토링 */
  const refSub2 = ref();
  /** @todo vue 3.5 업데이트하면 useTemplateRef으로 리팩토링 */
  const refSub3 = ref();

  const projectInfoStore = useProjectInfoStore();
  const userID = computed(() => projectInfoStore.userInfo?.id || '');

  const openItemInfo = ref<boolean>(false);
  const openDemandInfo = ref<boolean>(false);
  const openBomMapView = ref<boolean>(false);
  const currentWidgetSetting = ref<any>();

  const { custParam, custSource } = useCustInRtfQuery(planVer);
  const { itemGroup, itemGroupSource } = useItemGroupInRtfQuery(planVer);
  const { region, regionSource } = useGetRegionsQuery(planVer);
  const { demandType, demandTypeSource } = useGetDemandTypesQuery(planVer);

  const selectedItem = ref<{
    due: '[TOTAL]' | '[SUB TOTAL]' | `${number}-${number}`;
    custID: string;
    itemGroupID: string;
    demandType: string;
    region: string;
  }>({
    due: '[TOTAL]',
    custID: '',
    itemGroupID: '',
    demandType: '',
    region: '',
  });

  const projectModule = useProjectInfoStore();
  const { onLoadHeader, propColumns, propColumnsModule } = useProp(planVer, 'RtfReport');

  const { uomType, qtyUOMSource } = useQtyUomQuery(['DEFAULT', 'CONVERSION'], 'DEFAULT', {
    menuID: 'rtfReportUomType',
  });
  const { aggType, aggTypeSource, isAggFetching } = useAggTypeQuery(planVer, ['WEEK', 'MONTH'], {
    defaultValue: 'MONTH',
  });
  const { prodStatus, prodStatusSource } = useProdStatusTypeQuery(['default', 'on_time', 'late', 'short'], 'default');

  const widgetSummarySource = ref<any[]>([
    { label: t('text-upper-item_group'), value: 'itemGroup' },
    { label: t('text-upper-customer'), value: 'cust' },
    { label: t('text-upper-demand_type'), value: 'demandType' },
    { label: t('text-due'), value: 'due' },
  ]);

  const { summarySource, summaryType } = useSummaryQuery(['itemGroup', 'cust', 'region', 'demandType'], 'itemGroup');

  onMounted(async () => {
    // await getRtfWidgetValue.mutateAsync();
    await getRtfSummaryQuery.mutateAsync();
  });

  const RAR_RTF_REPORT = 'RarRtfReport' as const;
  const mainApiKey = `${RAR_RTF_REPORT}/Main2` as const;
  const detailApiKey = `${RAR_RTF_REPORT}/Detail2` as const;
  const shortApiKey = `${RAR_RTF_REPORT}/Short` as const;
  const planByProdDetailApiKey = `RarPlanByProd/Detail2` as const;
  const showTargetPlanView = ref<boolean>(false);
  const isZoomedDetail = ref<boolean>(false);

  const planByProdDetailStandardSource = ref<
    { key: 'BUFFER' | 'OPER' | 'OPERGROUP'; value: 'BUFFER' | 'OPER' | 'OPERGROUP'; label: string }[]
  >([
    { key: 'BUFFER', value: 'BUFFER', label: t('text-isu_by_buffer') },
    { key: 'OPERGROUP', value: 'OPERGROUP', label: t('text-isu_by_oper_group') },
    { key: 'OPER', value: 'OPER', label: t('text-isu_by_oper') },
  ]);

  type MainPayloadType = {
    planVer: string;
    aggregateType: AggregateType;
    summary: 'due' | 'cust' | 'itemGroup' | 'region' | 'demandType';
    customers?: any[];
    itemGroupIDs?: any[];
    regions?: any[];
    prodStatus?: prodStatusType;
    demandTypes?: any[];
  };

  const {
    loadParams: mainLoadParams,
    queryKey: mainQueryKey,
    saveParams: saveMainParams,
  } = useLoaderParams(() => [
    mainApiKey,
    {
      planVer: planVer.value,
      aggregateType: aggType.value,
      prodStatus: prodStatus.value,
      summary: summaryType.value as 'due' | 'cust' | 'itemGroup' | 'region' | 'demandType',
      ...(summaryType.value === 'cust' && { customers: Array.from(new Set([...custParam.value])) }),
      ...(summaryType.value === 'itemGroup' && { itemGroupIDs: itemGroup.value }),
      ...(summaryType.value === 'region' && { regions: region.value }),
      ...(summaryType.value === 'demandType' && { demandTypes: demandType.value }),
      uomType: uomType.value,
      /** 아래는 클라이언트만 사용하는 상태 */
      planCycleID: planCycleID.value,
    } satisfies MainPayloadType & { planCycleID: string; uomType: QtyUOMType },
  ]);
  const mainQuery = useQuery({
    queryKey: mainQueryKey,
    queryFn: () => {
      if (!planVer.value) return null;
      return apiCall({
        url: mainApiKey,
        param: mainLoadParams.value,
        method: 'POST',
      });
    },
    select: (response) => response?.data,
  });

  const selectedCustomers = computed(() => {
    if (selectedItem.value?.custID === '[TOTAL]') {
      return mainLoadParams.value?.customers ? [...mainLoadParams.value?.customers] : [];
    }
    return [selectedItem.value?.custID];
  });

  const selectedItemGroupIDs = computed(() => {
    if (selectedItem.value?.itemGroupID === '[TOTAL]') {
      return mainLoadParams.value?.itemGroupIDs ? [...mainLoadParams.value?.itemGroupIDs] : [];
    }
    return [selectedItem.value?.itemGroupID];
  });

  const selectedDemandType = computed(() => {
    if (selectedItem.value?.demandType === '[TOTAL]') {
      return mainLoadParams.value?.demandTypes ? [...mainLoadParams.value?.demandTypes] : [];
    }
    return [selectedItem.value?.demandType];
  });

  const selectedProductionArea = computed(() => {
    if (!selectedItem.value?.region || selectedItem.value.region === '[TOTAL]') {
      return '';
    }
    return selectedItem.value.region;
  });

  const selectedDue = computed(() => {
    let restoredDate: { year: string; month: string } | { year: string; week: string } | null = null;

    switch (selectedItem.value?.due) {
      case '[SUB TOTAL]':
        return '[SUB TOTAL]';
      case '[TOTAL]':
        return '[TOTAL]';
      default:
        switch (mainLoadParams.value.aggregateType) {
          case 'MONTH':
            // 2024-11
            restoredDate = projectModule.restoreDate('dateMonth', selectedItem.value?.due)! as any;
            return `${restoredDate!.year}-${(restoredDate as any).month}`;
          case 'WEEK':
            // 2024-48
            restoredDate = projectModule.restoreDate('dateWeek', selectedItem.value?.due)! as any;
            return `${restoredDate!.year}-${(restoredDate as any).week}`;
          default:
            return '[TOTAL]';
        }
    }
  });

  type DetailPayloadType = {
    planVer: string;
    aggregateType: AggregateType;
    summary: SummaryType;
    dueMonth?: string;
    dueWeek?: string;
    customers?: any[];
    itemGroupIDs?: any[];
    productionArea?: string;
    prodStatus?: prodStatusType;
    uomType: QtyUOMType;
  };

  const {
    loadParams: detailLoadParams,
    queryKey: detailQueryKey,
    saveParams: saveDetailParams,
  } = useLoaderParams(() => [
    detailApiKey,
    {
      planVer: mainLoadParams.value.planVer,
      aggregateType: mainLoadParams.value.aggregateType,
      uomType: mainLoadParams.value.uomType,
      prodStatus: mainLoadParams.value.prodStatus,

      ...(mainLoadParams.value.aggregateType === 'MONTH' && { dueMonth: selectedDue.value }),
      ...(mainLoadParams.value.aggregateType === 'WEEK' && { dueWeek: selectedDue.value }),

      summary: mainLoadParams.value.summary,

      ...(mainLoadParams.value.summary === 'cust' && {
        customers: selectedCustomers.value,
      }),
      ...(mainLoadParams.value.summary === 'itemGroup' && {
        itemGroupIDs: selectedItemGroupIDs.value,
      }),
      ...(mainLoadParams.value.summary === 'demandType' && {
        demandTypes: selectedDemandType.value,
      }),
      ...(mainLoadParams.value.summary === 'region' && {
        productionArea: selectedProductionArea.value,
      }),
    } satisfies DetailPayloadType,
  ]);
  const detailQuery = useQuery({
    queryKey: detailQueryKey,
    queryFn: () => {
      if (!mainLoadParams.value?.planVer) return null;

      return apiCall({
        url: detailApiKey,
        param: detailLoadParams.value,
        method: 'POST',
      });
    },
    select: (response) => response?.data,
  });

  const {
    loadParams: shortLoadParams,
    queryKey: shortQueryKey,
    // saveParams: saveShortParams,
  } = useLoaderParams(() => [
    shortApiKey,
    { planVer: mainLoadParams.value?.planVer, demandID: demandID.value, uomType: detailLoadParams.value.uomType },
  ]);

  const shortQuery = useQuery({
    queryKey: computed(() => [`${RAR_RTF_REPORT}/Short`, demandID.value]),
    queryFn: () => {
      if (!planVer.value || !demandID.value) return null;
      return apiCall({
        url: shortApiKey,
        param: { planVer: planVer.value, demandID: demandID.value },
        method: 'POST',
      });
    },
    select: (response) => response?.data,
    enabled: true,
  });

  const bufferPlanTargetApiKey = 'RarPlanByProd/GetBufferPlanTarget' as const;

  const {
    loadParams: bufferPlanTargetLoadParams,
    queryKey: bufferPlanTargetQueryKey,
    // saveParams: savebufferPlanTargetParams,
  } = useLoaderParams(() => [
    bufferPlanTargetApiKey,
    { planVer: mainLoadParams.value?.planVer, demandID: demandID.value },
  ]);

  const bufferPlanTargetQuery = useQuery({
    queryKey: computed(() => [`${bufferPlanTargetApiKey}`, demandID.value, showTargetPlanView.value]),
    queryFn: () => {
      if (!planVer.value || !demandID.value) return null;
      return apiCall({
        url: bufferPlanTargetApiKey,
        param: { planVer: planVer.value, demandID: demandID.value },
        method: 'POST',
      });
    },
    select: (response) => response?.data,
    enabled: computed(() => showTargetPlanView.value),
  });

  const onLoad = debounce(async () => {
    // sub2 초기화
    selectedItem.value = { due: '[TOTAL]', custID: '', itemGroupID: '', demandType: '', region: '' };
    refSub2.value?.resetDetailDataSource();

    // sub1 로드
    refSub1.value?.onLoad();
  }, 100);

  const planByProdSummaryApiKey = `rarPlanByProd/DemandSummary` as const;

  const {
    loadParams: summaryLoadParams,
    queryKey: summaryQueryKey,
    // saveParams: saveSummaryParams,
  } = useLoaderParams(() => [
    planByProdSummaryApiKey,
    { planVer: mainLoadParams.value?.planVer, demandID: [demandID.value] },
  ]);

  const getPlanByProdSummaryQuery = useQuery({
    queryKey: summaryQueryKey,
    queryFn: () => {
      if (!planVer.value || !demandID.value) return null;
      return apiCall({
        url: planByProdSummaryApiKey,
        param: { planVer: mainLoadParams.value?.planVer, demandIDs: [demandID.value] },
        method: 'POST',
      });
    },
    select: (response) => response?.data,
    enabled: true,
  });

  const {
    loadParams: prodDetailLoadParams,
    queryKey: prodDetailQueryKey,
    // saveParams: saveProdDetailParams,
  } = useLoaderParams(() => [
    planByProdDetailApiKey,
    { planVer: mainLoadParams.value?.planVer, demandID: demandID.value, uomType: mainLoadParams.value.uomType },
  ]);

  const getPlanByProdDetailQuery = useQuery({
    queryKey: prodDetailQueryKey,
    queryFn: () => {
      if (!planVer.value || !demandID.value) return [];
      return apiCall({
        url: planByProdDetailApiKey,
        param: {
          planVer: mainLoadParams.value?.planVer,
          demandID: demandID.value,
          uomType: mainLoadParams.value.uomType,
        },
        method: 'POST',
      });
    },
    select: (response) => response?.data,
    enabled: computed(() => !!demandID.value),
  });

  const showPegInfoDetail = ref<boolean>(false);

  const demandInfoQuery = useQuery({
    queryKey: computed(() => [`RarPeggingReport/DemandInfo`, demandID.value]),
    queryFn: () =>
      apiCall({
        url: 'RarPeggingReport/DemandInfo',
        param: { planVer: mainLoadParams.value?.planVer, demandID: demandID.value },
        method: 'POST',
      }),
    select: (response) => (response ? response.data : null),
    enabled: true,
  });

  const pegInfoDetailQuery = useQuery({
    queryKey: computed(() => [`RarPeggingReport/PegInfoDetail`, demandID.value]),
    queryFn: () =>
      apiCall({
        url: 'RarPeggingReport/PegInfoDetail',
        param: { planVer: mainLoadParams.value?.planVer, demandID: demandID.value },
        method: 'POST',
      }),
    select: (response) => (response ? response.data : null),
    enabled: true,
  });

  // bom map popup
  const showBomMapView = ref<boolean>(false);

  const apiKey = 'RarBomMapViewNew' as const;
  useLoaderParams(() => [
    apiKey,
    {
      planVer: planVer.value,
      demandID: demandID?.value,
    },
  ]);

  const { loadParams: planCycleParams } = useLoaderParams(() => [
    apiKey,
    {
      /** 아래 3가지 키와 값은 클라이언트만 사용 */
      fromDate: fromDate.value?.format('YYYY-MM-DD'),
      toDate: toDate.value?.format('YYYY-MM-DD'),
      planCycleID: planCycleID.value,
    },
  ]);

  const bomNetworkQuery = useQuery({
    queryKey: computed(() => [`RarBomMapViewNew`, demandID.value]),
    queryFn: () =>
      apiCall({
        url: apiKey,
        param: {
          planVer: mainLoadParams.value?.planVer,
          demandID: demandID.value,
          onlyTargetBom: true,
          uomType: mainLoadParams.value.uomType,
        },
        method: 'POST',
      }),
    select: (response) => (response ? response.data : null),
    enabled: true,
  });

  // item Detail query
  const detailItemId = ref<string>();
  const itemDetailQueryKey = computed(() => ['RarPlanByRes/GetProps', detailItemId.value]);
  const itemDetailQuery = useQuery({
    queryKey: itemDetailQueryKey,
    queryFn: () =>
      apiCall({
        url: 'RarPlanByRes/GetProps',
        param: { planVer: planVer.value, itemID: detailItemId.value },
        method: 'POST',
      }),
    select: (response) => response?.data,
    enabled: true,
  });

  const dewmandDetailQueryKey = computed(() => ['RarPlanByRes/GetProps', demandID.value]);
  const demandDetailQuery = useQuery({
    queryKey: dewmandDetailQueryKey,
    queryFn: () =>
      apiCall({
        url: 'odlReport',
        param: { planVer: planVer.value, schema_name: 'Demand', demandID: demandID.value },
        method: 'POST',
      }),
    select: (response) => response?.data,
    enabled: true,
  });

  const getWidgetValueIsPending = computed(() => getRtfSummaryQuery.isPending.value);

  // const defaultSource = [
  //   { label: t('text-upper-item_group'), value: 'itemGroup' },
  //   { label: t('text-upper-customer'), value: 'cust' },
  //   { label: t('text-upper-demand_type'), value: 'demandType' },
  //   { label: t('text-upper-period'), value: 'period' },
  // ] as const;

  const originWidgetSetting = ref<any>([]);

  const getRtfSummaryQuery = useMutation({
    mutationFn: () =>
      apiCall({
        url: 'PlanDashboard/GetRTFSummaryPopup',
        param: { userID: userID.value, planVer: planVer.value },
        method: 'POST',
      }),
    onSuccess: async (result) => {
      if (result && result.data) {
        currentWidgetSetting.value = structuredClone(result.data);
        originWidgetSetting.value = structuredClone(result.data);

        // if (result.data?.summaryTypes) {
        //   const trueKeys = Object.keys(result.data.summaryTypes).filter((key) => result.data.summaryTypes[key]);
        //   summarySource.value = defaultSource.filter((item: any) => trueKeys.includes(item.value)) as any;
        //   const hasValue = ref<boolean>(false);

        //   summarySource.value.forEach((item: any) => {
        //     if (item.value === summaryType.value) {
        //       hasValue.value = true;
        //     }
        //   });

        //   if (!hasValue.value) {
        //     summaryType.value = summarySource.value[0].value;
        //     await onLoad();
        //   }
        // }
      } else showMessage(t('msg-toast-save_error'), false);
    },
    onError: () => {
      showMessage(t('msg-toast-save_error'), false);
    },
  });

  // const getRtfWidgetValue = useMutation({
  //   mutationFn: async () => await apiCall(`RarRtfReport/GetWidget`, {}, 'POST'),
  //   onSuccess: async (result) => {
  //     if (result && result.data) {
  //       currentWidgetSetting.value = {
  //         summaryTypes: result.data?.summaryTypes,
  //         detailType: result.data?.detailType,
  //       };

  //       // API 호출 후 summarySource update
  //       if (result.data?.summaryTypes) {
  //         // const defaultSource = [
  //         //   { label: t('text-upper-item_group'), value: 'itemGroup' },
  //         //   { label: t('text-upper-customer'), value: 'cust' },
  //         //   { label: t('text-upper-region'), value: 'region' },
  //         //   { label: t('text-upper-demand_type'), value: 'demandType' },
  //         //   { label: t('text-upper-period'), value: 'period' },
  //         // ] as const;

  //         const trueKeys = Object.keys(result.data.summaryTypes).filter((key) => result.data.summaryTypes[key]);

  //         summarySource.value = defaultSource.filter((item: any) => trueKeys.includes(item.value)) as any;

  //         const hasValue = ref<boolean>(false);

  //         summarySource.value.forEach((item: any) => {
  //           if (item.value === summaryType.value) {
  //             hasValue.value = true;
  //           }
  //         });

  //         if (!hasValue.value) {
  //           summaryType.value = summarySource.value[0].value;
  //           await onLoad();
  //         }
  //       }
  //     } else {
  //       currentWidgetSetting.value = {
  //         summaryTypes: {
  //           period: false,
  //           cust: false,
  //           itemGroup: false,
  //           region: false,
  //           demandType: false,
  //         },
  //         detailType: 'BUFFER',
  //       };

  //       summarySource.value = defaultSource as any;
  //     }
  //   },
  //   onError: () => {
  //     showMessage(t(`getError`), false);
  //   },
  // });

  const saveRtfWidgetValue = useMutation({
    mutationFn: async (param: any) =>
      await apiCall({
        url: 'PlanDashboard/SaveWidgetValue',
        param,
        method: 'POST',
      }),
    onSuccess: async (result) => {
      if (result) {
        showMessage(t('msg-toast-save_success'), true);
        // await getRtfWidgetValue.mutateAsync();
        await getRtfSummaryQuery.mutateAsync();
      } else {
        showMessage(t('msg-toast-save_error'), false);
      }
    },
    onError: () => {
      showMessage(t('msg-toast-save_error'), false);
    },
  });

  const isPageFetching = computed(
    () => mainQuery.isFetching.value || detailQuery.isFetching.value || getPlanByProdDetailQuery.isFetching.value,
  );

  return {
    planByProdDetailStandardSource,

    getRtfSummaryQuery,
    // getRtfWidgetValue,
    saveRtfWidgetValue,
    widgetSummarySource,
    getWidgetValueIsPending,
    currentWidgetSetting,
    originWidgetSetting,

    demandDetailQuery,
    itemDetailQuery,
    detailItemId,
    aggType,
    aggTypeSource,
    summaryType,
    summarySource,
    selectedItem,
    demandID,
    isPageFetching,
    uomType,
    qtyUOMSource,
    isAggFetching,

    mainApiKey,
    refSub1,
    mainQuery,
    mainQueryKey,
    mainLoadParams,
    saveMainParams,

    detailApiKey,
    refSub2,
    detailQuery,
    detailQueryKey,
    detailLoadParams,
    saveDetailParams,

    shortApiKey,
    refSub3,
    shortQuery,
    shortQueryKey,
    shortLoadParams,
    // saveShortParams,

    bufferPlanTargetQuery,
    bufferPlanTargetLoadParams,
    // savebufferPlanTargetParams,
    bufferPlanTargetQueryKey,

    getPlanByProdSummaryQuery,
    summaryLoadParams,
    // saveSummaryParams,

    getPlanByProdDetailQuery,
    planByProdDetailApiKey,
    prodDetailLoadParams,
    // saveProdDetailParams,

    demandInfoQuery,
    pegInfoDetailQuery,
    showPegInfoDetail,

    bomNetworkQuery,
    showBomMapView,
    planCycleParams,
    // savePlanCycleParams,

    showTargetPlanView,
    isZoomedDetail,

    propColumns,
    propColumnsModule,
    onLoadHeader,

    onLoad,
    custSource,
    custParam,
    itemGroup,
    itemGroupSource,

    region,
    regionSource,

    demandType,
    demandTypeSource,

    openItemInfo,
    openDemandInfo,
    openBomMapView,

    prodStatus,
    prodStatusSource,
  };
};

export type IRtfReportQuery = ReturnType<typeof useRtfReportQuery>;

// 새로운 조회 조건 추가를 위한 로직
export type prodStatusType = 'default' | 'on_time' | 'late' | 'short';
export type prodStatusSourceType = { label: string; value: prodStatusType };

export const useProdStatusTypeQuery = (source: prodStatusType[], defaultValue: prodStatusType) => {
  const { t } = useTranslation();
  const prodStatus = ref<prodStatusType>(defaultValue);
  const createSource = (types: prodStatusType[]): prodStatusSourceType[] => {
    const allTypes: prodStatusSourceType[] = [
      { label: t('text-short-prod'), value: 'short' },
      { label: t('text-late_production'), value: 'late' },
      { label: t('text-on_time_production'), value: 'on_time' },
      { label: t('text-total'), value: 'default' },
    ];
    return allTypes.filter((type) => types.includes(type.value));
  };
  const prodStatusSource = ref<prodStatusSourceType[]>(createSource(source));

  onBeforeMount(async () => {
    /** 현재 URL에서 qtyUOM이 있는지 상태를 먼저 확인 */

    useSearchParam({
      model: prodStatus,
      id: 'prodStatus',
      defaultValue: () => defaultValue,
      type: 'String',
    });
  });

  return {
    prodStatus,
    prodStatusSource,
    // isUomFetched,
  };
};
