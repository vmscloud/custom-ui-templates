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
          <ExtendFlexGrid
            name="ResBasedPlanAnalysis"
            width="100%"
            height="100%"
            class="prod-plan-ins-master"
            :emptyState="{
              isLoading: masterQuery.isPending.value,
              useImg: false,
            }"
            :autoGenerateColumns="false"
            :itemsSource="masterDataSource"
            :initialized="onInitialized"
            :allowSorting="'None'"
            :isReadOnly="true"
            :setContextMenuProps="{
              useFlexGridSetting: false,
              useFilter: false,
              useGroupColumn: false,
              useViewSelectColumn: false,
              useExportExcel: true,
              useSum: true,
              onExportOriginalData: () =>
                downloadBigData({
                  column_map: COLUMN_MAP,
                  file_name: `${t(`text-popup-prod_plan_ins_detail_popup`)}_${summaryLoadParams.planVer}`,
                  data_method: 'POST',
                  data_parameter: JSON.stringify(summaryLoadParams),
                  api_key: summaryApiKey,
                }),
            }"
            :selectionChanged="onMasterSelectionChanged"
            :formatItem="masterFormatItem"
            :use-tool-box="false"
            :loading="masterQuery.isPending.value"
            :use-sort="false"
          >
            <ExtendGridContextOpenNewTab
              :route="
                (item: any) => {
                  return {
                    path: `/sp/BomMapPlanView`,
                    query: {
                      planCycle: planCycleID,
                      planVer: planVer,
                      demandItemID: item?.demandItemID,
                      demandID: item?.demandID,
                    },
                  };
                }
              "
              :disabled="
                (item: any) => {
                  return !(item?.demandItemID || item?.itemID || item?.demandID);
                }
              "
              :label="t('text-context-open_bom_map_plan_view')"
            />
            <WjFlexGridColumn binding="demandID" :header="t('text-demand_id')" :width="getWidthByKey('DF')" />
            <WjFlexGridColumn binding="demandItemID" :header="t('text-demand_item_id')" :width="getWidthByKey('DF')" />
            <WjFlexGridColumn binding="demandItemName" :header="t('text-demand_item_name')" :width="getWidthByKey('DF')" />
            <WjFlexGridColumn binding="custName" :header="t('text-cust_name')" :width="getWidthByKey('D1')" />
            <WjFlexGridColumn
              binding="demandQty"
              :header="t('text-demand_qty')"
              dataType="Number"
              :width="getWidthByKey('D2')"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              binding="dueDate"
              :header="t('text-due_date')"
              dataType="Date"
              :format="projectModule.formatGrid('date')"
              align="center"
              :width="getWidthByKey('D2')"
            />
            <WjFlexGridColumn
              binding="warehousingDate"
              :header="t('text-upper-warehousing_date')"
              dataType="Date"
              :format="projectModule.formatGrid('date')"
              align="center"
              :width="getWidthByKey('D2')"
            />
            <WjFlexGridColumn
              binding="shipmentDate"
              :header="t('text-shipment_date')"
              dataType="Date"
              :width="getWidthByKey('D2')"
              :format="projectModule.formatGrid('date')"
              align="center"
            />
            <WjFlexGridColumn
              binding="dateDiff"
              :header="`${t('text-due_delay')}(${t('text-day')})`"
              :width="getWidthByKey('D2')"
            />
            <WjFlexGridColumn
              binding="rtfRatio"
              :header="t('text-rtf_ratio')"
              dataType="Number"
              aggregate="Avg"
              :width="getWidthByKey('D2')"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              binding="onTimeQty"
              :header="t('text-on_time_qty')"
              dataType="Number"
              :width="getWidthByKey('D2')"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              binding="lateQty"
              :header="t('text-late_qty')"
              dataType="Number"
              :width="getWidthByKey('D2')"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              :width="getWidthByKey('N2')"
              binding="shortQty"
              :header="t('text-short_qty')"
              dataType="Number"
              :format="projectModule.formatGrid('qty')"
              align="right"
            />
          </ExtendFlexGrid>
          <ExtendFlexGrid
            name="ResBasedPlanAnalysis"
            width="100%"
            height="100%"
            class="prod-plan-ins-detail"
            :autoGenerateColumns="false"
            :itemsSource="detailDataSource"
            :initialized="onInitializedDetail"
            :allowSorting="'None'"
            :isReadOnly="true"
            :setContextMenuProps="{
              useFlexGridSetting: false,
              useFilter: false,
              useGroupColumn: false,
              useViewSelectColumn: false,
              useExportExcel: true,
              useSum: true,
              onExportOriginalData: () =>
                downloadBigData({
                  column_map: DETAIL_COLUMN_MAP,
                  file_name: `${t(`text-popup-prod_plan_ins_detail_popup`)}_${detailLoadParams.planVer}`,
                  data_method: 'POST',
                  data_parameter: JSON.stringify(detailLoadParams),
                  api_key: `${detailApiKey}/Excel`,
                }),
            }"
            :formatItem="detailFormatItem"
            :use-tool-box="false"
            :use-extend-footer="true"
            :loading="detailQuery.isPending.value"
            :use-sort="false"
          >
            <WjFlexGridColumn binding="itemID" :header="t('text-item_id')" :width="getWidthByKey('D2')" />
            <WjFlexGridColumn binding="itemName" :header="t('text-item_name')" :width="getWidthByKey('D2')" />
            <WjFlexGridColumn binding="bufferID" :header="t('text-buffer_id')" :width="getWidthByKey('N3')" />
            <WjFlexGridColumn binding="siteID" :header="t('text-site_id')" :width="getWidthByKey('N3')" />
            <WjFlexGridColumn binding="itemType" :header="t('text-type')" :width="getWidthByKey('N3')" />
            <WjFlexGridColumn
              binding="wipQty"
              :header="t('text-boh')"
              :width="getWidthByKey('N3')"
              dataType="Number"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              binding="pegQty"
              :header="t('text-use')"
              :width="getWidthByKey('N3')"
              dataType="Number"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              binding="usedTotal"
              :header="t('text-used_total')"
              :width="getWidthByKey('N3')"
              dataType="Number"
              :format="projectModule.formatGrid('qty')"
            />
            <WjFlexGridColumn
              v-for="col in itemColumns"
              :binding="col.binding"
              :header="t(col.header)"
              :width="col.width"
              :align="col.align"
              :format="projectModule.formatGrid('qty')"
            />
          </ExtendFlexGrid>
        </div>
      </template>
    </Tab>
  </Popup>
