<template>
  <MozGrid
    :name="t(`${currentMenu.menuName}-sub2-summary`)"
    :id="`${currentMenu.menuName}-sub2-summary-id`"
    class="moz-readonly-grid rtf-report-sub2"
    style="width: var(--parents-main-width); height: 100%"
    :coreConfig="detailCoreConfig"
    :contextMenuConfig="detailContextMenuConfig"
    :use-tool-box="true"
    :loading="detailQuery.isFetching.value || mainQuery.isFetching.value"
    @ready="onReady"
    @cell:click="onCellClick"
    @contextmenu="onContextMenu"
  >
    <CellTemplate field="showDetailCol">
      <span class="cs-link" @click="popup = true">{{ '상세 보기' }}</span>
    </CellTemplate>
  </MozGrid>

  <PlanByProdPop
    :showDetail="localState.showDetail"
    :planCycleID="mainLoadParams.planCycleID"
    :planVer="mainLoadParams.planVer"
    :data="{
      demandItemIDs: [localState.selectedItem?.itemID],
      customers: [localState.selectedItem?.custID],
      demandIDs: [localState.selectedItem?.demandID],
      demandQty: localState.selectedItem?.demandQty,
    }"
    :close="() => (localState.showDetail = false)"
    :auto-focus-props="{
      targetDemandID: localState.selectedItem?.demandID,
    }"
  />
  <Popup
    :width="popupWidth"
    :height="popupHeight"
    v-model:visible="popup"
    :title="t('text-short-reason-detail-view')"
    :onCancel="
      () => {
        popup = false;
      }
    "
    preset="close"
    :maxWidth="popupWidth"
    :maxHeight="popupHeight"
    :resizeable="true"
    :style="{
      minWidth: '650px',
      minHeight: '400px',
    }"
    :useVShow="false"
  >
    <div ref="container" class="bom-map-popup-container" v-loading="bomNetworkQuery.isFetching.value">
      <SplitPane horizontal style="max-width: 100%">
        <Pane size="70%" max-size="90%">
          <BomMapInterface
            v-if="!bomNetworkQuery.isFetching.value && bomNetworkInfos?.length"
            :bomNetworkInfos="bomNetworkInfos"
            :demandInfos="demandInfos"
            :shortLogs="shortLogs"
            :initKey="demandInfos?.item_id"
            :planCycleData="{
              planVer: mainLoadParams.planVer,
              planCycleID,
              fromDate: fromDate?.format('YYYY-MM-DD') ?? '',
              toDate: toDate?.format('YYYY-MM-DD') ?? '',
              projectID,
              demandID: demandID,
            }"
            :userID="userID"
          />
          <div v-else class="grid-empty">
            <EmptyState v-if="!bomNetworkQuery.isLoading.value" :is-read-only="true" />
          </div>
        </Pane>
        <Pane size="30%" max-size="90%">
          <div v-if="!bomNetworkQuery.isFetching.value && bomNetworkInfos?.length" class="grid-sort-reason">
            <MozGrid
              height="100%"
              class="moz-readonly-grid"
              :id="`${currentMenu.menuName}-sub2-short-info-modal-id`"
              :name="t(`${currentMenu.menuName}`) + '-sub2-short-info-modal'"
              :coreConfig="shortCoreConfig"
              :contextMenuConfig="{
                useViewSelectColumn: true,
                useExportExcel: true,
                useFilter: false,
                onExportOriginalData: () =>
                  downloadBigData({
                    column_map: COLUMN_MAP,
                    file_name: `${t(`${menuModule.currentMenu.menuName}`)}_${shortLoadParams.planVer}`,
                    data_method: 'POST',
                    data_parameter: JSON.stringify(shortLoadParams),
                    api_key: shortApiKey,
                  }),
              }"
              :use-tool-box="false"
              :emptyState="{
                contentMsg: '',
              }"
              :loading="shortQuery.isFetching.value"
            >
              <CellTemplate field="shortReason" #default="{ rowData }">
                <span
                  v-tooltip="{
                    text: t(`desc-${rowData?.shortType}-${rowData?.shortCategory}-${rowData?.shortReason}`),
                  }"
                  >{{
                    convertToInternationalization(String(rowData?.shortReason ?? ''), 'short', [
                      'LackOfResourceCapacity',
                      'LateReleaseLot',
                      'InvalidBuffer',
                      'InvalidCustomer',
                      'InvalidItem',
                      'InvalidSite',
                    ])
                  }}</span
                >
              </CellTemplate>
            </MozGrid>
          </div>
        </Pane>
      </SplitPane>
    </div>
  </Popup>
  <InfoModal key="main-info-modal">
    <!-- 제목 슬롯 -->
    <template #title>
      <span>{{ itemInfoHeaderText }}</span>
    </template>
    <!-- 컨텐츠 슬롯 -->
    <template #content>
      <div class="info-modal-content-wrapper">
        <MozGrid
          height="100%"
          :id="`${t(currentMenu.menuName)}-item-info-modal-id`"
          :name="`${t(currentMenu.menuName)}-item-info-modal-name`"
          :coreConfig="itemInfoCoreConfig"
          :emptyState="{
            contentMsg: '',
          }"
          :use-tool-box="true"
          :loading="itemDetailQuery.isFetching.value"
          :use-sort="true"
          :contextMenuConfig="{
            useViewSelectColumn: true,
            useBulkEditColumn: false,
            useExportExcel: false,
            useExportImport: currentMenu?.isWrite,
          }"
        />
      </div>
    </template>
  </InfoModal>

  <!-- 두 번째 InfoModal (수요 정보용) -->
  <InfoModal key="demand-info-modal" storeKey="useDemandInfoModal">
    <template #title>
      <span>{{ '수요 정보 상세 보기' }}</span>
    </template>
    <template #content>
      <div class="demand-modal-content-wrapper">
        <MozGrid
          height="100%"
          :id="`${t(currentMenu.menuName)}-demand-info-modal-id`"
          :name="`${t(currentMenu.menuName)}-demand-info-modal`"
          :coreConfig="demandInfoCoreConfig"
          :contextMenuConfig="{
            useViewSelectColumn: false,
            useBulkEditColumn: false,
            useExportExcel: false,
            useExportImport: false,
          }"
          :loading="false"
        />
        <!-- 수요 정보용 그리드나 다른 컨텐츠 -->
      </div>
    </template>
  </InfoModal>
