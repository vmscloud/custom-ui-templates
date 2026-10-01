<template>
  <div class="plan-by-prod-popup-grid-container">
    <div class="plan-by-prod-popup-grid-summary">
      <div>
        <div class="capa">
          <span
            >{{ t('text-demand_qty_lng') }} :
            {{
              getPlanByProdSummaryQuery.isPending.value
                ? '0'
                : planByProdSummarySource?.demandQty
                  ? `${getValue(planByProdSummarySource?.demandQty, '-')}`
                  : '-'
            }}</span
          >
          <span class="dividor">|</span>
          <span>{{
            `${t('text-used_total')} : ${getPlanByProdSummaryQuery.isPending.value ? '0' : getValue((planByProdSummarySource?.shipmentQty || 0).toLocaleString(), '-')}`
          }}</span>

          <span class="dividor">|</span>
          <span>
            {{
              `${t('text-available-wip-qty')} : ${getPlanByProdSummaryQuery.isPending.value ? '0' : getValue((planByProdSummarySource?.wipQty || 0).toLocaleString(), '-')}`
            }}
          </span>
          <span class="dividor">|</span>
          <span>
            {{
              `${t('text-use')} : ${getPlanByProdSummaryQuery.isPending.value ? '0' : getValue((planByProdSummarySource?.pegQty || 0).toLocaleString(), '-')} (${getValue(
                (planByProdSummarySource?.pegRatio || 0).toLocaleString(),
                '-',
              )}%)`
            }}
          </span>
          <span class="dividor">|</span>
          <span>
            {{
              `${t('text-upper-warehousing_date')} :
          ${getPlanByProdSummaryQuery.isPending.value ? '-' : planByProdSummarySource?.warehousingDate ? getValue((dayjs(planByProdSummarySource?.warehousingDate).format('YYYY-MM-DD') || '-').toLocaleString(), '-') : '-'}`
            }}
            <span class="dividor">|</span>

            {{
              `${t('text-shipment_date')} :
          ${getPlanByProdSummaryQuery.isPending.value ? '-' : planByProdSummarySource?.shipmentDate ? getValue((dayjs(planByProdSummarySource?.shipmentDate).format('YYYY-MM-DD') || '-').toLocaleString(), '-') : '-'}`
            }}
          </span>
        </div>
      </div>
    </div>
    <MozGrid
      :name="`${currentMenu.menuID}-plan-by-prod_pivot`"
      :id="`${currentMenu.menuID}-plan-by-prod_pivot-id`"
      :emptyState="{
        contentMsg: '',
      }"
      class="prod-plan-ins-main"
      height="100%"
      :coreConfig="pivotCoreConfig"
      :usePivot="true"
      :use-tool-box-setting="true"
      :loading="detailQuery.isPending.value && getPlanByProdDetailQuery.isPending.value"
      :contextMenuConfig="{
        customMenu: [
          {
            id: 'openWipInfoDetail',
            label: t('text-open-wip-info-detail-view'),
            handler: () => (popup = true),
          },
          {
            id: 'openProdPlanDetail',
            label: t('text-open-prod-plan-detail-view'),
            handler: () => (showTargetPlanView = true),
          },
        ],
      }"
    >
      <template #tool-items>
        <div
          @click="handleZoomClick"
          class="zoom-button"
          v-tooltip="{
            text: isZoomedDetail ? t('text-zoom_out') : t('text-zoom_in'),
            position: ['center', 'toBottom, 4px'],
          }"
        >
          <IconExpandArrow v-if="!isZoomedDetail" />
          <IconCollapseArrow v-else />
        </div>
      </template>
    </MozGrid>
  </div>
  <Popup
    :width="popupWidth"
    :height="620"
    v-model:visible="popup"
    :title="t('text-popup-peg_info_detail')"
    :onCancel="
      () => {
        popup = false;
      }
    "
    preset="close"
    :resizeable="false"
    :style="{
      minWidth: '650px',
      minHeight: '400px',
    }"
  >
    <div class="peg-detail-outer-wrapper">
      <div>
        <div class="peg-detail-label">
          {{ t('text-popup-selected_demand_info') }}
        </div>
        <MozGrid
          :height="demandInfoGridHeight"
          :coreConfig="demandInfoCoreConfig"
          :useContextMenu="false"
          :use-tool-box="false"
          :use-extend-footer="false"
          :useSort="false"
          :name="`${currentMenu.menuID}_sub3_demand_info_modal`"
          :id="`${currentMenu.menuID}-sub3-demand-info-modal-id`"
        />
      </div>
      <div class="peg-detail-section">
        <div class="peg-detail-label">
          {{ t('text-popup-peg_info') }}
        </div>
        <div class="peg-detail-grid-wrapper">
          <MozGrid
            :coreConfig="pegInfoCoreConfig"
            :useContextMenu="false"
            :height="340"
            :use-tool-box="false"
            :useSort="false"
            :name="`${currentMenu.menuID}_sub3_peg_info_modal`"
            :id="`${currentMenu.menuID}-sub3-peg-info-modal-id`"
          />
        </div>
      </div>
    </div>
  </Popup>

  <Popup
    :width="targetPlanPopupWidth"
    :height="targetPlanPopupHeight"
    v-model:visible="showTargetPlanView"
    :title="targetPlanTitle"
    :onCancel="
      () => {
        showTargetPlanView = false;
      }
    "
    preset="close"
    :maxWidth="targetPlanPopupWidth"
    :maxHeight="targetPlanPopupHeight"
    :resizeable="true"
    :style="{
      minWidth: '650px',
      minHeight: '400px',
    }"
    :useVShow="false"
  >
    <div ref="container" class="bom-map-popup-container" v-loading="bomNetworkQuery.isFetching.value">
      <SplitPane horizontal style="max-width: 100%">
        <Pane size="58%" max-size="90%">
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
        <Pane size="42%" max-size="90%">
          <div v-if="!bomNetworkQuery.isFetching.value && bomNetworkInfos?.length" class="grid-sort-reason">
            <div class="grid-uom-type-viewer">
              {{
                `(${t('text-qty_uom')}: ${bufferPlanTargetSource[0]?.qty_uom ?? '-'}, ${t('text-oper_group_id')} ${t('기준')})`
              }}
            </div>
            <MozGrid
              :name="`${currentMenu.menuID}-buffer-plan-target_pivot`"
              :id="`${currentMenu.menuID}-buffer-plan-target_pivot-id`"
              class="buffer-plan-target-main"
              height="100%"
              :coreConfig="bufferPlanCoreConfig"
              :use-tool-box-setting="false"
              :use-tool-box="false"
              :usePivotBar="false"
              :useSort="false"
              :loading="bufferPlanTargetQuery.isFetching.value"
              @ready="onBufferPlanReady"
            />
          </div>
        </Pane>
      </SplitPane>
    </div>
  </Popup>
