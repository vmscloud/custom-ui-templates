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
    <ExtendPivotGrid
      v-memo="[dataSource, valueFields, getPlanByProdDetailQuery.isPending.value]"
      :name="`${currentMenu.menuID}-plan-by-prod_pivot`"
      :id="`${currentMenu.menuID}-plan-by-prod_pivot-id`"
      :use-preset="true"
      :emptyState="{
        isLoading: detailQuery.isPending.value && getPlanByProdDetailQuery.isPending.value,
        contentMsg: '',
      }"
      class="prod-plan-ins-main"
      ref="extendPivot"
      height="100%"
      :itemsSource="dataSource"
      :engine-option="{
        fields: fields,
        rowFields: rowFields,
        columnFields: columnFields,
        valueFields: valueFields,
        showRowTotals: dataState.showRowTotals,
        showColumnTotals: dataState.showColumnTotals,
        showZeros: dataState.showZeros,
        totalsBeforeData: dataState.totalsBeforeData,
      }"
      :initialized="onInitialized"
      :panel-on-update="updateView"
      :formatItem="formatItem"
      :pivotRef="extendPivot"
      :usePivotChart="false"
      :use-tool-box-setting="true"
      :loading="detailQuery.isPending.value && getPlanByProdDetailQuery.isPending.value"
      :setContextMenuProps="
        (ht: any) => ({
          customMenu: [
            {
              text: t('text-open-wip-info-detail-view'),
              function: () => (popup = true),
              disabled: () => false,
            },
            {
              text: t('text-open-prod-plan-detail-view'),
              function: () => (showTargetPlanView = true),
              disabled: () => false,
            },
          ],
        })
      "
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
    </ExtendPivotGrid>
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
        <ExtendFlexGrid
          :useFilter="false"
          :allowSorting="'None'"
          :itemsSource="demandInfoSource"
          :initialized="onInitializedDemandInfo"
          :formatItem="popupFormatItem"
          :isReadOnly="true"
          :allowPinning="false"
          :useContextMenu="false"
          :use-tool-box="false"
          :use-extend-footer="false"
          :name="`${currentMenu.menuID}_sub3_demand_info_modal`"
          :id="`${currentMenu.menuID}-sub3-demand-info-modal-id`"
          :use-preset="true"
        >
          <!-- <WjFlexGridColumn binding="demand_id" :header="t('text-demand_id')" :width="getWidthByKey('S2')" /> -->
          <WjFlexGridColumn binding="demand_id" :header="t('text-demand_id')" :width="'*'" />
          <!-- <WjFlexGridColumn binding="demand_type" :header="t('text-demand_type')" :width="getWidthByKey('S2')" /> -->
          <WjFlexGridColumn binding="demand_item_id" :header="t('text-item_id')" :width="'*'" />
          <WjFlexGridColumn binding="site_id" :header="t('text-site_id')" :width="'*'" />
          <WjFlexGridColumn binding="buffer_id" :header="t('text-buffer_id')" :width="getWidthByKey('S3')" />
          <WjFlexGridColumn binding="prod_qty" :header="t('text-prod_qty')" :width="getWidthByKey('S3')" />
          <WjFlexGridColumn binding="demand_qty" :header="t('text-demand_qty')" :width="getWidthByKey('S3')" />
          <WjFlexGridColumn
            binding="due_date"
            :header="t('text-due_date')"
            :width="getWidthByKey('S2')"
            dataType="String"
          />
        </ExtendFlexGrid>
      </div>
      <div class="peg-detail-section">
        <div class="peg-detail-label">
          {{ t('text-popup-peg_info') }}
        </div>
        <div class="peg-detail-grid-wrapper">
          <ExtendFlexGrid
            :useFilter="false"
            :allowSorting="'None'"
            :itemsSource="pegInfoDetailSource"
            :initialized="onInitializedPegInfo"
            :formatItem="formatItemDetail"
            :isReadOnly="true"
            :allowPinning="false"
            :useContextMenu="false"
            :height="340"
            :use-tool-box="false"
            :name="`${currentMenu.menuID}_sub3_peg_info_modal`"
            :id="`${currentMenu.menuID}-sub3-peg-info-modal-id`"
            :use-preset="true"
          >
            <WjFlexGridColumn binding="wip_id" :header="t('text-wip_id')" :width="getWidthByKey('S1')" />
            <WjFlexGridColumn binding="item_id" :header="t('text-item_id')" :width="getWidthByKey('S2')" />
            <WjFlexGridColumn binding="wip_qty" :header="t('text-wip_qty')" :width="getWidthByKey('S3')" />
            <WjFlexGridColumn binding="peg_qty" :header="t('text-peg_qty')" :width="getWidthByKey('S3')" />
            <WjFlexGridColumn binding="target_qty" :header="t('text-target_qty')" :width="getWidthByKey('S3')" />
            <WjFlexGridColumn binding="site_id" :header="t('text-site_id')" :width="getWidthByKey('S2')" />
            <WjFlexGridColumn binding="buffer_id" :header="t('text-buffer_id')" :width="getWidthByKey('S2')" />
            <WjFlexGridColumn binding="oper_id" :header="t('text-oper_id')" :width="getWidthByKey('S2')" />
            <WjFlexGridColumn
              binding="stage_id"
              :header="t('text-stage_id')"
              :width="getWidthByKey('S3')"
              :visible="false"
            />
            <WjFlexGridColumn
              binding="module_id"
              :header="t('text-module_id')"
              :width="getWidthByKey('S3')"
              :visible="false"
            />
            <WjFlexGridColumn
              binding="phase_no"
              :header="t('text-phase_no')"
              :width="getWidthByKey('S3')"
              :visible="false"
            />
            <!--        PEG SEQ이 pegging_key가 맞는지 확인할 것! -->
            <WjFlexGridColumn
              binding="routing_id"
              :header="t('text-routing_id')"
              :width="getWidthByKey('S2')"
              :visible="false"
            />
            <WjFlexGridColumn
              binding="pegging_key"
              :header="t('text-pegging_key')"
              :width="getWidthByKey('S1')"
              :visible="false"
            />
          </ExtendFlexGrid>
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
            <ExtendPivotGrid
              v-memo="[bufferPlanTargetSource, valueFields, bufferPlanTargetQuery.isFetching.value]"
              :name="`${currentMenu.menuID}-buffer-plan-target_pivot`"
              :id="`${currentMenu.menuID}-buffer-plan-target_pivot-id`"
              :use-preset="true"
              :emptyState="{
                isLoading: bufferPlanTargetQuery.isFetching.value,
              }"
              class="buffer-plan-target-main"
              ref="bufferPlanExtendPivot"
              height="100%"
              :itemsSource="bufferPlanTargetSource"
              :engine-option="{
                fields: bufferPlanFields,
                rowFields: bufferPlanRowFields,
                columnFields: bufferPlanColumnFields,
                valueFields: bufferPlanValueFields,
                showRowTotals: bufferPlanDataState.showRowTotals,
                showColumnTotals: bufferPlanDataState.showColumnTotals,
                showZeros: bufferPlanDataState.showZeros,
                totalsBeforeData: bufferPlanDataState.totalsBeforeData,
              }"
              :initialized="onInitializedBufferPlan"
              :panel-on-update="updateViewBufferPlan"
              :formatItem="formatItemBufferPlan"
              :pivotRef="bufferPlanExtendPivot"
              :usePivotChart="false"
              :use-tool-box-setting="false"
              :use-tool-box="false"
              :use-filter="false"
              :use-sorting="false"
              :loading="bufferPlanTargetQuery.isFetching.value"
            >
            </ExtendPivotGrid>
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
import { DataType } from '@vmscloud/moz-wijmo-grid/wijmo';
import { CellType, FlexGrid, FormatItemEventArgs } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { PivotGrid, ShowTotals } from '@vmscloud/moz-wijmo-grid/wijmo.olap';
import { WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import { EmptyState, Pane, Popup, SplitPane } from '@vmscloud/moz-ui-components';
import { ExtendFlexGrid, ExtendPivotGrid, type ExtendGrid } from '@vmscloud/moz-wijmo-grid';
import { IconCollapseArrow, IconExpandArrow } from '@moz-shared/icons';
import { getWidthByKey, isDataCell } from '@vmscloud/moz-wijmo-grid/utils';
import { getValue, showMessage } from '@moz-shared/utils';
import dayjs from 'dayjs';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import { computed, inject, onBeforeUnmount, reactive, Ref, ref, toRaw, watch, watchEffect } from 'vue';
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
const dataState: {
  menuName: string;
  showRowTotals: ShowTotals;
  showColumnTotals: ShowTotals;
  showZeros: boolean;
  totalsBeforeData: boolean;
} = reactive({
  menuName: '',
  showRowTotals: ShowTotals.None,
  showColumnTotals: ShowTotals.GrandTotals,
  showZeros: false,
  totalsBeforeData: false,
});

const fields = computed(() => {
  const defaultFields: any[] = [
    {
      binding: 'itemID',
      header: t('text-item_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'bufferSeq',
      header: t('text-buffer_seq'),
      dataType: DataType.Number,
      align: 'right',
    },
    {
      binding: 'bufferID',
      header: t('text-buffer_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'operGroupID',
      header: t('text-oper_group_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'operID',
      header: t('text-oper_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'siteID',
      header: t('text-site_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'itemType',
      header: t('text-item_type'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'wipQty',
      header: t('text-default-wip_qty'),
      dataType: DataType.Number,
      align: 'right',
    },
    {
      binding: 'pegQty',
      header: t('text-peg_qty'),
      dataType: DataType.Number,
      align: 'right',
    },
    {
      binding: 'usedTotalQty',
      header: t('text-used_total'),
      dataType: DataType.Number,
      align: 'right',
    },
    {
      binding: 'outPlanQty',
      header: t('text-out_plan_qty'),
      dataType: DataType.Number,
      align: 'right',
    },
    {
      binding: 'planDate',
      header: t('text-plan_date'),
      dataType: DataType.String,
      align: 'center',
    },
    // {
    //   binding: 'planWeek',
    //   header: t('text-plan_week'),
    //   dataType: DataType.String,
    //   align: 'center',
    // },
    {
      binding: 'planMonth',
      header: t('text-plan_month'),
      dataType: DataType.String,
      align: 'center',
    },
  ] satisfies any[];

  return defaultFields;
});

const rowFields = computed(() => {
  const baseRows = [
    t('text-item_id'),
    t('text-site_id'),
    t('text-item_type'),
    t('text-default-wip_qty'),
    t('text-peg_qty'),
    t('text-used_total'),
  ];

  return [t('text-oper_group_id'), t('text-oper_id'), ...baseRows];

  // if (currentWidgetSetting?.value?.detailType === 'OPERGROUP') {
  //   return [t('text-oper_group_id'), t('text-oper_id'), ...baseRows];
  // }

  // if (currentWidgetSetting?.value?.detailType === 'OPER') {
  //   return [t('text-oper_id'), ...baseRows];
  // }

  // if (currentWidgetSetting?.value?.detailType === 'BUFFER') {
  //   return [t('text-buffer_seq'), t('text-buffer_id'), ...baseRows];
  // }

  // return baseRows;
});

const columnFields: Ref<string[]> = ref([
  t('text-plan_month'),
  // t('text-plan_week'),
  t('text-plan_date'),
]);
// const columnFields: Ref<string[]> = ref([t('text-plan_date')]);
const valueFields: Ref<string[]> = ref([t('text-out_plan_qty')]);

/**
 * @todo 백엔드 API 스네이크 케이스로 받고 하드코딩된 로직 제거
 * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
 */

const detailDataSource = ref<GroupByPlanDateType[]>([]); // DataSource 객체 선언
const planByProdSummarySource = ref<any>();

// region PIVOT CODES
const extendPivot = ref();
const pivot = ref();

const targetPlanPivot = ref();

const bufferPlanExtendPivot = ref();

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

// -----------------------------------------Pivot Grid-----------------------------------------
// GRID INITIALIZE
const onInitialized = (_pivot: PivotGrid) => {
  _pivot.rowHeaders.columns.defaultSize = 100;
  // _pivot.columns.defaultSize = 50;
  pivot.value = _pivot;

  _pivot.loadedRows.addHandler(() => {
    toggleCollapsibleSubtotals();
  });
};

// 펼치기/접기 토글 함수
const toggleCollapsibleSubtotals = () => {
  if (pivot.value) {
    // PivotGrid의 collapsibleSubtotals 속성을 체크박스 상태에 따라 설정
    pivot.value.collapsibleSubtotals = localState.collapsibleSubtotals;

    // collapsibleSubtotals가 true일 때 열에서만 부분합 표시, 행에서는 부분합 없음
    if (localState.collapsibleSubtotals) {
      // 행은 부분합 없음, 열만 부분합 표시
      dataState.showRowTotals = ShowTotals.None;
      dataState.showColumnTotals = ShowTotals.Subtotals;

      // PivotEngine의 설정도 업데이트
      if (pivot.value.engine) {
        pivot.value.engine.showRowTotals = ShowTotals.None;
        pivot.value.engine.showColumnTotals = ShowTotals.Subtotals;
      }
    } else {
      dataState.showRowTotals = ShowTotals.None;
      dataState.showColumnTotals = ShowTotals.GrandTotals;

      // PivotEngine의 설정도 업데이트
      if (pivot.value.engine) {
        pivot.value.engine.showRowTotals = ShowTotals.None;
        pivot.value.engine.showColumnTotals = ShowTotals.GrandTotals;
      }
    }

    // 그리드 새로고침
    pivot.value.invalidate();

    const collapse = () => {
      (pivot.value as PivotGrid).collapseColumnsToLevel(2);
      (pivot.value as PivotGrid).collectionView?.collectionChanged.removeHandler(collapse);
    };
    (pivot.value as PivotGrid).collectionView?.collectionChanged.addHandler(collapse);
  }
};

const onInitializedBufferPlan = (_pivot: PivotGrid) => {
  _pivot.rowHeaders.columns.defaultSize = 100;
  _pivot.columnHeaders.columns.defaultSize = 90;

  targetPlanPivot.value = _pivot;
};

onBeforeUnmount(() => {
  if (pivot.value) {
    pivot.value?.dispose();
  }
});

// pivot panel update
const updateView = () => {
  if (extendPivot.value) {
    extendPivot.value.hidePanel();
  } else {
    showMessage(t('msg-toast-first_search'), false);
  }
};

const updateViewBufferPlan = () => {
  if (bufferPlanExtendPivot.value) {
    bufferPlanExtendPivot.value.hidePanel();
  } else {
    showMessage(t('msg-toast-first_search'), false);
  }
};

const formatItem = (s: PivotGrid, e: any) => {
  // topLeft 영역에서 row field 이름들 확인
  if (e.panel.cellType === CellType.TopLeft) {
    e.cell.style.justifyContent = 'start';
  }
};

const formatItemBufferPlan = (s: PivotGrid, e: any) => {
  // plan_type 값들의 prefix 제거 (모든 숫자-텍스트 패턴에서 제거)
  if (e.cell.textContent) {
    const text = e.cell.textContent;
    const number = Number(text);

    if (!isNaN(number) && number < 0) {
      e.cell.classList.add('negative-number');
    }

    // 일단 모든 "숫자-" 패턴을 제거해보기
    if (/^\d+_/.test(text)) {
      e.cell.textContent = text.replace(/^\d+_/, '');
    }
  }
};

const demandInfoGrid = ref<FlexGrid | null>(null);
const demandInfoExtendGrid = ref<ExtendGrid | null>(null); // Wijmo Grid 확장 기능

const onInitializedDemandInfo = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  demandInfoGrid.value = flexGrid;
  demandInfoExtendGrid.value = _extendGrid;
};

const pegInfoGrid = ref<FlexGrid | null>(null);
const pegInfoExtendGrid = ref<ExtendGrid | null>(null); // Wijmo Grid 확장 기능

const onInitializedPegInfo = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  pegInfoGrid.value = flexGrid;
  pegInfoExtendGrid.value = _extendGrid;
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

        // 데이터 로드 후 펼치기/접기 기능 다시 적용
        setTimeout(() => {
          if (localState.collapsibleSubtotals) {
            toggleCollapsibleSubtotals();
          }
        }, 100);
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
const bufferPlanDataState: {
  menuName: string;
  showRowTotals: ShowTotals;
  showColumnTotals: ShowTotals;
  showZeros: boolean;
  totalsBeforeData: boolean;
} = reactive({
  menuName: '',
  showRowTotals: ShowTotals.None,
  showColumnTotals: ShowTotals.None,
  showZeros: false,
  totalsBeforeData: false,
});

// 펼치기/접기 토글 함수
const setTargetPlanSubtotals = () => {
  if (targetPlanPivot.value) {
    // PivotGrid의 collapsibleSubtotals 속성을 체크박스 상태에 따라 설정
    targetPlanPivot.value.collapsibleSubtotals = localState.collapsibleSubtotals;

    // collapsibleSubtotals가 true일 때 열에서만 부분합 표시, 행에서는 부분합 없음
    if (localState.collapsibleSubtotals) {
      // 행은 부분합 없음, 열만 부분합 표시
      bufferPlanDataState.showRowTotals = ShowTotals.None;
      bufferPlanDataState.showColumnTotals = ShowTotals.Subtotals;

      // PivotEngine의 설정도 업데이트
      if (targetPlanPivot.value.engine) {
        targetPlanPivot.value.engine.showRowTotals = ShowTotals.None;
        targetPlanPivot.value.engine.showColumnTotals = ShowTotals.Subtotals;
      }
    } else {
      bufferPlanDataState.showRowTotals = ShowTotals.None;
      bufferPlanDataState.showColumnTotals = ShowTotals.GrandTotals;

      // PivotEngine의 설정도 업데이트
      if (targetPlanPivot.value.engine) {
        targetPlanPivot.value.engine.showRowTotals = ShowTotals.None;
        targetPlanPivot.value.engine.showColumnTotals = ShowTotals.GrandTotals;
      }
    }

    // 그리드 새로고침
    targetPlanPivot.value.invalidate();
  }
};

const bufferPlanFields = computed(() => {
  const defaultFields: any[] = [
    {
      binding: 'buffer_id',
      header: t('text-buffer_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'oper_group_id',
      header: t('text-oper_group_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'oper_id',
      header: t('text-oper_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'qty_uom',
      header: t('text-qty_uom'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'plan_type',
      header: t('text-plan_type'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'lot_id',
      header: t('text-lot_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'date',
      header: t('text-plan_date'),
      dataType: DataType.String,
      align: 'left',
    },
    // {
    //   binding: 'week',
    //   header: t('text-plan_week'),
    //   dataType: DataType.String,
    //   align: 'left',
    // },
    {
      binding: 'month',
      header: t('text-plan_month'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'qty',
      header: t('text-qty'),
      dataType: DataType.Number,
      align: 'right',
    },
    {
      binding: 'item_id',
      header: t('text-item_id'),
      dataType: DataType.String,
      align: 'left',
    },
    {
      binding: 'site_id',
      header: t('text-site_id'),
      dataType: DataType.String,
      align: 'left',
    },
  ] satisfies any[];

  return defaultFields;
});

const bufferPlanRowFields = computed(() => {
  const baseRows = [t('text-item_id'), t('text-plan_type')];

  return [t('text-oper_group_id'), t('text-oper_id'), ...baseRows];

  // if (currentWidgetSetting?.value?.detailType === 'OPERGROUP') {
  //   return [t('text-oper_group_id'), t('text-oper_id'), ...baseRows];
  // }

  // if (currentWidgetSetting?.value?.detailType === 'OPER') {
  //   return [t('text-oper_id'), ...baseRows];
  // }

  // if (currentWidgetSetting?.value?.detailType === 'BUFFER') {
  //   return [t('text-buffer_id'), ...baseRows];
  // }

  // return baseRows;
});

const bufferPlanColumnFields: Ref<string[]> = ref([
  t('text-plan_month'),
  // t('text-plan_week'),
  t('text-plan_date'),
]);
const bufferPlanValueFields: Ref<string[]> = ref([t('text-qty')]);

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

        setTimeout(() => {
          if (localState.collapsibleSubtotals) {
            setTargetPlanSubtotals();
          }
        }, 100);
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

const popupFormatItem = (s: FlexGrid, e: FormatItemEventArgs) => {
  //
  if (!isDataCell(s, e)) return;
  e.cell.style.borderBottom = 'none';
};

const demandInfoSource = ref<any[]>([]);
const pegInfoDetailSource = ref<any[]>([]);

watchEffect(
  () => {
    if (demandInfoQuery.isSuccess.value && demandInfoQuery.data.value) {
      if (demandInfoQuery.data.value.length) {
        demandInfoSource.value = toRaw(demandInfoQuery.data.value).map((elem: any) => {
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

const formatItemDetail = (s: FlexGrid, e: any) => {
  if (!isDataCell(s, e)) return;

  const rowNum = e.row;
  if (rowNum % 2 === 1) {
    e.cell.classList.add('peg-detail-row-even');
  }
};

watchEffect(
  () => {
    if (pegInfoDetailQuery.isSuccess.value && pegInfoDetailQuery.data.value) {
      if (pegInfoDetailQuery.data.value.length) {
        pegInfoDetailSource.value = toRaw(pegInfoDetailQuery.data.value);
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
 * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
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

  .wj-flexgrid .wj-cells .wj-row {
    &:nth-child(n) {
      .wj-cell.ratio-short {
        // 흰 배경일때 ratio-short 일때
        background-color: #f6d5d5 !important;

        // 그 상태에서 clicked 했을때
        &.aleatorik-clicked-state {
          background-color: #eae0ec !important;
        }
      }

      .wj-cell.ratio-late {
        // 흰 배경일때 ratio-late 일때
        background-color: #fde6c8 !important;

        // 그 상태에서 clicked 했을때
        &.aleatorik-clicked-state {
          background-color: #eae0ec !important;
        }
      }
    }

    &:nth-child(2n) {
      .wj-cell.ratio-short {
        // 파란 배경에서 ratio-short 일때
        background-color: #f1d0d4 !important;

        &.aleatorik-clicked-state {
          background-color: #e5daea !important;
        }
        .ratio-short-col {
          color: #dc5a5a;
        }
      }

      .wj-cell.ratio-late {
        // 파란 배경에서 ratio-late 일때
        background-color: #f8e1c7 !important;

        &.aleatorik-clicked-state {
          background-color: #e5daea !important;
        }
      }
    }

    .wj-cell.ratio-short:not(.wj-header) {
      &.wj-state-multi-selected,
      &.wj-state-active {
        background-color: #d4cde8 !important;
      }
    }

    &:hover {
      .wj-cell.ratio-short:not(.wj-header) {
        background-color: #d4cde8 !important;
      }
    }

    .wj-cell.ratio-late:not(.wj-header) {
      &.wj-state-multi-selected,
      &.wj-state-active {
        background-color: #d4cde8 !important;
      }
    }

    &:hover {
      .wj-cell.ratio-late:not(.wj-header) {
        background-color: #d4cde8 !important;
      }
    }
  }

  .ratio-short-col span {
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
  .wj-colheaders {
    .wj-cell.wj-header {
      //   justify-content: center;
      .spacer {
        display: none;
      }
    }
  }

  .wj-colheaders {
    .wj-row {
      .wj-header.after-due-date {
        border-left: 2px solid #dc5a5a;
      }
    }
  }

  .wj-cells {
    .wj-row {
      .wj-cell {
        &.summary-row {
          background-color: #d6def8;
          font-weight: 500;
        }

        &.late {
          color: #dc5a5a;
          span {
            color: #dc5a5a;
          }
        }

        &.after-due-date {
          border-left: 2px solid #dc5a5a;
        }
      }
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
  span {
    color: #dc5a5a !important;
  }
}

.wj-aggregate:not(.wj-header) {
  background-color: white !important;
}

.wj-cell:not(.wj-header):not(.wj-aggregate) + .wj-aggregate {
  background-color: #d6def8 !important;
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