</template>
<script setup lang="ts">
import { createOpenNewTabMenu, useGridContextTarget } from './components/gridContextMenu';
import { useInfoModalStore } from './components/InfoModal';
import InfoModal from './components/InfoModal.vue';
import { downloadBigData, useMenuStore, usePlanCycleStore } from './adapters/stores';
import { useLoadStore, useProjectInfoStore } from './adapters/stores';
import { convertToInternationalization, ROW_KEY, withRowKey } from './adapters/utils';
import BomMapInterface from './components/bom-map/BomMapInterface.vue';
import { CellTemplate, MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { GridChrome, IContextMenuConfig, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
import { EmptyState, Pane, Popup, SplitPane } from '@vmscloud/moz-ui-components-vue';
import { useExcelStore } from '@/shims/grid/store';
import { getWidthByKey } from '@/shims/grid/utils';
import { camelToSnake, showMessage } from '@moz-shared/utils';
import { useQueryClient } from '@tanstack/vue-query';
import { debounce } from 'es-toolkit';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import {
  computed,
  defineAsyncComponent,
  inject,
  nextTick,
  onBeforeUnmount,
  onMounted,
  provide,
  reactive,
  ref,
  shallowRef,
  toRaw,
  toRefs,
  watch,
  watchEffect,
} from 'vue';
import { IRtfReportQuery } from './NewRtfReport';

const PlanByProdPop = defineAsyncComponent(() => import('./components/PlanByProdPop.vue'));

/**
 * props
 */
interface Props {
  parentsMainWidth?: string;
  parentsMainHeight?: string;
}

const props = withDefaults(defineProps<Props>(), {});
const { parentsMainWidth, parentsMainHeight } = toRefs(props);
const planCycleStore = usePlanCycleStore();
const { demandVer, fromDate, toDate, planCycleID, planVer } = storeToRefs(planCycleStore as any);

/**
 * DEFINE DEFAULT VARIABLE
 */
const queryClient = useQueryClient();
const menuModule = useMenuStore();
const { currentMenu } = storeToRefs(menuModule);
const projectModule = useProjectInfoStore();
const { currentProjectID: projectID } = storeToRefs(projectModule);
const projectInfoStore = useProjectInfoStore();
const userID = computed(() => projectInfoStore.userInfo?.id || '');
const excelModule = useExcelStore();
const load = useLoadStore();
const useInfoModal = useInfoModalStore();
const useDemandInfoModal = useInfoModalStore();
provide('useInfoModal', useInfoModal);
provide('useDemandInfoModal', useDemandInfoModal);
const { modalOpen, open } = useInfoModal;
const { modalOpen: demandModalOpen, open: demandOpen } = useDemandInfoModal;

const {
  itemDetailQuery,
  detailItemId,
  demandID,
  detailQuery,
  detailQueryKey,
  refSub3,
  saveDetailParams,
  mainLoadParams,
  detailApiKey,
  detailLoadParams,
  onLoadHeader,
  propColumnsModule,
  propColumns,
  showBomMapView: popup,
  bomNetworkQuery,
  shortQuery,
  shortLoadParams,
  shortApiKey,
  mainQuery,
  openItemInfo,
  demandDetailQuery,
  openDemandInfo,
} = inject('useRtfReport') as IRtfReportQuery;

const { t } = useTranslation(); // 다국어

// 브라우저 크기 변화 감지용 반응형 변수
const windowWidth = ref(window.innerWidth);
const windowHeight = ref(window.innerHeight);

// 브라우저 크기 90%의 px 단위 숫자 반환
const popupWidth = computed(() => Math.floor(windowWidth.value * 0.8));
const popupHeight = computed(() => Math.floor(windowHeight.value * 0.9));

// window resize 이벤트 처리
const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
  windowHeight.value = window.innerHeight;
};

onMounted(() => {
  window.addEventListener('resize', updateWindowWidth);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateWindowWidth);
});

