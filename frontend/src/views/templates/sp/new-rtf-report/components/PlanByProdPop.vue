<template>
  <Popup
    :title="t('text-popup-detail_view')"
    :onCancel="onClose"
    :width="popupWidth"
    :height="popupHeight"
    v-model:visible="showDetailPopup"
    :use-v-show="true"
  >
    <Tab
      class="plan-by-prod-popup-tab"
      :itemSource="tabList"
      v-model="currentTab"
      @change="onTabChanged"
      style="height: 100%; overflow: hidden"
    >
      <template v-for="tab in additionTabList" #[tab.id]>
        <div class="plan-by-prod-popup-grid-container" v-if="useAdditionTab && additionTabList" :key="tab.id">
          <slot :name="tab.id"></slot>
        </div>
      </template>
      <template #plan-by-prod-analysis>
        <div class="plan-by-prod-popup-grid-container">
          <PopupController>
            <template #filter>
              <Radio
                :label="t('text-search_method')"
                v-model="currentDemandFilter"
                :items-source="demandFilterList"
                display-expr="label"
                value-expr="value"
              />
            </template>
          </PopupController>
          <MozGrid
            name="ResBasedPlanAnalysis"
            height="100%"
            class="prod-plan-ins-master"
            :emptyState="{
              useImg: false,
            }"
            :coreConfig="masterCoreConfig"
            :contextMenuConfig="{
              useFilter: false,
              useViewSelectColumn: false,
              useExportExcel: true,
              customMenu: masterContextMenus,
              onExportOriginalData: () =>
                downloadBigData({
                  column_map: COLUMN_MAP,
                  file_name: `${t(`text-popup-prod_plan_ins_detail_popup`)}_${summaryLoadParams.planVer}`,
                  data_method: 'POST',
                  data_parameter: JSON.stringify(summaryLoadParams),
                  api_key: summaryApiKey,
                }),
            }"
            :use-tool-box="false"
            :loading="masterQuery.isPending.value"
            :use-sort="false"
            @ready="onReady"
            @data:loaded="onMasterDataLoaded"
            @cell:click="onMasterCellClick"
            @contextmenu="onMasterContextMenu"
          />
          <MozGrid
            name="ResBasedPlanAnalysis"
            height="100%"
            class="prod-plan-ins-detail"
            :coreConfig="detailCoreConfig"
            :contextMenuConfig="{
              useFilter: false,
              useViewSelectColumn: false,
              useExportExcel: true,
              onExportOriginalData: () =>
                downloadBigData({
                  column_map: DETAIL_COLUMN_MAP,
                  file_name: `${t(`text-popup-prod_plan_ins_detail_popup`)}_${detailLoadParams.planVer}`,
                  data_method: 'POST',
                  data_parameter: JSON.stringify(detailLoadParams),
                  api_key: `${detailApiKey}/Excel`,
                }),
            }"
            :use-tool-box="false"
            :use-extend-footer="true"
            :loading="detailQuery.isPending.value"
            :use-sort="false"
            @ready="onReadyDetail"
          />
        </div>
      </template>
    </Tab>
  </Popup>