</template>
<script setup lang="ts">
import ExtendGridContextOpenNewTab from './ExtendGridContextOpenNewTab.vue';
import PopupController from './PopupController.vue';
import { apiCall, downloadBigData } from '../adapters/stores';
import { useProjectInfoStore } from '../adapters/stores';
import { useLoaderParams } from '../adapters/utils';
import { IPlanByProdDetailSource, IPlanByProdMasterSource } from '../adapters/types';
import { AllowMerging, CellRange, FlexGrid, GridPanel, MergeManager, Row } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import { Popup, Radio, Tab } from '@vmscloud/moz-ui-components';
import { ExtendFlexGrid } from '@vmscloud/moz-wijmo-grid';
import { ExtendGrid } from '@vmscloud/moz-wijmo-grid';

import { getWidthByKey, isDataCell } from '@vmscloud/moz-wijmo-grid/utils';
import { showMessage } from '@moz-shared/utils';
import { useMutation } from '@tanstack/vue-query';
import dayjs from 'dayjs';
import { debounce, groupBy } from 'es-toolkit';
import { useTranslation } from 'i18next-vue';
import { computed, nextTick, onBeforeUnmount, onMounted, onUnmounted, reactive, ref, toRefs, watch } from 'vue';

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
 * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
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
 * 서버에서 받는 케이스가 안 맞아서 `excelModule.createColumnMapForExport(grid as FlexGrid)`으로 처리 불가능 함
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

const masterGrid = ref<FlexGrid | null>(null); // Wijmo Grid
const masterExtendGrid = ref<ExtendGrid | null>(null); // Wijmo Grid 확장 기능
const detailGrid = ref<FlexGrid | null>(null); // Wijmo Grid
const detailExtendGrid = ref<ExtendGrid | null>(null); // Wijmo Grid 확장 기능
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