const grid = shallowRef<PureSheet | null>(null); // 코어 그리드
const localState: {
  showDetail: boolean;
  selectedItem: any;
} = reactive({
  showDetail: false,
  selectedItem: null,
});
const detailDataSource = shallowRef<any[]>([]);
const selectedCellPosition = ref<any>();
const { target: contextTarget, onContextMenu: onGridContextMenu } = useGridContextTarget();

/**
 * INITIALIZE
 */
onMounted(() => {
  resetSize();
});

// GRID INITIALIZE
const onReady = (pureSheet: PureSheet, _chrome: GridChrome) => {
  grid.value = pureSheet;
};

const onSelectionChanged = debounce((dataItem: any, cellElement?: HTMLElement | null) => {
  if (!dataItem) {
    demandID.value = '';
  } else {
    demandID.value = dataItem.demandID;
    detailItemId.value = dataItem.itemID;

    // 선택된 셀의 DOM 요소와 위치 정보 얻기
    if (cellElement) {
      selectedCellPosition.value = cellElement.getBoundingClientRect();
    }
  }

  refSub3.value?.onLoad();
}, 300);

const onCellClick = (payload: any) => {
  const cellElement = (payload?.event?.target as HTMLElement | undefined)?.closest?.('.ps-cell') as HTMLElement | null;
  onSelectionChanged(payload?.row, cellElement);
};

const onContextMenu = (payload: any) => {
  onGridContextMenu(payload);
  // 우클릭한 셀 기준으로 정보 모달을 띄운다 (옛 그리드는 우클릭 시 셀이 선택됐다)
  if (contextTarget.value.cell?.rect) {
    selectedCellPosition.value = contextTarget.value.cell.rect;
  }
};

const isHeaderTarget = () => contextTarget.value.cell?.area !== 'cell';

const openNewTabMenus = [
  createOpenNewTabMenu(
    'openProdPlanByOper',
    {
      route: (item: any) => {
        return {
          path: `/sp/ProdPlanByOper`,
          query: {
            planCycle: mainLoadParams.value.planCycleID,
            planVer: mainLoadParams.value.planVer,
            fromDate: fromDate.value?.format('YYYY-MM-DD') ?? '',
            toDate: toDate.value?.format('YYYY-MM-DD') ?? '',
            [`buffer[A]`]: 'All',
            [`itemGroup[+]`]: `${[item?.itemGroupID]}`,
            [`item[+]`]: `${[item?.itemID]}`,
          },
        };
      },
      disabled: (item: any) => {
        return !(item?.itemID || item?.itemGroup);
      },
      label: t('text-context-open_prod_plan_by_oper'),
    },
    () => contextTarget.value,
  ),
  createOpenNewTabMenu(
    'openDemand',
    {
      route: (item: any) => {
        return {
          path: `/dm/Demand`,
          query: {
            planCycle: mainLoadParams.value.planCycleID,
            planVer: mainLoadParams.value.planVer,
            [`item[+]`]: `${[item?.itemID]}`,
            [`demandVer[+]`]: `${[demandVer.value]}`,
          },
        };
      },
      disabled: (item: any) => {
        return !item?.itemID;
      },
      label: t('text-context-open_demand'),
    },
    () => contextTarget.value,
  ),
  createOpenNewTabMenu(
    'openBomMapPlanView',
    {
      route: (item: any) => {
        return {
          path: `/sp/BomMapPlanView`,
          query: {
            planCycle: mainLoadParams.value.planCycleID,
            planVer: mainLoadParams.value.planVer,
            demandItemID: item?.itemID,
            demandID: item?.demandID,
          },
        };
      },
      disabled: (item: any) => {
        return !(item?.demandItemID || item?.itemID || item?.demandID);
      },
      label: t('text-context-open_bom_map_plan_view'),
    },
    () => contextTarget.value,
  ),
  createOpenNewTabMenu(
    'openFgsStockInPlan',
    {
      route: (item: any) => {
        return {
          path: `/sp/FgsStockInPlan`,
          query: {
            planCycle: mainLoadParams.value.planCycleID,
            planVer: mainLoadParams.value.planVer,
            fromDate: fromDate.value?.format('YYYY-MM-DD') ?? '',
            toDate: toDate.value?.format('YYYY-MM-DD') ?? '',
            [`item[+]`]: item?.itemID,
            [`itemGroup[+]`]: `${[item?.itemGroupID]}`,
          },
        };
      },
      disabled: (item: any) => {
        return !(item?.demandItemID || item?.itemID || item?.demandID);
      },
      label: t('text-context-open_fgs_prod_plan'),
    },
    () => contextTarget.value,
  ),
];