</template>
<script setup lang="ts">
import { createOpenNewTabMenu, useGridContextTarget } from './gridContextMenu';
import PopupController from './PopupController.vue';
import { apiCall, downloadBigData } from '../adapters/stores';
import { useProjectInfoStore } from '../adapters/stores';
import { ROW_KEY, useLoaderParams, withRowKey } from '../adapters/utils';
import { IPlanByProdDetailSource, IPlanByProdMasterSource } from '../adapters/types';
import { MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { FieldDef, GridChrome, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
import { Popup, Radio, Tab } from '@vmscloud/moz-ui-components-vue';

import { getWidthByKey } from '@/shims/grid/utils';
import { showMessage } from '@moz-shared/utils';
import { useMutation } from '@tanstack/vue-query';
import dayjs from 'dayjs';
import { debounce, groupBy } from 'es-toolkit';
import { useTranslation } from 'i18next-vue';
import { computed, onMounted, onUnmounted, reactive, ref, shallowRef, toRefs, watch } from 'vue';

// API로 받아오는 스키마가 아니므로 타입 폴더가 아닌 컴포넌트 내에서 타입을 정의함
export interface IPlanByProdPopData {
  customers?: string[];
  demandItemIDs?: string[];
  prodQty?: number;
  demandQty?: number;
  date?: string;
  demandIDs?: string[];
}

interface ItabData {
  id: string;
  text: string;
}

/**
 * DEFINE DEFAULT VARIABLE
 */

const { t } = useTranslation(); // 다국어

interface Props {
  showDetail: boolean;
  planCycleID: string;
  planVer: string;
  data: IPlanByProdPopData | null;
  close: Function;
  width?: string | number;
  height?: string | number;
  aggregateType?: 'DAY' | 'WEEK';
  autoFocusProps?: {
    targetDemandID?: string;
    targetDate?: string;
    targetStartWeek?: string;
    targetEndWeek?: string;
  } | null;
  // PlanByProdPop을 여러 메뉴에서 사용하고 있음
  // 동일한 PlanByProdPop 컴포넌트의 popup에 해당 메뉴만의 추가적인 데이터를 보여주기 위해서 tab을 활용
  useAdditionTab?: boolean;
  additionTabList?: ItabData[] | null;
  activeTabIndex?: number;
}

const props = withDefaults(defineProps<Props>(), {
  width: 1000,
  height: 700,
  showDetail: false,
  aggregateType: 'DAY',
  useAdditionTab: false,
  additionTabList: null,
  // popup이 open될 때 초기 tab 선택을 위한 Index
  activeTabIndex: 0,
});
const {
  showDetail,
  data,
  aggregateType,
  autoFocusProps,
  planVer,
  useAdditionTab,
  additionTabList,
  activeTabIndex,
  planCycleID,
} = toRefs(props);

// 메뉴에서 사용되는 상태 값 정의
const localState: {
  masterSelectedRow: any;
} = reactive({
  masterSelectedRow: null,
});

const projectModule = useProjectInfoStore();

const demandFilterList = ref<any>([]);
const currentDemandFilter = ref<'customers' | 'demandItemIDs' | 'demandIDs' | ''>('');

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `createColumnMapForExport(coreConfig.fields)`로 처리 불가능 함
 */
const COLUMN_MAP = {
  demand_id: {
    column_name: t('text-demand_id'),
    column_type: 'System.String',
    column_format: null,
  },
  demand_item_id: {
    column_name: t('text-demand_item_id'),
    column_type: 'System.String',
    column_format: null,
  },
  cust_name: {
    column_name: t('text-cust_name'),
    column_type: 'System.String',
    column_format: null,
  },
  demand_qty: {
    column_name: t('text-demand_qty'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  due_date: {
    column_name: t('text-due_date'),
    column_type: 'System.DateTime',
    column_format: projectModule.formatGrid('date'),
  },
  warehousing_date: {
    column_name: t('text-upper-warehousing_date'),
    column_type: 'System.DateTime',
    column_format: projectModule.formatGrid('date'),
  },
  shipment_date: {
    column_name: t('text-shipment_date'),
    column_type: 'System.DateTime',
    column_format: projectModule.formatGrid('date'),
  },
  date_diff: {
    column_name: `${t('text-due_delay')}(${t('text-day')})`,
    column_type: 'System.Decimal',
    column_format: null,
  },
  rtf_ratio: {
    column_name: t('text-rtf_ratio'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  on_time_qty: {
    column_name: t('text-on_time_qty'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  late_qty: {
    column_name: t('text-late_qty'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  short_qty: {
    column_name: t('text-short_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
};

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `createColumnMapForExport(coreConfig.fields)`로 처리 불가능 함
 */
const DETAIL_COLUMN_MAP = {
  item_id: {
    column_name: t('text-item_id'),
    column_type: 'System.String',
    column_format: null,
  },
  buffer_id: {
    column_name: t('text-buffer_id'),
    column_type: 'System.String',
    column_format: null,
  },
  site_id: {
    column_name: t('text-site_id'),
    column_type: 'System.String',
    column_format: null,
  },
  item_type: {
    column_name: t('text-item_type'),
    column_type: 'System.String',
    column_format: null,
  },
  wip_qty: {
    column_name: t('text-boh'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  peg_qty: {
    column_name: t('text-use'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  prod_type: {
    column_name: t('text-prod_type'),
    column_type: 'System.String',
    column_format: null,
  },
  plan_date: {
    column_name: t('text-plan_date'),
    column_type: 'System.Decimal',
    column_format: null,
  },
  out_plan_qty: {
    column_name: t('text-out_plan_qty'),
    column_type: 'System.Decimal',
    column_format: projectModule.formatGrid('qty'),
  },
};

const tabList = computed(() => {
  const defaultTab = [{ id: 'plan-by-prod-analysis', text: t('text-popup-prod_plan_ins_detail_popup') }];

  if (useAdditionTab.value && additionTabList.value && additionTabList?.value.length) {
    additionTabList?.value.forEach((tab: { id: string; text: string }) => {
      defaultTab.unshift(tab);
    });
  }

  return defaultTab;
});

const currentTab = ref<string>(tabList.value[0].id);

watch(showDetail, () => {
  if (showDetail.value) currentTab.value = tabList.value[activeTabIndex.value].id;
});

const onTabChanged = () => {
  // 탭 변경시 실행할 로직 작성
};

watch(
  [data],
  () => {
    demandFilterList.value = [];
    currentDemandFilter.value = '';
    let isDefaultSet = false;
    if (data.value?.demandIDs) {
      demandFilterList.value.push({ label: t('text-demand_list'), value: 'demandIDs' });
      if (!isDefaultSet) currentDemandFilter.value = 'demandIDs';
      isDefaultSet = true;
    }
    if (data.value?.demandItemIDs) {
      demandFilterList.value.push({ label: t('text-demand_item_id'), value: 'demandItemIDs' });
      if (!isDefaultSet) currentDemandFilter.value = 'demandItemIDs';
      isDefaultSet = true;
    }
    if (data.value?.customers) {
      demandFilterList.value.push({ label: t('text-cust_id'), value: 'customers' });
      if (!isDefaultSet) currentDemandFilter.value = 'customers';
      isDefaultSet = true;
    }
  },
  { immediate: true, deep: true },
);

watch([showDetail, currentDemandFilter], () => {
  if (showDetail.value && currentDemandFilter.value) {
    onLoad();
  }
});

const masterGrid = shallowRef<PureSheet | null>(null); // 코어 그리드
const detailGrid = shallowRef<PureSheet | null>(null); // 코어 그리드
const masterDataSource = ref<IPlanByProdMasterSource[]>([]); // DataSource 객체 선언
const detailDataSource = ref<GroupByPlanDateType[]>([]); // DataSource 객체 선언

const itemColumns = ref<{ binding: string; header: string; width: number; align: 'left' | 'center' | 'right' }[]>([]); // 생산계획 배열
const afterDueDate = ref(new Date());
/** @description popup 이 mount 이후 첫번째 cell 자동 선택시 detail 요청을 차단 */
const ignoreDetailInit = ref(false);

const showDetailPopup = ref(false);
const apiKey = 'RarPlanByProd'; // Api Uri Key

const colorTargetDetailGridLastDate = ref('');
const colorTargetDueDate = ref('');

const { target: masterContextTarget, onContextMenu: onMasterContextMenu } = useGridContextTarget();

const masterContextMenus = [
  createOpenNewTabMenu(
    'openBomMapPlanView',
    {
      route: (item: any) => {
        return {
          path: `/sp/BomMapPlanView`,
          query: {
            planCycle: planCycleID.value,
            planVer: planVer.value,
            demandItemID: item?.demandItemID,
            demandID: item?.demandID,
          },
        };
      },
      disabled: (item: any) => {
        return !(item?.demandItemID || item?.itemID || item?.demandID);
      },
      label: t('text-context-open_bom_map_plan_view'),
    },
    () => masterContextTarget.value,
  ),
];

/**
 * short이 그리드 표시 우선순위에 더 중요해서 다음과 같이 분기처리함
 */
const masterCellAttributes = ({ row: rowData, columnId }: { row: any; columnId: string }) => {
  const classes = ['mouse-point'];
  if (rowData?.rtfRatio < 100) {
    classes.push('ratio-short');
    if (columnId === 'rtfRatio') classes.push('ratio-short-col');
  }
  if (rowData?.rtfRatio === 100 && rowData?.lateQty > 0) {
    classes.push('ratio-late');
  }
  return { class: classes.join(' ') };
};

const masterCoreConfig = computed<MozGridCoreProps>(() => {
  const qtyMask = projectModule.maskGrid('qty');
  const dateMask = projectModule.maskGrid('date');

  const fields: FieldDef[] = [
    { id: 'demandID', header: t('text-demand_id'), dataType: 'string', width: getWidthByKey('DF') },
    { id: 'demandItemID', header: t('text-demand_item_id'), dataType: 'string', width: getWidthByKey('DF') },
    { id: 'demandItemName', header: t('text-demand_item_name'), dataType: 'string', width: getWidthByKey('DF') },
    { id: 'custName', header: t('text-cust_name'), dataType: 'string', width: getWidthByKey('D1') },
    { id: 'demandQty', header: t('text-demand_qty'), dataType: 'number', width: getWidthByKey('D2'), mask: qtyMask },
    {
      id: 'dueDate',
      header: t('text-due_date'),
      dataType: 'date',
      mask: dateMask,
      align: 'center',
      width: getWidthByKey('D2'),
    },
    {
      id: 'warehousingDate',
      header: t('text-upper-warehousing_date'),
      dataType: 'date',
      mask: dateMask,
      align: 'center',
      width: getWidthByKey('D2'),
    },
    {
      id: 'shipmentDate',
      header: t('text-shipment_date'),
      dataType: 'date',
      width: getWidthByKey('D2'),
      mask: dateMask,
      align: 'center',
    },
    {
      id: 'dateDiff',
      header: `${t('text-due_delay')}(${t('text-day')})`,
      dataType: 'string',
      width: getWidthByKey('D2'),
    },
    {
      id: 'rtfRatio',
      header: t('text-rtf_ratio'),
      dataType: 'number',
      width: getWidthByKey('D2'),
      mask: { type: 'function', formatter: (value: unknown) => `${value ? value : '0'}%` },
    },
    { id: 'onTimeQty', header: t('text-on_time_qty'), dataType: 'number', width: getWidthByKey('D2'), mask: qtyMask },
    { id: 'lateQty', header: t('text-late_qty'), dataType: 'number', width: getWidthByKey('D2'), mask: qtyMask },
    {
      id: 'shortQty',
      header: t('text-short_qty'),
      dataType: 'number',
      width: getWidthByKey('N2'),
      mask: qtyMask,
      align: 'right',
    },
  ];

  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: masterDataSource.value,
    fields: fields.map((field) => ({ ...field, sortable: false, cellAttributes: masterCellAttributes })),
  };
});

const isDateFormat = (str: string): boolean => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(str);
};

/**
 * 납기일 이후 날짜 컬럼 표시 (헤더·셀 공용)
 */
const dueDateClasses = (col: string) => {
  const classes: string[] = [];
  const dueDate = localState?.masterSelectedRow?.dueDate;

  if (isDateFormat(col) && dueDate) {
    const colDate = dayjs(col);

    if (colDate.isAfter(afterDueDate.value)) {
      classes.push('late');
    } else if (colDate.isSame(afterDueDate.value, 'day')) {
      classes.push('late');
      classes.push('after-due-date');
    }
  }
  return classes;
};

const detailCellAttributes = ({ row: rowData, columnId }: { row: any; columnId: string }) => {
  const classes = dueDateClasses(columnId);
  if (rowData?.isSummaryRow) {
    classes.push('summary-row');
  }

  const attributes: Record<string, string> = {};
  if (classes.length) attributes.class = classes.join(' ');
  if (colorTargetDetailGridLastDate.value === columnId || colorTargetDueDate.value === columnId) {
    attributes.style = 'background-color: #e1707021'; // 우선순위 문제로 인라인 스타일 지정
  }
  return attributes;
};

// 왼쪽 7개 열 고정
const DETAIL_PINNED_COLUMNS = ['itemID', 'itemName', 'bufferID', 'siteID', 'itemType', 'wipQty', 'pegQty'];
// 첫 행(Summary)에서 같은 값이면 가로로 병합할 컬럼
const DETAIL_SUMMARY_MERGE_COLUMNS = ['itemID', 'itemName', 'bufferID', 'siteID', 'itemType'];

const detailCoreConfig = computed<MozGridCoreProps>(() => {
  const qtyMask = projectModule.maskGrid('qty');
  const baseFields: FieldDef[] = [
    { id: 'itemID', header: t('text-item_id'), dataType: 'string', width: getWidthByKey('D2') },
    { id: 'itemName', header: t('text-item_name'), dataType: 'string', width: getWidthByKey('D2') },
    { id: 'bufferID', header: t('text-buffer_id'), dataType: 'string', width: getWidthByKey('N3') },
    { id: 'siteID', header: t('text-site_id'), dataType: 'string', width: getWidthByKey('N3') },
    { id: 'itemType', header: t('text-type'), dataType: 'string', width: getWidthByKey('N3') },
    { id: 'wipQty', header: t('text-boh'), dataType: 'number', width: getWidthByKey('N3'), mask: qtyMask },
    { id: 'pegQty', header: t('text-use'), dataType: 'number', width: getWidthByKey('N3'), mask: qtyMask },
    { id: 'usedTotal', header: t('text-used_total'), dataType: 'number', width: getWidthByKey('N3'), mask: qtyMask },
    ...itemColumns.value.map((col): FieldDef => ({
      id: col.binding,
      header: t(col.header),
      dataType: 'number',
      width: col.width,
      align: col.align,
      mask: qtyMask,
    })),
  ];
  const fields = baseFields.map((field): FieldDef => {
    const headerClasses = dueDateClasses(field.id);
    return {
      ...field,
      sortable: false,
      pinned: DETAIL_PINNED_COLUMNS.includes(field.id) ? ('left' as const) : undefined,
      cellAttributes: detailCellAttributes,
      headerAttributes: headerClasses.length ? { class: headerClasses.join(' ') } : undefined,
    };
  });

  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: detailDataSource.value,
    fields,
    // 7번째 이후 컬럼은 생산계획, 재공 수량은 재공으로 헤더를 묶는다
    columnGroups: [
      { id: 'wip', header: t('text-wip'), children: ['wipQty', 'pegQty'] },
      {
        id: 'prodPlan',
        header: t('text-prod_plan'),
        children: ['usedTotal', ...itemColumns.value.map((col) => col.binding)],
      },
    ],
  };
});

/**
 * INITIALIZE
 */
const masterFocusColumnHandler = () => {
  if (!autoFocusProps.value || !showDetailPopup.value) return;
  if (autoFocusProps.value.targetDemandID) {
    masterFocusColumnByDemandID();
  } else {
    masterFocusColumnByDate();
  }
};

/**
 * 마스터 그리드의 행을 선택하고 선택 변경을 처리한다 (옛 그리드의 select(new CellRange(idx, 0)) 대체)
 */
const selectMasterRow = (index: number) => {
  const item = masterDataSource.value[index];
  if (!item) return;
  masterGrid.value?.cells.selectCellsByViewIndices([{ viewIndex: index, columnId: 'demandID' }]);
  masterGrid.value?.scrollToRow(index);
  onMasterSelectionChanged(item);
};

const masterFocusColumnByDemandID = () => {
  if (!masterDataSource.value) return;
  let focusTargetIndex = -1;

  if (data.value?.demandIDs?.length) {
    focusTargetIndex = masterDataSource.value.findIndex(
      (elem) => elem.demandID === data.value?.demandIDs?.[0],
    );
  } else {
    const prodQty = data.value?.prodQty ?? 0;
    const demandQty = data.value?.demandQty ?? 0;

    // 생산계획량과 요구수량 모두 0이면 그냥 첫번째 선택
    // selectIdx = 0;

    // 생산계획량이 0을 초과하면 생산완료일에 해당하는 첫번째
    if (prodQty) {
      focusTargetIndex = masterDataSource.value.findIndex(
        (elem) => elem.shipmentDate === data.value?.date,
      );
    }

    // 생산계획량이 0이면 납기일에 해당하는 첫번째 선택
    if (!prodQty && demandQty) {
      focusTargetIndex = masterDataSource.value.findIndex(
        (elem) => dayjs(elem.dueDate).format('YYYY-MM-DD') === data.value?.date,
      );
    }

    // masterGrid 가 정합성이 깨져 -1이 발생한 경우 첫번째 선택으로 초기화
    if (focusTargetIndex === -1) {
      focusTargetIndex = 0;
      onDetailLoad(masterDataSource.value[0]);
    }
  }

  if (focusTargetIndex !== -1) {
    selectMasterRow(focusTargetIndex);
  }
};

const masterFocusColumnByDate = () => {
  if (aggregateType.value === 'DAY' && !autoFocusProps.value?.targetDate) return;
  if (
    aggregateType.value === 'WEEK' &&
    (!autoFocusProps.value?.targetStartWeek || !autoFocusProps.value?.targetEndWeek)
  ) {
    return;
  }

  if (!masterGrid.value) return;

  let focusTargetIndex;
  // 이진 탐색으로 targetDate 이후의 날짜중 가장 빠른 날짜를 구한다.
  const binarySearch = (targetDate: string) => {
    if (!masterGrid.value || !masterDataSource.value.length) {
      return { dueDateMidIdx: -1, shipmentDateMidIdx: -1 };
    }

    // plan_date와의 일 수 차이가 0일인 날짜가 1순위이므로 target은 0이다.
    const target = 0;
    let dueDateStart = 0;
    let dueDateEnd = masterDataSource.value.length - 1;
    let dueDateMidIdx = -1;
    let dueDateFinishedExplore = false;

    let shipmentDateStart = 0;
    let shipmentDateEnd = masterDataSource.value.length - 1;
    let shipmentDateMidIdx = -1;
    let shipmentDateFinishedExplore = false;

    while (
      dueDateStart < dueDateEnd &&
      shipmentDateStart < shipmentDateEnd &&
      (!dueDateFinishedExplore || !shipmentDateFinishedExplore)
    ) {
      if (!dueDateFinishedExplore) {
        dueDateMidIdx = Math.floor((dueDateStart + dueDateEnd) / 2);
        if (!masterDataSource.value[dueDateMidIdx]?.dueDate) {
          dueDateMidIdx = -1;
          break;
        }
      }

      if (!shipmentDateFinishedExplore) {
        shipmentDateMidIdx = Math.floor((shipmentDateStart + shipmentDateEnd) / 2);
        if (!masterDataSource.value[shipmentDateMidIdx]?.shipmentDate) {
          shipmentDateMidIdx = -1;
          break;
        }
      }

      const dueDateMidDiff = Number(
        dayjs(masterDataSource.value[dueDateMidIdx].dueDate).diff(dayjs(targetDate), 'day'),
      );
      const shipmentDateMidDiff = Number(
        dayjs(masterDataSource.value[shipmentDateMidIdx].shipmentDate).diff(dayjs(targetDate), 'day'),
      );

      if (target === dueDateMidDiff) {
        dueDateFinishedExplore = true;
      } else {
        if (dueDateMidDiff >= target) {
          dueDateEnd = dueDateMidIdx;
        } else {
          dueDateStart = dueDateMidIdx + 1;
        }
      }

      if (target === shipmentDateMidDiff) {
        shipmentDateFinishedExplore = true;
      } else {
        if (target >= shipmentDateMidDiff) {
          shipmentDateStart = shipmentDateMidIdx + 1;
        } else {
          shipmentDateEnd = shipmentDateMidIdx;
        }
      }
    }

    while (
      dueDateMidIdx !== -1 &&
      Number(dayjs(masterDataSource.value[dueDateMidIdx].dueDate).diff(dayjs(targetDate), 'day')) < 0 &&
      !masterDataSource.value[dueDateMidIdx + 1]?.dueDate
    ) {
      dueDateMidIdx += 1;
    }
    while (
      shipmentDateMidIdx !== -1 &&
      Number(
        dayjs(masterDataSource.value[shipmentDateMidIdx].shipmentDate).diff(dayjs(targetDate), 'day'),
      ) < 0 &&
      masterDataSource.value[shipmentDateMidIdx + 1]?.shipmentDate
    ) {
      shipmentDateMidIdx += 1;
    }

    return { dueDateMidIdx, shipmentDateMidIdx };
  };

  // 집계 기준에 따른 조건 분기
  if (aggregateType.value === 'DAY') {
    // 이진 탐색 실행
    if (!autoFocusProps.value?.targetDate) return;
    const { dueDateMidIdx, shipmentDateMidIdx } = binarySearch(autoFocusProps.value.targetDate);
    // 이진 탐색으로 구한 인덱스를 기반으로 조건 분기

    if (
      // 1 순위 : 납기일 = 선택한 날짜
      dueDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[dueDateMidIdx]?.dueDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) === 0
    ) {
      focusTargetIndex = dueDateMidIdx;
    } else if (
      // 2 순위 : 생산 완료일 = 선택한 날짜
      shipmentDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[shipmentDateMidIdx]?.shipmentDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) === 0
    ) {
      focusTargetIndex = shipmentDateMidIdx;
    } else if (
      // 3 순위 : 선택한 날짜 < 생산 완료일 중에서, 가장 생산 완료일이 작은 Demand
      shipmentDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[shipmentDateMidIdx]?.shipmentDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) >= 0
    ) {
      focusTargetIndex = shipmentDateMidIdx;
    } else if (
      // 4 순위 : 선택한 날짜 < 납기일 중에서, 가장 납기일이 작은 Demand
      dueDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[dueDateMidIdx]?.dueDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) >= 0
    ) {
      focusTargetIndex = dueDateMidIdx;
    } else {
      // 5 순위 : 마지막 Demand (여기까지 왔으면, 되게 뒤쪽 날짜를 선택한 상황이라서, 마지막 Demand 선택하면 됨)
      focusTargetIndex = masterDataSource.value.length - 1;
    }
  } else {
    // 이진 탐색 실행
    if (!autoFocusProps.value?.targetStartWeek) return;
    const { dueDateMidIdx, shipmentDateMidIdx } = binarySearch(autoFocusProps.value.targetStartWeek);
    // 이진 탐색으로 구한 인덱스를 기반으로 조건 분기
    const isWeekStartEarlierThanDueDate =
      dueDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[dueDateMidIdx].dueDate).diff(
        dayjs(autoFocusProps.value.targetStartWeek),
        'day',
      ) >= 0;
    const isWeekEndLaterThanDueDate =
      dueDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[dueDateMidIdx].dueDate).diff(
        dayjs(autoFocusProps.value.targetEndWeek),
        'day',
      ) <= 0;
    const isWeekStartEarlierThanShipmentDate =
      shipmentDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[shipmentDateMidIdx].shipmentDate).diff(
        dayjs(autoFocusProps.value.targetStartWeek),
        'day',
      ) >= 0;
    const isWeekEndLaterThanShipmentDate =
      shipmentDateMidIdx !== -1 &&
      dayjs(masterDataSource.value[shipmentDateMidIdx].shipmentDate).diff(
        dayjs(autoFocusProps.value.targetEndWeek),
        'day',
      ) <= 0;

    if (isWeekStartEarlierThanShipmentDate && isWeekEndLaterThanShipmentDate) {
      // 1 순위 : First ≤ 생산 완료일 ≤ Last 중에서, 가장 생산 완료일이 작은 Demand
      focusTargetIndex = shipmentDateMidIdx;
    } else if (isWeekStartEarlierThanDueDate && isWeekEndLaterThanDueDate) {
      // 2 순위 : First ≤ 납기일 ≤ Last 중에서, 가장 납기일이 작은 Demand
      focusTargetIndex = dueDateMidIdx;
    } else if (isWeekStartEarlierThanShipmentDate) {
      // 3 순위 : Last < 생산 완료일 중에서, 가장 생산 완료일이 작은 Demand
      focusTargetIndex = shipmentDateMidIdx;
    } else if (isWeekStartEarlierThanDueDate) {
      // 4 순위 : Last < 납기일 중에서, 가장 납기일이 작은 Demand
      focusTargetIndex = dueDateMidIdx;
    } else {
      // 5 순위 : 마지막 Demand (여기까지 왔으면, 되게 뒤쪽 날짜를 선택한 상황이라서, 마지막 Demand 선택하면 됨)
      focusTargetIndex = masterDataSource.value.length - 1;
    }
  }

  selectMasterRow(focusTargetIndex);
};

// GRID INITIALIZE
const onReady = (grid: PureSheet, _chrome: GridChrome) => {
  masterGrid.value = grid;
};

const onReadyDetail = (grid: PureSheet, _chrome: GridChrome) => {
  detailGrid.value = grid;

  // 첫 행(Summary)은 값이 같은 왼쪽 컬럼끼리 가로로 병합한다
  grid.setMergeConfig({
    type: 'custom',
    columns: DETAIL_SUMMARY_MERGE_COLUMNS,
    getMergedRange: ({ rowIndex, columnId, columnsInOrder, getCellValue, getRowData }: any) => {
      if (rowIndex !== 0 || !getRowData(0)?.isSummaryRow) return null;

      const value = getCellValue(rowIndex, columnId);
      let start = DETAIL_SUMMARY_MERGE_COLUMNS.indexOf(columnId);
      let end = start;
      while (start > 0 && getCellValue(rowIndex, DETAIL_SUMMARY_MERGE_COLUMNS[start - 1]) === value) start--;
      while (
        end < DETAIL_SUMMARY_MERGE_COLUMNS.length - 1 &&
        getCellValue(rowIndex, DETAIL_SUMMARY_MERGE_COLUMNS[end + 1]) === value
      ) {
        end++;
      }
      if (start === end) return null;

      return {
        startRow: rowIndex,
        endRow: rowIndex,
        startCol: columnsInOrder.indexOf(DETAIL_SUMMARY_MERGE_COLUMNS[start]),
        endCol: columnsInOrder.indexOf(DETAIL_SUMMARY_MERGE_COLUMNS[end]),
      };
    },
  });
};

const onMasterCellClick = (payload: any) => {
  onMasterSelectionChanged(payload?.row);
};

/**
 * DEFINE API
 *    apiCall (URI : apiKey, Body : param, Method : GET / POST / PUT / DELETE)
 *    CallBack Function
 */
// GET DATA
const fetchCall = (url: string, param: any) => {
  if (!param.planVer) return null;
  if (!showDetail.value) return null;

  return apiCall({ url, param, method: 'POST' });
};

const summaryApiKey = `${apiKey}/Summary` as const;
const { loadParams: summaryLoadParams, saveParams: saveSummaryLoadParam } = useLoaderParams(() => {
  const params: {
    planVer: string | null | undefined;
    itemIDs?: string[];
    customers?: string[];
    demandIDs?: string[];
    summary: string;
  } = {
    planVer: planVer.value,
    itemIDs: [],
    customers: [],
    demandIDs: [],
    summary: '',
  };

  switch (currentDemandFilter.value) {
    case 'demandIDs':
      params.demandIDs = data.value?.demandIDs;
      break;
    case 'demandItemIDs':
      params.itemIDs = data.value?.demandItemIDs;
      break;
    case 'customers':
      params.customers = data.value?.customers;
      break;
    default:
      break;
  }
  params.summary = currentDemandFilter.value;
  return [
    summaryApiKey,
    {
      ...params,
    },
  ];
});

const masterQuery = useMutation({
  mutationFn: async () => await fetchCall(summaryApiKey, summaryLoadParams.value),
  onSuccess: (result) => {
    if (result && result.data && result.data.length) {
      masterDataSource.value = withRowKey(result.data);
    } else {
      masterDataSource.value = []
    }
  },
  onError: () => {
    showMessage(t('msg-toast-get_error'), false);
    masterDataSource.value = [];
  },
  onSettled: () => {
    ignoreDetailInit.value = true;
  },
});

const demandID = ref('');
const detailApiKey = `${apiKey}/Detail` as const;
const { loadParams: detailLoadParams, saveParams: saveDetailLoadParam } = useLoaderParams(() => [
  detailApiKey,
  {
    planVer: planVer.value,
    demandID: demandID.value,
  },
]);

const detailQuery = useMutation({
  mutationFn: async () => await fetchCall(detailApiKey, detailLoadParams.value),
  onSuccess: (result) => {
    if (result && result.data) {
      setColumnGroups(result.data.period[0] || []);
      groupByPlanDate(result.data.detail || []);
    } else {
      detailDataSource.value = [];
    }
  },
  onError: () => {
    showMessage(t('msg-toast-get_error'), false);
    detailDataSource.value = [];
  },
});

const onMasterLoad = () => {
  saveSummaryLoadParam();
  masterQuery.mutateAsync();
};

const onDetailLoad = (masterSelectedRow: any) => {
  if (!masterSelectedRow?.demandID) {
    setColumnGroups();
    groupByPlanDate([]);
    return;
  }

  demandID.value = masterSelectedRow.demandID;
  saveDetailLoadParam();
  detailQuery.mutateAsync();
};

/**
 * BUTTON EVENT
 */
// 조회 버튼 CLICK
const onLoad = async () => {
  onMasterLoad();
};

/**
 * 날짜로 들어갈 생산계획과 그리드 해더를 만듬
 */
const setColumnGroups = (datas?: { minDate: string; maxDate: string }) => {
  const newItemColumns: { binding: string; header: string; width: number; align: 'left' | 'center' | 'right' }[] = [];
  const minDate = datas?.minDate; // 주차 시작일
  const maxDate = datas?.maxDate; // 주차 마감일

  colorTargetDetailGridLastDate.value = maxDate ?? '';
  const calcDate = dayjs(maxDate).add(1, 'day');

  if (minDate || maxDate) {
    for (let s = dayjs(minDate); s.isBefore(calcDate); s = s.add(1, 'day')) {
      // day 단위 for 문
      const dateBinding = s.format('YYYY-MM-DD');
      const dateHeader = projectModule.convertToFormat('date', s.format('YYYYMMDD'));

      newItemColumns.push({
        binding: dateBinding,
        header: dateHeader,
        width: 80,
        align: 'right',
      });
    }
  }

  // 헤더 묶음(재공·생산계획)은 detailCoreConfig 의 columnGroups 로 만든다
  itemColumns.value = newItemColumns;
};

type FirstRowType = { usedTotal: number; isSummaryRow?: boolean };
type PlanDateType = { [key: string]: IPlanByProdDetailSource['outPlanQty'] };
type GroupByPlanDateType = Partial<IPlanByProdDetailSource & FirstRowType & PlanDateType>;
/**
 * flex gird로 피봇 형태의 그리드를 만드는 방식이라 첫번째 row를 따로 처리
 */
const groupByPlanDate = (detail: IPlanByProdDetailSource[]) => {
  const rows: GroupByPlanDateType[] = [];

  // 아이템별 데이터 그룹 선정
  const groupByData: Record<string, any[]> = groupBy(
    detail,
    (item) => `${item.itemID}_${item.bufferID}_${item.siteID}`,
  ) as Record<string, any[]>;
  const firstKey = Object.keys(groupByData)[0];
  if (!!firstKey) {
    const summary = groupByData[firstKey]; // 0번째 데이터 선택
    if (summary.length > 0) {
      const firstRow: GroupByPlanDateType = {};
      summary.forEach((item) => {
        if (!item.itemID) return; // 비어있는 row 추가 방지
        Object.assign(firstRow, {
          ...item,
          itemID: `${item.itemID} Summary`,
          itemName: `${item.itemID} Summary`,
          bufferID: `${item.itemID} Summary`,
          siteID: `${item.itemID} Summary`,
          prodType: `${item.itemID} Summary`,
          usedTotal: (firstRow?.usedTotal || 0) + (item.outPlanQty ?? 0),
          isSummaryRow: true,
          [dayjs(item.planDate).format('YYYY-MM-DD')]: item.outPlanQty,
        });
      });
      rows.push(firstRow);
    }
  }

  // 아이템별 루프
  Object.keys(groupByData).forEach(async (key) => {
    const newItem = groupByData[key];
    const row: GroupByPlanDateType = {};

    // 장비 밑에 값이 없으면 continue
    if (newItem.length === 0) return;

    newItem.forEach((item: any) => {
      Object.assign(row, {
        ...item,
        [dayjs(item.planDate).format('YYYY-MM-DD')]: item.outPlanQty,
      });
    });

    if (row.itemID) rows.push(row); // 비어있는 row 추가 방지
  });

  detailDataSource.value = withRowKey(rows);
};

/**
 * EVENT
 */
const onMasterSelectionChanged = debounce((selected?: any) => {

  if (!selected) {
    localState.masterSelectedRow = null;
    detailDataSource.value = [];
    itemColumns.value = [];
    return;
  }
  const dueDate = new Date(selected?.dueDate);
  colorTargetDueDate.value = dayjs(dueDate).format('YYYY-MM-DD');
  afterDueDate.value = dayjs(dueDate.setDate(dueDate.getDate() + 1)).toDate();
  localState.masterSelectedRow = selected;

  if (ignoreDetailInit.value) {
    onDetailLoad(selected);
    ignoreDetailInit.value = true;

    return;
  }
}, 100);

const onClose = () => {
  masterGrid.value?.cells.clearCellSelection();
  props?.close();
};

/**
 * WATCH
 */

// 열기/닫기 시
watch([showDetail], () => {
  if (showDetail.value) {
    showDetailPopup.value = true;
    ignoreDetailInit.value = false;
    masterDataSource.value = [];
    detailDataSource.value = [];
  } else {
    masterDataSource.value = [];
    detailDataSource.value = [];
    showDetailPopup.value = false;
  }
});

// 데이터가 바뀌면 첫 행을 선택하고, 자동 포커스 대상이 있으면 그 행을 선택한다 (옛 itemsSourceChanged 대체)
const onMasterDataLoaded = () => {
  if (!masterDataSource.value.length) {
    onMasterSelectionChanged(null);
    return;
  }
  selectMasterRow(0);
  masterFocusColumnHandler();
};

// region 브라우저 사이즈에 따른 팝업 크기 계산
// 팝업 크기 계산을 위한 상수
const MARGIN_WIDTH = 250; // 브라우저 창과 팝업 사이 여백
const MARGIN_HEIGHT = 70; // 브라우저 창과 팝업 사이 여백
const MIN_WIDTH = 780; // 최소 너비
const MIN_HEIGHT = 600; // 최소 높이

const popupWidth = ref(1100);
const popupHeight = ref(800);

// 팝업 크기 조절 함수
const updatePopupSize = () => {
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;

  popupWidth.value = Math.max(MIN_WIDTH, windowWidth - MARGIN_WIDTH * 2);
  popupHeight.value = Math.max(MIN_HEIGHT, windowHeight - MARGIN_HEIGHT * 2);
};

// 컴포넌트 마운트 시 초기 크기 설정 및 리사이즈 이벤트 리스너 등록
onMounted(() => {
  updatePopupSize();
  window.addEventListener('resize', updatePopupSize);
});

// 컴포넌트 언마운트 시 이벤트 리스너 제거
onUnmounted(() => {
  window.removeEventListener('resize', updatePopupSize);
});
// endregion
</script>
<style lang="scss">
.plan-by-prod-popup-grid-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;

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

  .ratio-short-col {
    color: #dc5a5a !important;
  }

  .moz-tabs-container {
    display: block !important;
  }

  .mouse-point {
    cursor: pointer;
  }
}

.prod-plan-ins-master,
.prod-plan-ins-detail {
  .ps-header-cell {
    justify-content: center;

    &.after-due-date {
      border-left: 2px solid #dc5a5a;
    }
  }

  .ps-cell {
    &.summary-row {
      background-color: #d6def8;
      font-weight: 500;
    }

    &.late {
      color: #dc5a5a;
    }

    &.after-due-date {
      border-left: 2px solid #dc5a5a;
    }
  }
}

.plan-by-prod-popup-tab {
  .moz-tab-body {
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .hide {
      min-height: 0;
    }
  }
}
</style>