class CustomMergeManager extends MergeManager {
  getMergedRange(panel: GridPanel, r: number, c: number) {
    // create basic cell range
    const rng = new CellRange(r, c);

    if (panel === panel.grid.cells) {
      if (r <= 0 && c <= 4) {
        for (let i = rng.col; i < panel.columns.length - 1; i++) {
          if (panel.getCellData(rng.row, i, true) !== panel.getCellData(rng.row, i + 1, true)) break;
          rng.col2 = i + 1;
        }
        for (let i = rng.col; i > 0; i--) {
          if (panel.getCellData(rng.row, i, true) !== panel.getCellData(rng.row, i - 1, true)) break;
          rng.col = i - 1;
        }
      }
      return rng;
    }

    //
    // expand left/right
    for (let i = rng.col; i < panel.columns.length - 1; i++) {
      if (panel.getCellData(rng.row, i, true) !== panel.getCellData(rng.row, i + 1, true)) break;
      rng.col2 = i + 1;
    }
    for (let i = rng.col; i > 0; i--) {
      if (panel.getCellData(rng.row, i, true) !== panel.getCellData(rng.row, i - 1, true)) break;
      rng.col = i - 1;
    }

    // expand up/down
    for (let i = rng.row; i < panel.rows.length - 1; i++) {
      if (panel.getCellData(i, rng.col, true) !== panel.getCellData(i + 1, rng.col, true)) break;
      rng.row2 = i + 1;
    }
    for (let i = rng.row; i > 0; i--) {
      if (panel.getCellData(i, rng.col, true) !== panel.getCellData(i - 1, rng.col, true)) break;
      rng.row = i - 1;
    }

    // done
    return rng;
  }
}

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