const detailContextMenuConfig = computed<IContextMenuConfig>(() => ({
  useFilter: true,
  useExportExcel: true,
  customMenu: [
    {
      id: 'openView',
      label: t(`text-view-item-additional-prop`),
      handler: () => {
        if (isHeaderTarget()) return;
        if (!open.value && selectedCellPosition.value) {
          modalOpen(
            selectedCellPosition.value.left,
            selectedCellPosition.value.top + selectedCellPosition.value.height + 5,
          );
        }
      },
    },
    {
      id: 'openDemandInfo',
      label: t('text-open-demand-info-detail-view'),
      handler: () => {
        if (isHeaderTarget()) return;
        if (!demandOpen.value && selectedCellPosition.value) {
          demandModalOpen(
            selectedCellPosition.value.left,
            selectedCellPosition.value.top + selectedCellPosition.value.height + 5,
          );
        }
      },
    },
    { id: 'sep-open-view', label: '', separator: true },
    ...openNewTabMenus,
  ],
  onExportOriginalData: () =>
    downloadBigData({
      /**
       * @todo 백엔드 API 스네이크 케이스로 받고 변환처리하는 로직 제거
       * 서버에서 받는 케이스가 안 맞아서 `createColumnMapForExport(coreConfig.fields)`로 처리 불가능 함
       */
      column_map: camelToSnake(
        propColumnsModule.parseExcel(
          // 현재 표시 중인 컬럼만 내보내도록 런타임 컬럼 상태(visible)를 넘긴다
          excelModule.createColumnMapForExport(grid.value?.columns.getAll() ?? detailCoreConfig.value.fields),
        ),
      ),
      file_name: `${t(`${menuModule.currentMenu.menuName}`)}_${detailLoadParams.value.planVer}`,
      data_method: 'POST',
      data_parameter: JSON.stringify(detailLoadParams.value),
      api_key: detailApiKey,
    }),
}));

/**
 * @description 하나의 tick 사이클에서 처리되어야 함. 전체 목록을 기록하는 과정이 있어야 prop 컬럼들에 대해서 채번이 가능해짐.
 * 갱신에 반응함. 그래서 고정된 문자열 배열로 처리해야 함.
 */
const propHeaders = computed(() => {
  const result: string[] = [
    t('text-demand_id'),
    t('text-cust_name'),
    t('text-on_time_ratio'),
    t('text-late_ratio'),
    t('text-rtf_ratio'),
    t('text-item_group'),
    t('text-item_id'),
    t('text-item_name'),
    t('text-due_week'),
    t('text-due_date'),
    t('text-demand_qty'),
    t('text-on_time_qty'),
    t('text-late_qty'),
    t('text-rtf_qty'),
    t('text-short_qty'),
    t('text-qty_uom'),
    t('text-demand_type'),
    t('text-item_type'),
    t('text-prod_type'),
    t('text-item_size_type'),
    t('text-item_spec'),
  ];

  // prop 컬럼이 아닌 일반 컬럼의 header (갱신 시 기존 prop 컬럼 제외)
  const existingHeaders = [...result, t('text-simple_short_reason')];

  propColumns.value.forEach((prop) => {
    // 정규식 특수문자 이스케이프
    const escapedHeader = prop.header.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // 정확히 일치하거나 "헤더명 숫자" 형식만 매칭 (^시작, $끝으로 부분 매칭 방지)
    const exactPattern = new RegExp(`^${escapedHeader}(\\s\\d+)?$`);

    /**
     * 그리드의 컬럼 header(prop 제외)와 앞으로 붙일 배열(result) 전체를 확인하고 채번을 한다.
     */
    const duplicatedHeaders = existingHeaders.concat(result).filter((header) => exactPattern.test(header));

    if (!duplicatedHeaders.length) {
      result.push(prop.header);
      return;
    }
    result.push(`${prop.header} ${duplicatedHeaders.length + 1}`);
  });
  return result;
});