</template>
<script setup lang="ts">
import { useMenuStore, usePlanCycleStore } from './adapters/stores';
import { useProjectInfoStore } from './adapters/stores';
import BomMapInterface from './components/bom-map/BomMapInterface.vue';
import { IPlanByProdDetailSource } from './adapters/types';
import { ROW_KEY, withRowKey } from './adapters/utils';
import { MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { GridChrome, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
import { EmptyState, Pane, Popup, SplitPane } from '@vmscloud/moz-ui-components-vue';
import { IconCollapseArrow, IconExpandArrow } from '@moz-shared/icons';
import { getWidthByKey } from '@/shims/grid/utils';
import { getValue, showMessage } from '@moz-shared/utils';
import dayjs from 'dayjs';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import { computed, inject, reactive, ref, toRaw, watch, watchEffect } from 'vue';
import { IRtfReportQuery } from './NewRtfReport';

const planCycleStore = usePlanCycleStore();
const { planVer, planCycleID, fromDate, toDate } = storeToRefs(planCycleStore as any);

const projectModule = useProjectInfoStore();
const { currentProjectID: projectID } = storeToRefs(projectModule);
const projectInfoStore = useProjectInfoStore();
const userID = computed(() => projectInfoStore.userInfo?.id || '');

const {
  mainLoadParams,
  demandID,
  getPlanByProdDetailQuery,
  demandInfoQuery,
  pegInfoDetailQuery,
  showPegInfoDetail: popup,
  getPlanByProdSummaryQuery,
  detailQuery,
  bomNetworkQuery,
  showTargetPlanView,
  bufferPlanTargetQuery,
  isZoomedDetail,
  // currentWidgetSetting,
} = inject('useRtfReport') as IRtfReportQuery;

// ✅ 확대 버튼 클릭 핸들러
const handleZoomClick = () => {
  isZoomedDetail.value = !isZoomedDetail.value;
};

/**
 * DEFINE DEFAULT VARIABLE
 */

const { t } = useTranslation(); // 다국어

// 메뉴에서 사용되는 상태 값 정의
const localState: {
  masterSelectedRow: any;
  collapsibleSubtotals: boolean;
} = reactive({
  masterSelectedRow: null,
  collapsibleSubtotals: true,
});

const menuModule = useMenuStore();
const { currentMenu } = storeToRefs(menuModule);

/**
 * 피벗 소계/합계 설정
 * collapsibleSubtotals가 true일 때 열에서만 부분합 표시(접기/펼치기 가능), 행에서는 부분합 없음
 */
const pivotTotals = computed(() => ({
  showRowSubTotals: false,
  showRowGrandTotals: false,
  showColumnSubTotals: localState.collapsibleSubtotals,
  showColumnGrandTotals: true,
  columnCollapsible: localState.collapsibleSubtotals,
  showZeros: false,
}));

const pivotCoreConfig = computed<MozGridCoreProps>(() => {
  const rowField = (field: string, header: string, dataType = 'string') => ({ field, header, dataType, width: 100 });
  const rowFields = [
    rowField('operGroupID', t('text-oper_group_id')),
    rowField('operID', t('text-oper_id')),
    rowField('itemID', t('text-item_id')),
    rowField('siteID', t('text-site_id')),
    rowField('itemType', t('text-item_type')),
    rowField('wipQty', t('text-default-wip_qty'), 'number'),
    rowField('pegQty', t('text-peg_qty'), 'number'),
    rowField('usedTotalQty', t('text-used_total'), 'number'),
  ];

  // if (currentWidgetSetting?.value?.detailType === 'OPER') → operID 부터
  // if (currentWidgetSetting?.value?.detailType === 'BUFFER') → bufferSeq, bufferID 부터

  return {
    mode: 'pivot',
    data: dataSource.value,
    rowFields,
    columnFields: [
      { field: 'planMonth', header: t('text-plan_month'), dataType: 'string' },
      // { field: 'planWeek', header: t('text-plan_week'), dataType: 'string' },
      { field: 'planDate', header: t('text-plan_date'), dataType: 'string' },
    ],
    valueFields: [{ field: 'outPlanQty', header: t('text-out_plan_qty'), dataType: 'number', aggregate: 'sum' }],
    ...pivotTotals.value,
  };
});

const detailDataSource = ref<GroupByPlanDateType[]>([]); // DataSource 객체 선언
const planByProdSummarySource = ref<any>();

const targetPlanTitle = computed(() => {
  const prefix = 'Target vs Plan';

  return `${prefix}(${t('text-by-oper-group')})`;
  // if (currentWidgetSetting?.value?.detailType === 'OPERGROUP') {
  //   return `${prefix}(${t('text-by-oper-group')})`;
  // }

  // if (currentWidgetSetting?.value?.detailType === 'OPER') {
  //   return `${prefix}(${t('text-by-oper')})`;
  // }

  // if (currentWidgetSetting?.value?.detailType === 'BUFFER') {
  //   return `${prefix}(${t('text-by-buffer')})`;
  // }

  // return prefix;
});

/**
 * INITIALIZE
 */

// plan_type 값들의 정렬용 prefix 제거 (모든 "숫자_" 패턴에서 제거)
const onBufferPlanReady = (grid: PureSheet, _chrome: GridChrome) => {
  grid.formatRow.addHandler('bufferPlanPrefix', (info: any) => {
    const cells = info?.ctx?.cells;
    if (!cells) return;
    Object.values(cells).forEach((cell: any) => {
      const text = cell?.element?.textContent;
      if (text && /^\d+_/.test(text)) {
        cell.element.textContent = text.replace(/^\d+_/, '');
      }
    });
  });
};

/**
 * DEFINE API
 *    apiCall (URI : apiKey, Body : param, Method : GET / POST / PUT / DELETE)
 *    CallBack Function
 */
// GET DATA
// const fetchCall = (url: string, param: any) => {
//   if (!param.planVer) return null;

//   return apiCall(url, param, 'POST');
// };

watchEffect(
  () => {
    if (planVer.value && getPlanByProdSummaryQuery.isSuccess.value) {
      if (getPlanByProdSummaryQuery.data.value?.length) {
        planByProdSummarySource.value = getPlanByProdSummaryQuery.data.value[0];
      }
    } else if (getPlanByProdSummaryQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
      detailDataSource.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const dataSource = ref<any[]>([]);

watchEffect(
  () => {
    if (planVer.value && getPlanByProdDetailQuery.isSuccess.value) {
      if (getPlanByProdDetailQuery.data.value) {
        dataSource.value = toRaw(getPlanByProdDetailQuery.data.value.detail);
      } else {
        dataSource.value = [];
      }
    } else if (getPlanByProdDetailQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
      dataSource.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const bufferPlanTargetSource = ref<any[]>([]);

const bufferPlanCoreConfig = computed<MozGridCoreProps>(() => {
  const rowField = (field: string, header: string) => ({ field, header, dataType: 'string', width: 100 });

  // if (currentWidgetSetting?.value?.detailType === 'OPER') → oper_id 부터
  // if (currentWidgetSetting?.value?.detailType === 'BUFFER') → buffer_id 부터

  return {
    mode: 'pivot',
    data: bufferPlanTargetSource.value,
    rowFields: [
      rowField('oper_group_id', t('text-oper_group_id')),
      rowField('oper_id', t('text-oper_id')),
      rowField('item_id', t('text-item_id')),
      rowField('plan_type', t('text-plan_type')),
    ],
    columnFields: [
      { field: 'month', header: t('text-plan_month'), dataType: 'string' },
      // { field: 'week', header: t('text-plan_week'), dataType: 'string' },
      { field: 'date', header: t('text-plan_date'), dataType: 'string' },
    ],
    valueFields: [
      {
        field: 'qty',
        header: t('text-qty'),
        dataType: 'number',
        aggregate: 'sum',
        width: 90,
        cellAttributes: ({ value }: { value: unknown }) =>
          typeof value === 'number' && value < 0 ? { class: 'negative-number' } : undefined,
      },
    ],
    ...pivotTotals.value,
  };
});

const addPrefix = (value: string) => {
  if (value === 'TARGET') {
    return '1_TARGET';
  }

  if (value === 'PLAN') {
    return '2_PLAN';
  }

  if (value === 'DIFF') {
    return '3_DIFF';
  }

  return value;
};

watchEffect(
  () => {
    if (planVer.value && bufferPlanTargetQuery.isSuccess.value) {
      if (bufferPlanTargetQuery.data.value) {
        bufferPlanTargetSource.value = bufferPlanTargetQuery.data.value.map((item: any) => ({
          ...item,
          // date: item.date === 'TOTAL' ? item.date : projectModule.convertToFormat('date', item.date),
          // week: item.week === 'TOTAL' ? item.week : projectModule.convertToFormat('dateWeek', item.week),
          // month: item.month === 'TOTAL' ? item.month : projectModule.convertToFormat('dateMonth', item.month),
          plan_type: addPrefix(item.plan_type),
        }));
      }
    } else if (bufferPlanTargetQuery.isError.value) {
      bufferPlanTargetSource.value = [];
      showMessage(t('msg-toast-get_error'), false);
    }
  },
  {
    flush: 'post',
  },
);

/**
 * BUTTON EVENT
 */

type FirstRowType = { usedTotal: number; isSummaryRow?: boolean };
type PlanDateType = { [key: string]: IPlanByProdDetailSource['outPlanQty'] };
type GroupByPlanDateType = Partial<IPlanByProdDetailSource & FirstRowType & PlanDateType>;

/**
 * EVENT
 */

/**
 * WATCH
 */

/**
 * demand info popup
 */
/**
 * 1920에 1242px 최대
 * 1280에  880px 최소
 * Popup 활성화할 때마다 동적으로 너비 결정
 */
const setWidth = (windowWidth: number) => {
  const width = windowWidth * (181 / 320) + 156;

  if (width <= 880) return 880;
  if (width >= 1242) return 1242;
  return width;
};

// 브라우저 크기 변화 감지용 반응형 변수
const windowWidth = ref(window.innerWidth);
const windowHeight = ref(window.innerHeight);

const targetPlanPopupWidth = computed(() => Math.floor(windowWidth.value * 0.8));
const targetPlanPopupHeight = computed(() => Math.floor(windowHeight.value * 0.9));

const popupWidth = ref(setWidth(window.innerWidth));

const demandInfoSource = ref<any[]>([]);
const pegInfoDetailSource = ref<any[]>([]);

// 수요 정보는 행 수만큼만 높이를 잡는다 (헤더 32px + 행 30px)
const demandInfoGridHeight = computed(() => 34 + Math.max(demandInfoSource.value.length, 1) * 30);

const demandInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: 'flat',
  keyFields: [ROW_KEY],
  data: demandInfoSource.value,
  headerHeight: 32,
  rowHeight: 30,
  fields: [
    // { id: 'demand_type', header: t('text-demand_type'), width: getWidthByKey('S2') },
    { id: 'demand_id', header: t('text-demand_id'), dataType: 'string', flex: 1 },
    { id: 'demand_item_id', header: t('text-item_id'), dataType: 'string', flex: 1 },
    { id: 'site_id', header: t('text-site_id'), dataType: 'string', flex: 1 },
    { id: 'buffer_id', header: t('text-buffer_id'), dataType: 'string', width: getWidthByKey('S3') },
    { id: 'prod_qty', header: t('text-prod_qty'), dataType: 'number', width: getWidthByKey('S3') },
    { id: 'demand_qty', header: t('text-demand_qty'), dataType: 'number', width: getWidthByKey('S3') },
    { id: 'due_date', header: t('text-due_date'), dataType: 'string', width: getWidthByKey('S2') },
  ].map((field) => ({ ...field, sortable: false })),
}));

const pegInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: 'flat',
  keyFields: [ROW_KEY],
  data: pegInfoDetailSource.value,
  fields: [
    { id: 'wip_id', header: t('text-wip_id'), dataType: 'string', width: getWidthByKey('S1') },
    { id: 'item_id', header: t('text-item_id'), dataType: 'string', width: getWidthByKey('S2') },
    { id: 'wip_qty', header: t('text-wip_qty'), dataType: 'number', width: getWidthByKey('S3') },
    { id: 'peg_qty', header: t('text-peg_qty'), dataType: 'number', width: getWidthByKey('S3') },
    { id: 'target_qty', header: t('text-target_qty'), dataType: 'number', width: getWidthByKey('S3') },
    { id: 'site_id', header: t('text-site_id'), dataType: 'string', width: getWidthByKey('S2') },
    { id: 'buffer_id', header: t('text-buffer_id'), dataType: 'string', width: getWidthByKey('S2') },
    { id: 'oper_id', header: t('text-oper_id'), dataType: 'string', width: getWidthByKey('S2') },
    { id: 'stage_id', header: t('text-stage_id'), dataType: 'string', width: getWidthByKey('S3'), hidden: true },
    { id: 'module_id', header: t('text-module_id'), dataType: 'string', width: getWidthByKey('S3'), hidden: true },
    { id: 'phase_no', header: t('text-phase_no'), dataType: 'string', width: getWidthByKey('S3'), hidden: true },
    //        PEG SEQ이 pegging_key가 맞는지 확인할 것!
    { id: 'routing_id', header: t('text-routing_id'), dataType: 'string', width: getWidthByKey('S2'), hidden: true },
    { id: 'pegging_key', header: t('text-pegging_key'), dataType: 'string', width: getWidthByKey('S1'), hidden: true },
  ].map((field) => ({
    ...field,
    sortable: false,
    cellAttributes: ({ rowIndex }: { rowIndex: number }) =>
      rowIndex % 2 === 1 ? { class: 'peg-detail-row-even' } : undefined,
  })),
}));

watchEffect(
  () => {
    if (demandInfoQuery.isSuccess.value && demandInfoQuery.data.value) {
      if (demandInfoQuery.data.value.length) {
        demandInfoSource.value = withRowKey(toRaw(demandInfoQuery.data.value)).map((elem: any) => {
          if (elem.due_date) {
            const [date, range] = elem.due_date.split(' ');
            return {
              ...elem,
              due_date: `${projectModule.convertToFormat('date', date)} ${range}`,
            };
          }
          return elem;
        });
      } else {
        demandInfoSource.value = [];
      }
    } else if (demandInfoQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
      demandInfoSource.value = [];
    }
  },
  {
    flush: 'post',
  },
);

watchEffect(
  () => {
    if (pegInfoDetailQuery.isSuccess.value && pegInfoDetailQuery.data.value) {
      if (pegInfoDetailQuery.data.value.length) {
        pegInfoDetailSource.value = withRowKey(toRaw(pegInfoDetailQuery.data.value));
      } else {
        pegInfoDetailSource.value = [];
      }
    } else if (pegInfoDetailQuery.isError.value) {
      showMessage(t('msg-toast-get_error'), false);
      pegInfoDetailSource.value = [];
    }
  },
  {
    flush: 'post',
  },
);

const bomNetworkInfos = ref<any[]>([]);
const demandInfos = ref<any>({});
const shortLogs = ref<any[]>([]);

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

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `createColumnMapForExport(coreConfig.fields)`로 처리 불가능 함
 */
/* const COLUMN_MAP = {
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
}; */

watch(
  () => detailQuery.data.value,
  () => {
    if (!detailQuery.data.value?.length) {
      dataSource.value = [];
    }
  },
);
</script>
<style lang="scss">
.plan-by-prod-popup-grid-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;

  .moz-tabs-container {
    display: block !important;
  }

  .mouse-point {
    cursor: pointer;
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

.pegging-report-sub5 {
  $border-color: #6a7184;
}

.peg-detail-outer-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.peg-detail-label {
  color: #6a7184;
  font-weight: 500;
  margin-bottom: 11px;
  font-size: 14px;
}

.peg-detail-section {
  flex: 1;

  display: flex;
  flex-direction: column;
  margin-top: 12px;
}

.peg-detail-grid-wrapper {
  flex: 1;
}

.peg-detail-row-even {
  background: #f8f8fd;
}

.peg-report-peg-empty {
  height: calc(100% - 50px);
  display: flex;
  gap: 24px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.text-underline {
  text-decoration: underline;
  color: #4568e0;
}

.plan-by-prod-popup-grid-summary {
  display: flex;
  justify-content: space-between;
}

.capa {
  line-height: 16px;
  margin-right: auto;
  font-size: 12px;
  // height: 28px;
  border: 1px solid #bbc6d9;
  border-radius: 4px;
  padding: 6px 10px;
  background-color: #f8f9fd;
  width: 100%;
  font-weight: 400;
  .dividor {
    padding: 0 8px;
    color: #bbc6d9;
  }
}

.grid-sort-reason {
  height: 100%;

  .grid-uom-type-viewer {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    color: #6a7184;
    font-weight: 400;
    font-size: 12px;
    margin-bottom: 3px;
  }
}

.negative-number {
  color: #dc5a5a !important;

  span {
    color: #dc5a5a !important;
  }
}

.prod-plan-ins-main,
.buffer-plan-target-main {
  .ps-cell.ps-cell-column-subtotal {
    background-color: #d6def8;
  }
}

.zoom-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  &:hover {
    background-color: #4568e017;
    border-radius: 4px;
  }
}
</style>