const masterFocusColumnByDemandID = () => {
  if (!masterGrid.value?.collectionView?.items) return;
  let focusTargetIndex = -1;

  if (data.value?.demandIDs?.length) {
    focusTargetIndex = masterGrid.value.collectionView?.items.findIndex(
      (elem) => elem.demandID === data.value?.demandIDs?.[0],
    );
  } else {
    const prodQty = data.value?.prodQty ?? 0;
    const demandQty = data.value?.demandQty ?? 0;

    // 생산계획량과 요구수량 모두 0이면 그냥 첫번째 선택
    // selectIdx = 0;

    // 생산계획량이 0을 초과하면 생산완료일에 해당하는 첫번째
    if (prodQty) {
      focusTargetIndex = masterGrid.value.collectionView?.items.findIndex(
        (elem) => elem.shipmentDate === data.value?.date,
      );
    }

    // 생산계획량이 0이면 납기일에 해당하는 첫번째 선택
    if (!prodQty && demandQty) {
      focusTargetIndex = masterGrid.value.collectionView?.items.findIndex(
        (elem) => dayjs(elem.dueDate).format('YYYY-MM-DD') === data.value?.date,
      );
    }

    // masterGrid 가 정합성이 깨져 -1이 발생한 경우 첫번째 선택으로 초기화
    if (focusTargetIndex === -1) {
      focusTargetIndex = 0;
      onDetailLoad(masterGrid.value.collectionView.items[0]);
    }
  }

  if (focusTargetIndex !== -1) {
    masterGrid.value?.select(new CellRange(focusTargetIndex, 0), true);
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
    if (!masterGrid.value || !masterGrid.value.collectionView?.items.length) {
      return { dueDateMidIdx: -1, shipmentDateMidIdx: -1 };
    }

    // plan_date와의 일 수 차이가 0일인 날짜가 1순위이므로 target은 0이다.
    const target = 0;
    let dueDateStart = 0;
    let dueDateEnd = masterGrid.value.collectionView?.items.length - 1;
    let dueDateMidIdx = -1;
    let dueDateFinishedExplore = false;

    let shipmentDateStart = 0;
    let shipmentDateEnd = masterGrid.value.collectionView?.items.length - 1;
    let shipmentDateMidIdx = -1;
    let shipmentDateFinishedExplore = false;

    while (
      dueDateStart < dueDateEnd &&
      shipmentDateStart < shipmentDateEnd &&
      (!dueDateFinishedExplore || !shipmentDateFinishedExplore)
    ) {
      if (!dueDateFinishedExplore) {
        dueDateMidIdx = Math.floor((dueDateStart + dueDateEnd) / 2);
        if (!masterGrid.value.collectionView?.items[dueDateMidIdx]?.dueDate) {
          dueDateMidIdx = -1;
          break;
        }
      }

      if (!shipmentDateFinishedExplore) {
        shipmentDateMidIdx = Math.floor((shipmentDateStart + shipmentDateEnd) / 2);
        if (!masterGrid.value.collectionView?.items[shipmentDateMidIdx]?.shipmentDate) {
          shipmentDateMidIdx = -1;
          break;
        }
      }

      const dueDateMidDiff = Number(
        dayjs(masterGrid.value.collectionView?.items[dueDateMidIdx].dueDate).diff(dayjs(targetDate), 'day'),
      );
      const shipmentDateMidDiff = Number(
        dayjs(masterGrid.value.collectionView?.items[shipmentDateMidIdx].shipmentDate).diff(dayjs(targetDate), 'day'),
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
      Number(dayjs(masterGrid.value.collectionView?.items[dueDateMidIdx].dueDate).diff(dayjs(targetDate), 'day')) < 0 &&
      !masterGrid.value.collectionView?.items[dueDateMidIdx + 1]?.dueDate
    ) {
      dueDateMidIdx += 1;
    }
    while (
      shipmentDateMidIdx !== -1 &&
      Number(
        dayjs(masterGrid.value.collectionView?.items[shipmentDateMidIdx].shipmentDate).diff(dayjs(targetDate), 'day'),
      ) < 0 &&
      masterGrid.value.collectionView?.items[shipmentDateMidIdx + 1]?.shipmentDate
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
      dayjs(masterGrid.value.collectionView?.items[dueDateMidIdx]?.dueDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) === 0
    ) {
      focusTargetIndex = dueDateMidIdx;
    } else if (
      // 2 순위 : 생산 완료일 = 선택한 날짜
      shipmentDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[shipmentDateMidIdx]?.shipmentDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) === 0
    ) {
      focusTargetIndex = shipmentDateMidIdx;
    } else if (
      // 3 순위 : 선택한 날짜 < 생산 완료일 중에서, 가장 생산 완료일이 작은 Demand
      shipmentDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[shipmentDateMidIdx]?.shipmentDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) >= 0
    ) {
      focusTargetIndex = shipmentDateMidIdx;
    } else if (
      // 4 순위 : 선택한 날짜 < 납기일 중에서, 가장 납기일이 작은 Demand
      dueDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[dueDateMidIdx]?.dueDate).diff(
        dayjs(autoFocusProps.value.targetDate),
        'day',
      ) >= 0
    ) {
      focusTargetIndex = dueDateMidIdx;
    } else {
      // 5 순위 : 마지막 Demand (여기까지 왔으면, 되게 뒤쪽 날짜를 선택한 상황이라서, 마지막 Demand 선택하면 됨)
      focusTargetIndex = masterGrid.value.collectionView?.items.length - 1;
    }
  } else {
    // 이진 탐색 실행
    if (!autoFocusProps.value?.targetStartWeek) return;
    const { dueDateMidIdx, shipmentDateMidIdx } = binarySearch(autoFocusProps.value.targetStartWeek);
    // 이진 탐색으로 구한 인덱스를 기반으로 조건 분기
    const isWeekStartEarlierThanDueDate =
      dueDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[dueDateMidIdx].dueDate).diff(
        dayjs(autoFocusProps.value.targetStartWeek),
        'day',
      ) >= 0;
    const isWeekEndLaterThanDueDate =
      dueDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[dueDateMidIdx].dueDate).diff(
        dayjs(autoFocusProps.value.targetEndWeek),
        'day',
      ) <= 0;
    const isWeekStartEarlierThanShipmentDate =
      shipmentDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[shipmentDateMidIdx].shipmentDate).diff(
        dayjs(autoFocusProps.value.targetStartWeek),
        'day',
      ) >= 0;
    const isWeekEndLaterThanShipmentDate =
      shipmentDateMidIdx !== -1 &&
      dayjs(masterGrid.value.collectionView?.items[shipmentDateMidIdx].shipmentDate).diff(
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
      focusTargetIndex = masterGrid.value.collectionView?.items.length - 1;
    }
  }

  if (masterGrid.value) {
    masterGrid.value.select(new CellRange(focusTargetIndex, 0), true);
  }
};

// GRID INITIALIZE
const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  masterGrid.value = flexGrid;
  masterExtendGrid.value = _extendGrid;

  flexGrid.itemsSourceChanged.addHandler(masterFocusColumnHandler);
  flexGrid.itemsSourceChanged.addHandler(onMasterSelectionChanged);
};

const onInitializedDetail = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  detailGrid.value = flexGrid;
  detailExtendGrid.value = _extendGrid;

  detailGrid.value.mergeManager = new CustomMergeManager();

  const columnHeaders = detailGrid.value.columnHeaders;
  const extraRow = new Row({ _isExtraRow: true });
  columnHeaders.rows.insert(0, extraRow);

  detailGrid.value.allowMerging = AllowMerging.All;
  extraRow.allowMerging = true;

  // 헤더 수직 병합
  detailGrid.value.columns[0].allowMerging = true;
  detailGrid.value.columns[1].allowMerging = true;
  detailGrid.value.columns[2].allowMerging = true;
  detailGrid.value.columns[3].allowMerging = true;
  // detailGrid.value.columns[4].allowMerging = true;
  // detailGrid.value.columns[5].allowMerging = true;
  // detailGrid.value.columns[6].allowMerging = true;

  // 왼쪽 8개 열 고정
  detailGrid.value.frozenColumns = 7;
};