const qtyFields = ['rtfQty', 'demandQty', 'onTimeQty', 'shortQty', 'lateQty'];
const ratioFields = ['rtfRatio', 'onTimeRatio', 'lateRatio'];

/**
 * short이 그리드 표시 우선순위에 더 중요해서 다음과 같이 분기처리함
 */
const ratioCellAttributes = ({ rowData, columnId }: { rowData: any; columnId: string }) => {
  const classes: string[] = [];
  if (rowData?.rtfRatio < 100) {
    classes.push('ratio-short');
    if (columnId === 'rtfRatio') classes.push('ratio-short-font');
  }
  if (rowData?.rtfRatio === 100 && rowData?.lateRatio > 0) {
    classes.push('ratio-late');
  }
  return classes.length ? { class: classes.join(' ') } : undefined;
};

const ratioMask = {
  type: 'function' as const,
  formatter: (value: unknown) => (value === null || value === undefined ? '' : `${value}%`),
};

const detailCoreConfig = computed<MozGridCoreProps>(() => {
  const qtyMask = { type: 'numeric', pattern: '#,##0.###' };
  const field = (id: string, header: string, extra: Record<string, any> = {}) => ({
    id,
    header,
    dataType: 'string',
    sortable: false,
    cellAttributes: ratioCellAttributes,
    ...(qtyFields.includes(id) ? { dataType: 'number', align: 'right', mask: qtyMask } : {}),
    ...(ratioFields.includes(id) ? { dataType: 'number', align: 'right', mask: ratioMask } : {}),
    ...extra,
  });

  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: detailDataSource.value,
    fields: [
      field('demandID', t('text-demand_id'), { width: 80, align: 'left' }),
      field('custID', t('text-cust_name'), { width: 80 }),
      field('onTimeRatio', t('text-on_time_ratio'), { width: getWidthByKey('N2') }),
      field('lateRatio', t('text-late_ratio'), { width: getWidthByKey('N2') }),
      field('rtfRatio', t('text-rtf_ratio'), { width: getWidthByKey('N2') }),
      field('showDetailCol', t('text-simple_short_reason'), { width: getWidthByKey('N2') }),
      field('itemGroupID', t('text-item_group')),
      field('itemID', t('text-item_id')),
      field('itemName', t('text-item_name')),
      field('dueWeek', t('text-due_week'), { align: 'center' }),
      field('dueDate', t('text-due_date'), { width: getWidthByKey('S2') }),
      field('demandQty', t('text-demand_qty'), { width: getWidthByKey('N2') }),
      field('onTimeQty', t('text-on_time_qty'), { width: getWidthByKey('N2') }),
      field('lateQty', t('text-late_qty'), { width: getWidthByKey('N2') }),
      field('rtfQty', t('text-rtf_qty'), { width: getWidthByKey('N2') }),
      field('shortQty', t('text-short_qty'), { width: getWidthByKey('N2') }),
      field('qtyUom', t('text-qty_uom'), { align: 'left', width: 90, hidden: true }),
      field('demand_type', t('text-demand_type'), { hidden: true }),
      field('item_type', t('text-item_type'), { hidden: true }),
      field('prod_type', t('text-prod_type'), { hidden: true }),
      field('item_size_type', t('text-item_size_type'), { hidden: true }),
      field('item_spec', t('text-item_spec'), { hidden: true }),
      ...propColumns.value.map((col, idx) =>
        field(col.binding, propHeaders.value[idx], { width: 120, align: 'left', hidden: true }),
      ),
    ],
  };
});

const shortCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: 'flat',
  keyFields: [ROW_KEY],
  data: shortDataSource.value,
  fields: [
    { id: 'shortType', header: t('text-short_type'), dataType: 'string', width: getWidthByKey('S3'), align: 'center' },
    { id: 'shortCategory', header: t('text-short_category'), dataType: 'string', width: getWidthByKey('S2') },
    { id: 'shortReason', header: t('text-short_reason'), dataType: 'string', width: getWidthByKey('DF') },
    {
      id: 'shortQty',
      header: t('text-short_qty'),
      dataType: 'number',
      width: getWidthByKey('N2'),
      align: 'right',
      mask: { type: 'numeric', pattern: '#,##0.###' },
    },
    { id: 'qtyUom', header: t('text-qty_uom'), dataType: 'string', align: 'left', width: 90, hidden: true },
    { id: 'shortDetailInfo', header: t('text-short_detail_info'), dataType: 'string', width: getWidthByKey('S1') },
    { id: 'isbID', header: t('text-isb_id'), dataType: 'string', width: getWidthByKey('S1') },
    { id: 'bomID', header: t('text-bom_id'), dataType: 'string', width: getWidthByKey('S1') },
    { id: 'routingID', header: t('text-routing_id'), dataType: 'string', width: getWidthByKey('S1') },
    { id: 'operID', header: t('text-oper_id'), dataType: 'string', width: getWidthByKey('DF') },
    { id: 'resID', header: t('text-res_id'), dataType: 'string', width: getWidthByKey('DF') },
  ].map((field) => ({ ...field, sortable: false })),
}));

const itemInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: 'flat',
  keyFields: [ROW_KEY],
  data: selectedItemInfo.value,
  fields: [
    { id: 'item_id', header: t('text-item_id'), dataType: 'string', width: 150 },
    { id: 'item_type', header: t('text-item_type'), dataType: 'string', width: getWidthByKey('S3') },
    { id: 'item_name', header: t('text-item_name'), dataType: 'string', width: 150 },
    { id: 'item_group', header: t('text-item_group'), dataType: 'string', width: getWidthByKey('S2') },
    { id: 'description', header: t('text-description'), dataType: 'string', width: getWidthByKey('S1') },
    {
      id: 'item_priority',
      header: t('text-item_priority'),
      dataType: 'number',
      width: getWidthByKey('N2'),
      align: 'right',
    },
    { id: 'procurement_type', header: t('text-procurement_type'), dataType: 'string', width: getWidthByKey('S3') },
    { id: 'prod_type', header: t('text-prod_type'), dataType: 'string', width: getWidthByKey('S3') },
    { id: 'item_size', header: t('text-item_size'), dataType: 'string', width: getWidthByKey('S3') },
    { id: 'item_spec', header: t('text-item_spec'), dataType: 'string', width: getWidthByKey('S3') },
    ...selectedItemColumnHeaders.value.map((col) => ({
      id: `${col}`,
      header: t(col),
      dataType: 'string',
      width: 150,
      cellAttributes: { class: 'master-prop-col' },
    })),
  ],
}));