const isDateFormat = (str: string): boolean => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(str);
};

const masterFormatItem = (s: FlexGrid, e: any) => {
  if (!isDataCell(s, e)) return;

  const rowItem = e.getRow()?.dataItem;
  if (!rowItem) return;
  const col = e.getColumn().binding as
    | 'demandID'
    | 'custName'
    | 'demandQty'
    | 'dueDate'
    | 'shipmentDate'
    | 'dateDiff'
    | 'onTimeQty'
    | 'lateQty'
    | 'rtfRatio'
    | 'shortQty';

  const cell = e.cell.querySelector('span') != null ? e.cell.querySelector('span') : e.cell;
  if (!cell) return;

  switch (col) {
    case 'rtfRatio':
      cell.textContent = `${rowItem[col] ? rowItem[col] : '0'}%`;
      break;
    default:
      break;
  }

  // short이 그리드 표시 우선순위에 더 중요해서 다음과 같이 분기처리함
  if (rowItem.rtfRatio < 100) {
    e.cell.classList.add('ratio-short');
    switch (col) {
      case 'rtfRatio':
        e.cell.classList.add('ratio-short-col');
        break;
      default:
        break;
    }
  }
  if (rowItem.rtfRatio === 100 && rowItem.lateQty > 0) {
    e.cell.classList.add('ratio-late');
  }

  e.cell.classList.add('mouse-point');
};

const detailFormatItem = (s: FlexGrid, e: any) => {
  // if (!isDataCell(s, e)) return;

  const rowItem = e.getRow()?.dataItem;
  const col: string = e.getColumn().binding;

  const dueDate = localState?.masterSelectedRow?.dueDate;

  if (rowItem?.isSummaryRow) {
    e.cell.classList.add('summary-row');
  }

  if (isDateFormat(col) && dueDate) {
    const colDate = dayjs(col);

    if (colDate.isAfter(afterDueDate.value)) {
      e.cell.classList.add('late');
    } else if (colDate.isSame(afterDueDate.value, 'day')) {
      e.cell.classList.add('late');
      e.cell.classList.add('after-due-date');
    }
  }

  if (!isDataCell(s, e)) return;
  if (colorTargetDetailGridLastDate.value === col || colorTargetDueDate.value === col) {
    e.cell.style.backgroundColor = '#e1707021'; // 우선순위 문제로 인라인 스타일 지정
  } else {
    e.cell.style.backgroundColor = '#ffffff'; // Master gird 내에서 다른 전환시 복구
  }
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
      masterDataSource.value = result.data;
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

  itemColumns.value = newItemColumns;

  nextTick(() => {
    if (detailGrid.value) {
      // 그리드 헤더 만들기
      const columnHeaders = detailGrid.value.columnHeaders;
      const extraRow = columnHeaders.rows[1];

      if (!extraRow) return;

      for (let i = 0; i < detailGrid.value.columns.length; i++) {
        let headerName = columnHeaders.getCellData(1, i, false);

        if (i >= 7) {
          // 7번째 이전 컬럼은 원래 데이터 입력하고 그 이후는 생산계획으로 도배
          headerName = t('text-prod_plan');
        }

        columnHeaders.setCellData(0, i, headerName);
      }

      const bohColIndex = columnHeaders.columns.findIndex((c) => c.binding === 'wipQty');
      const pegColIndex = columnHeaders.columns.findIndex((c) => c.binding === 'pegQty');

      // 특별히 재공 입력
      columnHeaders.setCellData(0, bohColIndex, t('text-wip'));
      columnHeaders.setCellData(0, pegColIndex, t('text-wip'));
    }
  });
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

  detailDataSource.value = rows;
};

/**
 * EVENT
 */
const onMasterSelectionChanged = debounce((s: FlexGrid) => {
  const selected = s.selectedRows[0]?.dataItem;

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
  masterGrid.value?.select(-1, -1);
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

onBeforeUnmount(() => {
  if (masterGrid.value) {
    masterGrid.value.itemsSourceChanged.removeAllHandlers();
  }
});

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
      justify-content: center;
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
</style>