const demandInfoCoreConfig = computed<MozGridCoreProps>(() => {
  const dateMask = { type: 'date', pattern: 'YYYY-MM-DD' };
  const dateTimeMask = { type: 'date', pattern: 'YYYY-MM-DD HH:mm:ss' };

  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: demandInfoSource.value,
    fields: [
      { id: 'demand_id', header: t('text-demand_id'), dataType: 'string', width: getWidthByKey('S2') },
      { id: 'item_id', header: t('text-item_id'), dataType: 'string', width: getWidthByKey('DF') },
      { id: 'site_id', header: t('text-site_id'), dataType: 'string', width: getWidthByKey('S2') },
      { id: 'buffer_id', header: t('text-buffer_id'), dataType: 'string', width: getWidthByKey('S2') },
      {
        id: 'due_date',
        header: t('text-due_date'),
        dataType: 'date',
        width: getWidthByKey('D2'),
        align: 'center',
        mask: dateMask,
      },
      {
        id: 'due_datetime',
        header: t('text-due_datetime'),
        dataType: 'date',
        width: getWidthByKey('D1'),
        align: 'center',
        mask: dateTimeMask,
      },
      {
        id: 'demand_qty',
        header: t('text-demand_qty'),
        dataType: 'number',
        width: getWidthByKey('N2'),
        align: 'right',
      },
      {
        id: 'demand_priority',
        header: t('text-demand_priority'),
        dataType: 'number',
        width: getWidthByKey('N2'),
        align: 'right',
      },
      { id: 'cust_id', header: t('text-cust_id'), dataType: 'string', width: getWidthByKey('S2') },
      { id: 'demand_type', header: t('text-demand_type'), dataType: 'string', width: getWidthByKey('S3') },
      {
        id: 'max_lateness_day',
        header: t('text-max_lateness_day'),
        dataType: 'number',
        width: getWidthByKey('N2'),
        align: 'right',
      },
      {
        id: 'max_earliness_day',
        header: t('text-max_earliness_day'),
        dataType: 'number',
        width: getWidthByKey('N2'),
        align: 'right',
      },
      { id: 'demand_group', header: t('text-demand_group'), dataType: 'string', width: getWidthByKey('S2') },
      {
        id: 'final_item_buffer_id',
        header: t('text-final_item_buffer_id'),
        dataType: 'string',
        width: getWidthByKey('S2'),
      },
      { id: 'description', header: t('text-description'), dataType: 'string', width: getWidthByKey('S1') },
      {
        id: 'legacy_data_version',
        header: t('text-legacy_data_version'),
        dataType: 'string',
        width: getWidthByKey('S2'),
        hidden: true,
      },
      {
        id: 'interfaced_from',
        header: t('text-interfaced_from'),
        dataType: 'string',
        width: getWidthByKey('S2'),
        hidden: true,
      },
      {
        id: 'create_datetime',
        header: t('text-create_datetime'),
        dataType: 'date',
        width: getWidthByKey('D1'),
        align: 'center',
        mask: dateTimeMask,
      },
      { id: 'create_user_id', header: t('text-create_user_id'), dataType: 'string', width: getWidthByKey('S2') },
      {
        id: 'update_datetime',
        header: t('text-update_datetime'),
        dataType: 'date',
        width: getWidthByKey('D1'),
        align: 'center',
        mask: dateTimeMask,
      },
      { id: 'update_user_id', header: t('text-update_user_id'), dataType: 'string', width: getWidthByKey('S2') },
    ],
  };
});

const onloadDetail = async () => {
  saveDetailParams();
  const cache = queryClient.getQueryData(detailQueryKey);
  if (!cache) {
    await detailQuery.refetch();
  }

  if (detailQuery.isSuccess.value) {
    if (detailQuery.data.value?.length) {
      detailDataSource.value = toRaw(detailQuery.data.value).map((elem: any, idx: number) => {
        propColumnsModule.parseFlex(elem);
        const [date, rangeStart, rangeEnd] = elem.dueDate.split(' ');
        return {
          ...elem,
          [ROW_KEY]: idx,
          dueWeek: projectModule.convertToFormat('dateWeek', elem.dueWeek),
          dueDate: `${projectModule.convertToFormat('date', date)} ${rangeStart} ${rangeEnd}`,
        };
      });
      demandID.value = detailDataSource.value[0].demandID;
      refSub3.value?.onLoad();
    } else {
      detailDataSource.value = [];
    }
  } else if (detailQuery.isError.value) {
    showMessage(t('msg-toast-get_error'), false);
    detailDataSource.value = [];
  }
};

// region GET DATA
const onLoad = debounce(async () => {
  await onLoadHeader();
  await onloadDetail();
}, 100);

const resetDetailDataSource = () => {
  detailDataSource.value = [];
  demandID.value = '';
};

const bomNetworkInfos = shallowRef<any[]>([]);
const demandInfos = ref<any>({});
const shortLogs = shallowRef<any[]>([]);

watchEffect(
  () => {
    if (bomNetworkQuery.isSuccess.value) {
      if (bomNetworkQuery.data.value?.bomNetworkInfos?.length) {
        const rawData = toRaw(bomNetworkQuery.data.value);
        bomNetworkInfos.value = rawData.bomNetworkInfos;
        demandInfos.value = rawData.demandInfos;
        shortLogs.value = rawData.shortLogs;
      } else {
        bomNetworkInfos.value = [];
        demandInfos.value = {};
        shortLogs.value = [];
      }
    } else if (bomNetworkQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
      bomNetworkInfos.value = [];
      demandInfos.value = {};
      shortLogs.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const shortDataSource = shallowRef<any[]>([]);

// short 그리드 데이터
watchEffect(
  () => {
    if (shortQuery.isSuccess.value) {
      if (shortQuery.data.value) {
        shortDataSource.value = withRowKey(toRaw(shortQuery.data.value));
      } else {
        shortDataSource.value = [];
      }
    } else if (bomNetworkQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
    }
  },
  {
    flush: 'post',
  },
);

const INFO_COLUMN_KEYS = [
  'item_id',
  'item_type',
  'item_name',
  'item_group',
  'description',
  'item_priority',
  'procurement_type',
  'prod_type',
  'item_size',
  'item_spec',
  'descending',
];

const selectedItemColumnHeaders = ref<string[]>([]);
const selectedItemInfo = shallowRef<any[]>([]);

watchEffect(
  () => {
    if (planVer.value && itemDetailQuery.isSuccess.value) {
      if (itemDetailQuery.data.value) {
        selectedItemColumnHeaders.value = Object.keys(itemDetailQuery.data.value).filter((item: any) => {
          if (!INFO_COLUMN_KEYS.includes(item)) {
            return true;
          }
          return false;
        });

        nextTick(() => {
          selectedItemInfo.value = withRowKey([toRaw(itemDetailQuery.data.value)]);
        });
      } else {
        selectedItemColumnHeaders.value = [];
        selectedItemInfo.value = [];
      }
    } else if (itemDetailQuery.isError.value) {
      selectedItemColumnHeaders.value = [];
      selectedItemInfo.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const demandInfoSource = shallowRef<any[]>([]);

watchEffect(
  () => {
    if (planVer.value && demandDetailQuery.isSuccess.value) {
      if (demandDetailQuery.data.value) {
        nextTick(() => {
          demandInfoSource.value = withRowKey(toRaw(demandDetailQuery.data.value));
        });
      } else {
        demandInfoSource.value = [];
      }
    } else if (itemDetailQuery.isError.value) {
      demandInfoSource.value = [];
    }
  },
  {
    flush: 'post',
  },
);

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `createColumnMapForExport(coreConfig.fields)`로 처리 불가능 함
 */
const COLUMN_MAP = {
  short_type: {
    column_name: t('text-short_type'),
    column_type: 'System.String',
    column_format: null,
  },
  short_category: {
    column_name: t('text-short_category'),
    column_type: 'System.String',
    column_format: null,
  },
  short_reason: {
    column_name: t('text-short_reason'),
    column_type: 'System.String',
    column_format: null,
  },
  short_qty: {
    column_name: t('text-short_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
  short_detail_info: {
    column_name: t('text-short_detail_info'),
    column_type: 'System.String',
    column_format: null,
  },
  isb_id: {
    column_name: t('text-isb_id'),
    column_type: 'System.String',
    column_format: null,
  },
  bom_id: {
    column_name: t('text-bom_id'),
    column_type: 'System.String',
    column_format: null,
  },
  routing_id: {
    column_name: t('text-routing_id'),
    column_type: 'System.String',
    column_format: null,
  },
  oper_id: {
    column_name: t('text-oper_id'),
    column_type: 'System.String',
    column_format: null,
  },
  res_id: {
    column_name: t('text-res_id'),
    column_type: 'System.String',
    column_format: null,
  },
};

// endregion

watch([parentsMainWidth, parentsMainHeight], () => {
  resetSize();
});

watch(open, () => {
  openItemInfo.value = open.value;
});

watch(demandOpen, () => {
  openDemandInfo.value = demandOpen.value;
});

const resetSize = () => {
  const el = document.querySelector('.rtf-report-sub2') as HTMLElement;
  if (!el) return;

  el?.style?.setProperty('--parents-main-width', `${parentsMainWidth?.value}`);
  el?.style?.setProperty('--parents-main-height', `${parentsMainHeight?.value}`);
};

const itemInfoHeaderText = computed(() => `제품 정보 보기`);

defineExpose({ onLoad, resetDetailDataSource });
</script>
<style lang="scss">
.moz-readonly-grid.rtf-report-sub2 {
  .ps-cell.ratio-short {
    background-color: #f6d5d5;
  }

  .ps-cell.ratio-late {
    background-color: #fde6c8;
  }

  .ps-row:hover,
  .ps-row.ps-selected {
    .ps-cell.ratio-short,
    .ps-cell.ratio-late {
      background-color: #d4cde8;
    }
  }

  .ps-cell.ratio-short-font {
    color: #dc5a5a;
  }
}

.cs-link {
  color: #4568e0;
  text-decoration: underline;
  cursor: pointer;
}

.bom-map-popup-container {
  height: 100%;
  width: 100%;

  .bom-map-outer-wrapper {
    border: 1px solid #bbc6d9;
    border-bottom: none;

    &:before {
      border: none !important;
    }
  }

  .grid-sort-reason {
    height: 100%;
  }
}

.info-modal-content-wrapper {
  height: 100%;
}

.demand-modal-content-wrapper {
  height: 100%;
}
</style>
