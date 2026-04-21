<template>
  <div class="re-execute-plan-page">
  <Controller
    :navigations="[t('text-menu-production_planning'), t('text-re_plan_excute')]"
    :show-filter-button="true"
    :actions="[
      {
        action: 'Search',
        click: async () => {
          await onLoad();
          await loadDemandSourceData();
        },
        loading: isPageFetching,
      },
    ]"
  >
    <template #beforeFilter>
      <div v-if="currentPlanCycleSource?.frozen_plan_ver" class="info-frozen-plan-wrapper">
        <span class="info-frozen-plan-icon">i</span>
        <div class="info-frozen-plan-text">
          {{ t('text-info_frozen_plan_ver') }}
          <span class="info-frozen-plan-ver">{{
            currentPlanCycleSource?.plan_cycle_id ? currentPlanCycleSource?.plan_cycle_id : ''
          }}</span>
          /
          <span class="info-frozen-plan-ver">{{
            currentPlanCycleSource?.frozen_plan_ver ? currentPlanCycleSource?.frozen_plan_ver : ''
          }}</span>
        </div>
      </div>
    </template>
    <template #action>
      <Button :text="t('버전 정보')" @click="openVerInfo">
        <template #icon>
          <IconLineEdit :size="'14'" :color="'#ffffff'" />
        </template>
      </Button>
      <Button :text="t('text-plan_excute')" @click="openReExecute">
        <template #icon>
          <IconReExecute :size="'14'" :color="'#ffffff'" />
        </template>
      </Button>
    </template>
    <template #filter>
      <Radio
        v-model="summaryType"
        :label="t('text-summary_type')"
        :items-source="summarySource"
        display-expr="label"
        value-expr="value"
      />
      <MultiSelect
        :placeholder="`${!custSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
        :label="t('text-oper_group_id')"
        v-model="operGroups"
        :header-format="'{count:n0} OPER GROUPS'"
        :use-filter="true"
        :use-select-all="true"
        :display-prop="'oper_group_id'"
        :items-source="operGroupSource"
        :key-prop="'oper_group_id'"
        @close="
          () => {
            if (!operGroups.length) {
              operGroups = operGroupSource.map((item: any) => item.oper_group_id);
            }
          }
        "
      />
      <MultiSelect
        v-if="summaryType === 'cust'"
        :placeholder="`${!custSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
        :label="t('text-upper-customer')"
        v-model="custParam"
        :header-format="'{count:n0} CUSTOMERS'"
        :use-filter="true"
        :use-select-all="true"
        :display-prop="'cust_label'"
        :items-source="custSource"
        :key-prop="'cust_id'"
        @close="
          () => {
            if (!custParam.length) {
              custParam = custSource.map((item: any) => item.cust_id);
            }
          }
        "
      />
      <MultiSelect
        v-if="summaryType === 'itemGroup'"
        :placeholder="`${!itemGroupSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
        :label="t('text-upper-item_group')"
        v-model="itemGroup"
        :items-source="itemGroupSource"
        :header-format="'{count:n0} GROUPS'"
        :use-select-all="true"
        :use-filter="true"
        display-prop="item_group_id"
        key-prop="item_group_id"
        @close="
          () => {
            if (!itemGroup.length) {
              itemGroup = itemGroupSource.map((item: any) => item.item_group_id);
            }
          }
        "
      />
      <MultiSelect
        v-if="summaryType === 'region'"
        :placeholder="`${!regionSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
        :label="t('text-upper-region')"
        v-model="region"
        :items-source="regionSource"
        :header-format="'{count:n0} REGIONS'"
        :use-select-all="true"
        :use-filter="true"
        display-prop="text"
        key-prop="value"
        @close="
          () => {
            if (!region.length) {
              region = regionSource.map((item: any) => item.value);
            }
          }
        "
      />
      <MultiSelect
        v-if="summaryType === 'demandType'"
        :placeholder="`${!demandTypeSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
        :label="t('text-upper-demand_type')"
        v-model="demandType"
        :items-source="demandTypeSource"
        :header-format="'{count:n0} DEMAND TYPES'"
        :use-select-all="true"
        :use-filter="true"
        display-prop="value"
        key-prop="value"
        @close="
          () => {
            if (!demandType.length) {
              demandType = demandTypeSource.map((item: any) => item.value);
            }
          }
        "
      />
      <Select
        :label="t('text-qty_uom')"
        v-model="uomType"
        :items-source="qtyUOMSource"
        keyProp="value"
        displayProp="displayValue"
      />
    </template>
  </Controller>
  <div class="moz-frame-for-outer-control">
    <SplitPane horizontal>
      <Pane size="60%" min-size="30%">
        <div class="re-execute-pane">
          <ExtendPivotGrid
            v-memo="[pivotDataSource, valueFields]"
            :name="`re-execute-plan-pivot`"
            :id="`re-execute-plan-pivot-id`"
            :emptyState="{
              isLoading: mainQueryIsPending,
            }"
            class="prod-plan-ins-main"
            ref="extendPivot"
            height="100%"
            :itemsSource="pivotDataSource"
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
            :initialized="pivotOnInitialized"
            :panel-on-update="updateView"
            :formatItem="pivotFormatItem"
            :pivotRef="extendPivot"
            :usePivotChart="false"
            :use-tool-box-setting="false"
            :loading="mainQueryIsPending"
            :use-tool-box="false"
            :use-preset="true"
          >
          </ExtendPivotGrid>
        </div>
      </Pane>
      <Pane size="40%" min-size="30%">
        <div class="modify-demand-pane">
          <ExtendFlexGrid
            style="width: 100%; height: 100%"
            :id="'re-execute-plan-extend-grid-id'"
            :name="'re-execute-plan-extend-grid'"
            :use-preset="true"
            :autoGenerateColumns="false"
            :alternatingRowStep="0"
            :itemsSource="sharedDataSource"
            :initialized="onInitialized"
            :emptyState="{
              isLoading: getDemandSourceIsPending,
            }"
            :validateKey="'none'"
            :dataKey="gridKeys"
            :setContextMenuProps="{
              useGroupColumn: true,
              useViewSelectColumn: true,
              useBulkEditColumn: {
                max_lateness_day: {
                  min: 0,
                  step: 1,
                },
                max_earliness_day: {
                  min: 0,
                  step: 1,
                },
              },
            }"
            :onInitializeRowData="
              () => {
                return { isAdded: true };
              }
            "
            :loading="getDemandSourceIsPending"
            :cellEditEnded="onMainCellEditEnded"
            :use-tool-box="true"
            :is-tool-box-expanded="false"
          >
            <WjFlexGridColumn
              :width="120"
              binding="demand_id"
              :header="t('text-demand_id')"
              :isRequired="true"
            />
            <WjFlexGridColumn
              :width="150"
              binding="item_id"
              :header="t('text-item_id')"
              :isRequired="true"
            />
            <WjFlexGridColumn
              :width="120"
              binding="site_id"
              :header="t('text-site_id')"
              :isRequired="true"
            />
            <WjFlexGridColumn
              :width="120"
              binding="buffer_id"
              :header="t('text-buffer_id')"
              :isRequired="true"
            />
            <WjFlexGridColumn
              :width="120"
              binding="due_date"
              :header="t('text-due_date')"
              dataType="Date"
              format="yyyy-MM-dd"
              align="center"
              :isRequired="true"
            />
            <WjFlexGridColumn
              :width="160"
              binding="due_datetime"
              :header="t('text-due_datetime')"
              dataType="Date"
              format="yyyy-MM-dd HH:mm:ss"
              align="center"
            />
            <WjFlexGridColumn
              :width="100"
              binding="demand_qty"
              :header="t('text-demand_qty')"
              dataType="Number"
              align="right"
            />
            <WjFlexGridColumn
              :width="100"
              binding="demand_priority"
              :header="t('text-demand_priority')"
              dataType="Number"
              align="right"
            />
            <WjFlexGridColumn :width="120" binding="cust_id" :header="t('text-cust_id')" />
            <WjFlexGridColumn :width="120" binding="demand_type" :header="t('text-demand_type')" />
            <WjFlexGridColumn
              :width="120"
              binding="max_lateness_day"
              :header="t('text-max_lateness_day')"
              dataType="Number"
              align="right"
            />
            <WjFlexGridColumn
              :width="120"
              binding="max_earliness_day"
              :header="t('text-max_earliness_day')"
              dataType="Number"
              align="right"
            />
            <WjFlexGridColumn :width="120" binding="demand_group" :header="t('text-demand_group')" />
            <WjFlexGridColumn
              :width="120"
              binding="final_item_buffer_id"
              :header="t('text-final_item_buffer_id')"
            />
            <WjFlexGridColumn :width="100" binding="description" :header="t('text-description')" />
            <WjFlexGridColumn
              v-for="col in propColumns"
              :key="col.binding"
              :binding="col.binding"
              :header="col.header"
              :dataType="col.dataType"
              :width="col.width"
              :align="col.align"
            ></WjFlexGridColumn>
          </ExtendFlexGrid>
        </div>
      </Pane>
    </SplitPane>
  </div>

  <ReExecutePlanPop
    v-if="isOpen"
    :visible="isOpen"
    :popupDataSource="(useReExecutePlan.popupDataSource.value as any[]) || []"
    :demandSource="(useReExecutePlan.demandSource.value as any[]) || []"
    :alwaysEditedData="(useReExecutePlan.alwaysEditedData.value as any[]) || []"
    :propColumns="useReExecutePlan.propColumns.value"
    :executionFlowSource="useReExecutePlan.executionFlowSource.value"
    :scenarioList="useReExecutePlan.scenarioList.value"
    :inboundSource="useReExecutePlan.inboundSource.value"
    :scenarioModuleDataSource="useReExecutePlan.scenarioModuleDataSource.value"
    :phaseColumns="useReExecutePlan.phaseColumns.value"
    :planVer="planVer"
    :parentMenuName="t('text-menu-production_planning')"
    :menuName="t('text-re_plan_excute')"
    :planStartDate="useReExecutePlan.actStartDate?.value || ''"
    :planCycleId="useReExecutePlan.reExecuteState?.value?.planCycleID || ''"
    :demandVer="
      useReExecutePlan.reExecuteState?.value?.demandVer ||
      useReExecutePlan.demandVerSource?.value?.[0]?.demand_ver ||
      ''
    "
    @close="closeReExecute"
    @update:visible="(v: boolean) => { if (!v) closeReExecute(); }"
  />

  <Popup :title="t('버전 정보')" :width="290" preset="check" :onConfirm="closeVerInfo" v-model:visible="verInfoIsOpen">
    <div class="ver-info-container">
      <div class="ver-info-item">
        <div class="title">{{ t('확정 계획:') }}</div>
        <div class="value">{{ frozenPlanVerInfo }}</div>
      </div>
      <div class="ver-info-item">
        <div class="title">{{ t('수요 정보 버전:') }}</div>
        <div class="value">{{ demandVerInfo }}</div>
      </div>
    </div>
  </Popup>
  </div>
</template>
<script setup lang="ts">
import {
  Controller,
  Button,
  MultiSelect,
  Pane,
  Popup,
  Radio,
  Select,
  SplitPane,
} from "@vmscloud/moz-ui-components";
import { DataType } from "@vmscloud/moz-wijmo-grid/wijmo";
import { FlexGrid } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { PivotGrid, ShowTotals } from "@vmscloud/moz-wijmo-grid/wijmo.olap";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { ExtendFlexGrid, ExtendPivotGrid } from "@vmscloud/moz-wijmo-grid";
import type { ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { useTranslation } from "i18next-vue";
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  reactive,
  type Ref,
  ref,
  watch,
} from "vue";
import { useHostPlanCycle } from "@/composables/useHostStores";
import { IconLineEdit, IconReExecute } from "@moz-shared/icons";
import { useReExecutePlanQuery } from "./reExecutePlan";
import ReExecutePlanPop from "./ReExecutePlanPop.vue";

const { t } = useTranslation(); // 다국어
const { planVer, fromDate, toDate } = useHostPlanCycle();

// planCycleID - derived from planVer (no separate store in custom-ui-templates)
const planCycleID = ref("");

const useReExecutePlan = useReExecutePlanQuery(planVer, planCycleID, fromDate, toDate);
const {
  // 조회조건
  summaryType,
  summarySource,
  custSource,
  custParam,
  itemGroupSource,
  itemGroup,
  regionSource,
  region,
  demandTypeSource,
  demandType,
  uomType,
  qtyUOMSource,

  custIsSuccess,
  itemGroupIsSuccess,
  regionIsSuccess,
  demandTypeIsSuccess,

  //메뉴
  demandSource,
  selectedDemandList,
  pivotDataSource,
  fullDataSource,

  // 공유 CollectionView 관련
  sharedCollectionView,
  initializeSharedCollectionView,
  sharedDataSource,

  // 그리드 참조 공유
  mainGrid,
  popupGrid,

  // ExtendGrid 인스턴스 공유
  mainExtendGrid,
  popupExtendGrid,
  updateTrigger,

  // 계획 재실행 pop
  isOpen,
  open: originalOpen,

  // api 호출
  onLoad,
  isPageFetching,
  loadParams,
  mainQueryIsPending,

  loadDemandSource,
  getDemandSourceIsPending,

  operGroupSource,
  operGroups,

  getOperGroupSourceIsSuccess,
  getOperSourceIsSuccess,
  getBufferSourceIsSuccess,

  verInfoIsOpen,
  openVerInfo,
  closeVerInfo,

  propColumns,

  // frozen plan info
  currentPlanCycleSource,

  actStartDate,
  actEndDate,
} = useReExecutePlan;

// 피봇 셀 선택 상태 관리
const isPivotCellSelected = ref(false);

// 현재 적용된 필터 함수 보존
let currentFilterFunction: ((item: any) => boolean) | null = null;

// 피봇 셀 선택 해제 함수
const clearPivotSelection = () => {
  isPivotCellSelected.value = false;
  selectedDemandList.value = [];
  currentFilterFunction = null;

  if (pivot.value) {
    pivot.value.select(-1, -1);
  }

  if (grid.value && extendGrid.value) {
    applyDemandFilter();
  }
};

// demandSource에 직접 필터링 적용
const applyDemandFilter = () => {
  if (!grid.value || !extendGrid.value) {
    return;
  }

  const currentCV = grid.value.collectionView;
  if (!currentCV) {
    return;
  }

  const filterProtectionKey = "_filterProtectionAdded";
  if (!(currentCV as any)[filterProtectionKey]) {
    currentCV.collectionChanged.addHandler(() => {
      if (isPivotCellSelected.value && selectedDemandList.value?.length > 0 && !currentCV.filter) {
        setTimeout(() => {
          if (isPivotCellSelected.value && !currentCV.filter) {
            currentCV.filter = (item: any) => selectedDemandList.value.includes(item.demand_id);
            currentCV.refresh();
          }
        }, 50);
      }
    });
    (currentCV as any)[filterProtectionKey] = true;
  }

  if (!isPivotCellSelected.value || !selectedDemandList.value || selectedDemandList.value.length === 0) {
    currentCV.filter = null;
    currentFilterFunction = null;
  } else {
    currentFilterFunction = (item: any) => selectedDemandList.value.includes(item.demand_id);
    currentCV.filter = currentFilterFunction;
  }

  currentCV.refresh();

  nextTick(() => {
    if (grid.value) {
      grid.value.scrollIntoView(0, 0);
      grid.value.select(-1, -1);
      grid.value.invalidate();
      grid.value.refresh();

      setTimeout(() => {
        if (grid.value) {
          grid.value.scrollIntoView(0, 0);
          grid.value.invalidate();
        }
      }, 50);
    }
  });
};

// ExtendGrid
const grid = ref<FlexGrid | null>(null);
const extendGrid = ref<any>();
const gridKeys: string[] = ["demand_id"];

const extendPivot = ref();
const pivot = ref();

const fields = computed(() => {
  const defaultFields: any[] = [
    {
      binding: "plan_type",
      header: t("text-plan_type"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "oper_group_id",
      header: t("text-oper_group_id"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "item_group_id",
      header: t("text-item_group_id"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "aggr_value",
      header: t("text-aggr_value"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "buffer_id",
      header: t("text-buffer_id"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "oper_id",
      header: t("text-oper_id"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "date",
      header: t("text-date"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "week",
      header: t("text-week"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "month",
      header: t("text-month"),
      dataType: DataType.String,
      align: "left",
    },
    {
      binding: "qty",
      header: t("text-sum"),
      dataType: DataType.Number,
      align: "right",
      format: "n2",
    },
  ] satisfies any[];

  return defaultFields;
});

const rowFields = computed(() => [
  t("text-oper_group_id"),
  t("text-aggr_value"),
  t("text-plan_type"),
]);

const columnFields: Ref<string[]> = ref([t("text-month"), t("text-week"), t("text-date")]);
const valueFields: Ref<string[]> = ref([t("text-sum")]);

const dataState: {
  menuName: string;
  showRowTotals: ShowTotals;
  showColumnTotals: ShowTotals;
  showZeros: boolean;
  totalsBeforeData: boolean;
} = reactive({
  menuName: "",
  showRowTotals: ShowTotals.None,
  showColumnTotals: ShowTotals.GrandTotals,
  showZeros: false,
  totalsBeforeData: false,
});

const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
  extendGrid.value = _extendGrid;

  mainGrid.value = flexGrid;
  mainExtendGrid.value = _extendGrid;

  if (demandSource.value && demandSource.value.length > 0) {
    initializeSharedCollectionView();
  }

  flexGrid.addEventListener(flexGrid.hostElement, "click", onFlexGridClick);
  flexGrid.addEventListener(flexGrid.hostElement, "mousedown", onFlexGridInteraction);
  flexGrid.addEventListener(flexGrid.hostElement, "keydown", onFlexGridInteraction);

  flexGrid.selectionChanged.addHandler(() => {
    setTimeout(checkAndRestoreFilter, 10);
  });

  flexGrid.updatedView.addHandler(() => {
    setTimeout(checkAndRestoreFilter, 10);
  });

  flexGrid.loadedRows.addHandler(() => {
    if (_extendGrid && (_extendGrid as any).groupPanel) {
      (_extendGrid as any).groupPanel.hostElement.style.display = "";
    }
  });

  grid.value.loadedRows.addHandler(async () => {
    await nextTick(() => {
      if (grid.value) {
        grid.value.collapseGroupsToLevel(0);
      }
    });
  });
};

watch(demandSource, async () => {
  initializeSharedCollectionView();
});

const localState: {
  masterSelectedRow: any;
  collapsibleSubtotals: boolean;
} = reactive({
  masterSelectedRow: null,
  collapsibleSubtotals: true,
});

const toggleCollapsibleSubtotals = () => {
  if (pivot.value) {
    pivot.value.collapsibleSubtotals = localState.collapsibleSubtotals;

    if (localState.collapsibleSubtotals) {
      dataState.showRowTotals = ShowTotals.None;
      dataState.showColumnTotals = ShowTotals.Subtotals;

      if (pivot.value.engine) {
        pivot.value.engine.showRowTotals = ShowTotals.None;
        pivot.value.engine.showColumnTotals = ShowTotals.Subtotals;
      }
    } else {
      dataState.showRowTotals = ShowTotals.None;
      dataState.showColumnTotals = ShowTotals.GrandTotals;

      if (pivot.value.engine) {
        pivot.value.engine.showRowTotals = ShowTotals.None;
        pivot.value.engine.showColumnTotals = ShowTotals.GrandTotals;
      }
    }

    pivot.value.invalidate();

    const collapse = () => {
      (pivot.value as PivotGrid).collapseColumnsToLevel(2);
      (pivot.value as PivotGrid).collectionView?.collectionChanged.removeHandler(collapse);
    };
    (pivot.value as PivotGrid).collectionView?.collectionChanged.addHandler(collapse);
  }
};

// 필터 상태 체크 및 복원
const checkAndRestoreFilter = () => {
  if (!isPivotCellSelected.value || !selectedDemandList.value?.length || !grid.value?.collectionView) {
    return;
  }

  const currentCV = grid.value.collectionView;
  const currentFilter = currentCV.filter;

  if (!currentFilter && currentFilterFunction) {
    currentCV.filter = currentFilterFunction;
    currentCV.refresh();
  }
};

const onFlexGridClick = (_e: MouseEvent) => {
  setTimeout(checkAndRestoreFilter, 5);
};

const onFlexGridInteraction = (_e: Event) => {
  setTimeout(checkAndRestoreFilter, 5);
};

// ExtendFlexGrid 내부 상태 동기화 함수
const syncExtendGridStates = (sourceExtendGrid: any, targetExtendGrid: any) => {
  try {
    sourceExtendGrid.originalDataMap.forEach((value: any, key: string) => {
      if (!targetExtendGrid.originalDataMap.has(key)) {
        targetExtendGrid.originalDataMap.set(key, new Map(value));
      } else {
        const targetMap = targetExtendGrid.originalDataMap.get(key);
        value.forEach((colValue: any, colKey: string) => {
          targetMap.set(colKey, colValue);
        });
      }
    });

    sourceExtendGrid.updated.forEach((value: any, key: string) => {
      targetExtendGrid.updated.set(key, value);
    });

    sourceExtendGrid.added.forEach((value: any, key: string) => {
      targetExtendGrid.added.set(key, value);
    });

    sourceExtendGrid.removed.forEach((value: any, key: string) => {
      targetExtendGrid.removed.set(key, value);
    });
  } catch (error) {
    console.error("ExtendFlexGrid 상태 동기화 에러:", error);
  }
};

// 메인 그리드 셀 편집 완료 이벤트
const onMainCellEditEnded = (_sender: any, _e: any) => {
  if (isOpen.value && popupGrid.value && extendGrid.value) {
    try {
      const sourceExtendGrid = mainExtendGrid.value;

      if (popupExtendGrid.value) {
        syncExtendGridStates(sourceExtendGrid, popupExtendGrid.value);

        const scrollTop = popupGrid.value.scrollPosition?.y || 0;
        const scrollLeft = popupGrid.value.scrollPosition?.x || 0;

        popupGrid.value.invalidate();
        popupGrid.value.refresh();

        setTimeout(() => {
          if (popupGrid.value) {
            popupGrid.value.scrollPosition = { x: scrollLeft, y: scrollTop };
          }
        }, 10);
      } else {
        console.warn("[메인] 팝업 ExtendFlexGrid 인스턴스를 찾을 수 없음");
      }
    } catch (error) {
      console.error("[메인] 팝업 그리드 동기화 에러:", error);
    }
  }

  nextTick(() => {
    updateTrigger.value++;
  });
};

// 팝업 열기 함수
const openReExecute = () => {
  originalOpen();

  nextTick(() => {
    setTimeout(() => {
      if (mainExtendGrid.value && popupExtendGrid.value) {
        try {
          syncExtendGridStates(mainExtendGrid.value, popupExtendGrid.value);

          if (popupGrid.value) {
            popupGrid.value.invalidate();
            popupGrid.value.refresh();

            setTimeout(() => {
              if (popupGrid.value) {
                popupGrid.value.scrollPosition = { x: 0, y: 0 };
              }
            }, 10);
          }
        } catch (error) {
          console.error("[팝업 열기] 상태 동기화 에러:", error);
        }
      }
    }, 100);
  });
};

const closeReExecute = () => {
  useReExecutePlan.close();
};

const pivotOnInitialized = (pivotGrid: PivotGrid) => {
  pivot.value = pivotGrid;

  pivotGrid.allowDragging = 0;
  pivotGrid.selectionMode = 2;

  pivotGrid.addEventListener(pivotGrid.hostElement, "click", onPivotCellClick);

  document.addEventListener("click", onDocumentClick);

  pivotGrid.loadedRows.addHandler(onPivotLoadedRows);
};

const onPivotLoadedRows = () => {
  toggleCollapsibleSubtotals();
};

// 문서 전체 클릭 이벤트 (피봇 그리드 외부 클릭 감지)
const onDocumentClick = (e: MouseEvent) => {
  if (!pivot.value) return;

  if (!e.isTrusted) {
    return;
  }

  const pivotElement = pivot.value.hostElement;
  const target = e.target as Element;

  const flexGridElement = grid.value?.hostElement;
  const isFlexGridClick = flexGridElement && flexGridElement.contains(target);

  const isModifyDemandPaneClick = target.closest(".modify-demand-pane");

  const isUIComponentClick =
    target.closest(".moz-button") ||
    target.closest(".moz-multi-select") ||
    target.closest(".moz-select") ||
    target.closest(".moz-radio-buttons") ||
    target.closest(".moz-input") ||
    target.closest(".moz-date-picker") ||
    target.closest(".moz-checkbox") ||
    target.closest(".moz-dropdown");

  const isReExecutePopupOpen = isOpen.value;
  const isReExecutePopupClick =
    target.closest(".re-execute-plan-pop") ||
    target.closest(".moz-popup") ||
    target.closest(".popup-overlay");

  const isExceptionArea =
    isFlexGridClick ||
    isModifyDemandPaneClick ||
    isUIComponentClick ||
    (isReExecutePopupOpen && isReExecutePopupClick);

  if (pivotElement && !pivotElement.contains(target) && !isExceptionArea) {
    if (isPivotCellSelected.value) {
      if (isReExecutePopupOpen) {
        return;
      }
      clearPivotSelection();
    }
  }
};

// 피봇 그리드 셀 클릭 이벤트 핸들러
const onPivotCellClick = (e: MouseEvent) => {
  if (!pivot.value) return;

  const hitTest = pivot.value.hitTest(e);

  if (hitTest.cellType === 1 || hitTest.cellType === 3) {
    const row = hitTest.row;
    getRowDataWithTotalFilter(row);
  }
};

// 특정 행의 모든 데이터 중 date가 TOTAL인 것만 필터링하는 함수
const getRowDataWithTotalFilter = (rowIndex: number) => {
  if (!pivot.value) return;

  const pivotGrid = pivot.value;

  try {
    const pivotRow = pivotGrid.rows[rowIndex];

    if (pivotRow && pivotRow.dataItem) {
      const dataItem = pivotRow.dataItem;
      const totalData: any[] = [];

      Object.keys(dataItem).forEach((key) => {
        if (key.includes("TOTAL")) {
          const totalInfo = {
            key,
            value: dataItem[key],
            parsedKey: key.split(";"),
          };

          const parsedData: any = {};
          totalInfo.parsedKey.forEach((part) => {
            if (part.includes(":")) {
              const [fieldName, fieldValue] = part.split(":");
              parsedData[fieldName] = fieldValue;
            }
          });

          totalData.push({
            originalKey: key,
            value: totalInfo.value,
            date: parsedData["날짜"] || "TOTAL",
            qty: parsedData["수량"] || "0",
            ...parsedData,
          });
        }
      });

      const itemKey = "_item";
      if (dataItem.$rowKey && dataItem.$rowKey[itemKey]) {
        totalData.forEach((item) => {
          item.rowKeyInfo = dataItem.$rowKey[itemKey];
        });
      }

      const sourceData = fullDataSource.value || [];

      let sourceTotalData: any[] = [];

      if (dataItem.$rowKey && dataItem?.$rowKey?.[itemKey]) {
        const rowKeyInfo = dataItem?.$rowKey?.[itemKey];
        const keyFieldsToMatch = ["aggr_value", "buffer_id", "plan_type"];

        sourceTotalData = sourceData.filter((item: any) => {
          if (item.date !== "TOTAL") return false;

          return keyFieldsToMatch.every((key) => {
            const rowValue = rowKeyInfo[key];
            const itemValue = item[key];

            if (rowValue == null && itemValue == null) return true;
            if ((rowValue == null) !== (itemValue == null)) return false;
            return rowValue === itemValue;
          });
        });

        if (sourceTotalData.length > 0 && sourceTotalData[0].demandIDs) {
          selectedDemandList.value = sourceTotalData[0].demandIDs;
          isPivotCellSelected.value = true;
          applyDemandFilter();
        } else {
          clearPivotSelection();
        }
      } else {
        sourceTotalData = sourceData.filter((item: any) => item.date === "TOTAL");
      }

      if (totalData.length > 0) {
        // totalData found
      } else {
        console.warn("date가 TOTAL인 데이터를 찾을 수 없습니다.");
      }
    } else {
      console.warn("행 데이터를 찾을 수 없습니다.");
    }
  } catch (error) {
    console.error("행 데이터 처리 실패:", error);
  }
};

const pivotFormatItem = (s: PivotGrid, e: any) => {
  if (e.panel === s.cells) {
    const row = s.rows[e.row];
    if (row && row.dataItem) {
      const dataItem = row.dataItem;

      // 1. DIFF row 확인
      const isDiffRow = isDiffRowCheck(dataItem);

      // 2. text-sum column 확인
      const isTextSumColumn = isTextSumColumnCheck(s, e);

      // 3. 개별 데이터 컬럼이 아닌지 확인
      const isNotDataColumn = isNotDataColumnCheck(s, e);

      // 4. text-week 부분합 확인
      const isTextWeekSubtotal = isTextWeekSubtotalCheck(s, e);

      // 5. 총합계 확인
      const isGrandTotal = isGrandTotalCheck(s, e);

      if (isDiffRow && isTextWeekSubtotal) {
        const lastValue = findLastValueInAllData(dataItem);
        if (lastValue !== null) {
          const formattedValue = Math.round(lastValue * 100) / 100;
          const displayValue = formattedValue.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });
          e.cell.textContent = displayValue;
        }
      } else if (isDiffRow && isGrandTotal) {
        const lastValue = findLastValueInAllData(dataItem);
        if (lastValue !== null) {
          const formattedValue = Math.round(lastValue * 100) / 100;
          const displayValue = formattedValue.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });
          e.cell.textContent = displayValue;
        }
      } else if (isDiffRow && isTextSumColumn && isNotDataColumn) {
        const lastValue = findLastValueInSum(s, e);
        if (lastValue !== null) {
          const formattedValue = Math.round(lastValue * 100) / 100;
          const displayValue = formattedValue.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          });
          e.cell.textContent = displayValue;
        }
      }
    }
  }

  // valueFields인 경우에만 날짜 범위 확인
  if (e.panel === s.cells && actStartDate.value && actEndDate.value) {
    // isInRange placeholder - inline check
    const column = s.columns[e.col];
    if (column?.header) {
      const header = column.header;
      const dateMatch = header.match(/(\d{4}-\d{2}-\d{2})/);
      if (dateMatch) {
        const cellDate = dateMatch[1];
        if (cellDate >= actStartDate.value && cellDate <= actEndDate.value) {
          e.cell.style.backgroundColor = "#357e631a";
        } else {
          e.cell.style.backgroundColor = "";
          e.cell.classList.remove("date-range-highlight");
        }
      }
    }
  }

  if (e.cell.textContent) {
    const text = e.cell.textContent;
    const cleanText = text.replace(/,/g, "");
    const number = Number(cleanText);

    if (!isNaN(number) && number < 0) {
      e.cell.style.color = "#d32f2f";
      e.cell.classList.add("negative-number");
    }

    if (/^\d+_/.test(text)) {
      e.cell.textContent = text.replace(/^\d+_/, "");
    }

    if (e.cell.textContent === "DIFF") {
      e.cell.textContent = "DIFF(cum)";
    }
  }

  if (e.cell.textContent === "text-aggr_value") {
    if (loadParams.value.aggregateType === "itemGroup") {
      e.cell.textContent = t("text-item_group");
    }
    if (loadParams.value.aggregateType === "demandType") {
      e.cell.textContent = t("text-demand_type");
    }
    if (loadParams.value.aggregateType === "region") {
      e.cell.textContent = t("text-upper-region");
    }
    if (loadParams.value.aggregateType === "cust") {
      e.cell.textContent = t("text-upper-customer");
    }
  }

  if (e.cell.textContent.includes(t("text-month"))) {
    e.cell.classList.add("include-qty-uom");
    e.cell.textContent = "";

    const container = document.createElement("div");
    container.style.display = "flex";
    container.style.flexDirection = "row";
    container.style.justifyContent = "space-between";

    const div = document.createElement("div");
    let text;
    if (loadParams.value.uomType === "DEFAULT") {
      text = "(단위: EA)";
    } else {
      text = "(단위: m\u00B2)";
    }
    div.textContent = text;
    container.appendChild(div);

    const div2 = document.createElement("div");
    div2.textContent = "월:";
    container.appendChild(div2);

    e.cell.appendChild(container);
  }
};

// DIFF row 확인 함수
const isDiffRowCheck = (dataItem: any): boolean => {
  try {
    const itemKey = "_item";
    if (dataItem.$rowKey && dataItem.$rowKey[itemKey]) {
      const rowKeyInfo = dataItem.$rowKey[itemKey];
      return rowKeyInfo.plan_type === "DIFF" || rowKeyInfo.plan_type?.includes("DIFF");
    }

    if (dataItem.plan_type) {
      return dataItem.plan_type === "DIFF" || dataItem.plan_type.includes("DIFF");
    }

    return false;
  } catch {
    return false;
  }
};

// text-sum column 확인 함수
const isTextSumColumnCheck = (s: PivotGrid, e: any): boolean => {
  try {
    const column = s.columns[e.col];
    if (!column) return false;

    if (e.cell.classList.contains("wj-aggregate")) {
      return true;
    }

    return false;
  } catch {
    return false;
  }
};

// 개별 데이터 컬럼이 아닌지 확인
const isNotDataColumnCheck = (s: PivotGrid, e: any): boolean => {
  try {
    const column = s.columns[e.col];
    if (!column) return true;

    if (!column.aggregate && !e.cell.classList.contains("wj-aggregate")) {
      const columnHeader = column.header || "";
      if (!columnHeader.includes("합계") && !columnHeader.toLowerCase().includes("total")) {
        return false;
      }
    }

    return true;
  } catch {
    return true;
  }
};

// 합계를 구성하는 값들 중 마지막 값 찾기
const findLastValueInSum = (s: PivotGrid, e: any): number | null => {
  try {
    const currentRowIndex = e.row;

    for (let colIndex = e.col - 1; colIndex >= 0; colIndex--) {
      const column = s.columns[colIndex];
      if (column && !column.aggregate) {
        try {
          const cellValue = s.getCellData(currentRowIndex, colIndex, false);
          if (typeof cellValue === "number" && !isNaN(cellValue) && cellValue !== 0) {
            return cellValue;
          }
        } catch {
          continue;
        }
      }
    }

    for (let colIndex = e.col - 1; colIndex >= 0; colIndex--) {
      const column = s.columns[colIndex];
      if (column && !column.aggregate) {
        try {
          const cellValue = s.getCellData(currentRowIndex, colIndex, false);
          if (typeof cellValue === "number" && !isNaN(cellValue)) {
            return cellValue;
          }
        } catch {
          continue;
        }
      }
    }

    return null;
  } catch (error) {
    console.error("마지막 값 찾기 실패:", error);
    return null;
  }
};

// text-week 부분합인지 확인
const isTextWeekSubtotalCheck = (s: PivotGrid, e: any): boolean => {
  try {
    const column = s.columns[e.col];
    if (!column || !column.header) return false;

    const columnHeader = column.header;

    const hasWeek = columnHeader.includes("주") || columnHeader.includes("text-week");
    const hasMonth = columnHeader.includes("월") || columnHeader.includes("text-month");
    const isWeekSubtotal = !hasWeek && hasMonth;

    return isWeekSubtotal;
  } catch {
    return false;
  }
};

// 총합계인지 확인
const isGrandTotalCheck = (s: PivotGrid, e: any): boolean => {
  try {
    const column = s.columns[e.col];
    if (!column || !column.header) return false;

    const columnHeader = column.header;

    const hasWeek = columnHeader.includes("주") || columnHeader.includes("text-week");
    const hasMonth = columnHeader.includes("월") || columnHeader.includes("text-month");
    const isMonthSubtotal = !hasWeek && !hasMonth;

    return isMonthSubtotal;
  } catch {
    return false;
  }
};

// 전체 데이터에서 마지막 주차의 마지막 날짜 값 찾기
const findLastValueInAllData = (dataItem: any) => {
  try {
    const keys = Object.keys(dataItem);

    const dateKeys = keys.filter((key) => key.includes("text-date") || key.includes("날짜"));

    if (dateKeys.length === 0) {
      return null;
    }

    let lastDateKey = "";
    let maxDate = "";

    for (const key of dateKeys) {
      if (key.includes("text-date")) {
        const dateMatch = key.match(/text-date:(\d{4}-\d{2}-\d{2})/);
        if (dateMatch) {
          const currentDate = dateMatch[1];
          if (currentDate > maxDate) {
            maxDate = currentDate;
            lastDateKey = key;
          }
        }
      }

      if (key.includes("날짜")) {
        const dateMatch = key.match(/날짜:(\d{4}-\d{2}-\d{2})/);
        if (dateMatch) {
          const currentDate = dateMatch[1];
          if (currentDate > maxDate) {
            maxDate = currentDate;
            lastDateKey = key;
          }
        }
      }
    }

    if (!lastDateKey) {
      return null;
    }

    const lastValue = dataItem[lastDateKey];

    return typeof lastValue === "number" ? lastValue : null;
  } catch (error) {
    console.error("findLastValueInAllData 에러:", error);
    return null;
  }
};

const updateView = () => {
  if (extendPivot.value) {
    extendPivot.value.hidePanel();
  } else {
    console.warn("첫 조회를 먼저 수행해 주세요.");
  }
};

// frozen plan info
const frozenPlanVerInfo = computed(() => {
  if (currentPlanCycleSource.value?.frozen_plan_ver) {
    return currentPlanCycleSource.value?.frozen_plan_ver;
  }
  return "-";
});

// 원본 ReExecutePlan.vue: demandVerSource(ComDemandVer) 최신 항목의 demand_ver.
const demandVerInfo = computed(() => {
  const list = useReExecutePlan.demandVerSource?.value;
  if (list && list.length) {
    return list[list.length - 1]?.demand_ver ?? "-";
  }
  return "-";
});

watch(
  demandSource,
  (newValue) => {
    if (
      newValue &&
      newValue.length > 0 &&
      (!sharedCollectionView.value || (sharedDataSource.value as any)?.length === 0)
    ) {
      initializeSharedCollectionView();
    }
  },
  { immediate: true },
);

// Demand source loading helper
const loadDemandSourceData = async () => {
  await loadDemandSource({
    plan_ver: planVer.value,
    schema_name: "Demand",
  });
};

// 컴포넌트 언마운트 시 이벤트 리스너 정리
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);

  if (grid.value?.hostElement) {
    grid.value.hostElement.removeEventListener("click", onFlexGridClick);
    grid.value.hostElement.removeEventListener("mousedown", onFlexGridInteraction);
    grid.value.hostElement.removeEventListener("keydown", onFlexGridInteraction);
  }

  if (pivot.value?.hostElement) {
    pivot.value.removeEventListener(pivot.value.hostElement, "click", onPivotCellClick);
  }
  if (pivot.value?.loadedRows) {
    pivot.value.loadedRows.removeHandler(onPivotLoadedRows);
  }
});

// FROZEN PLAN VER 정보 조회 (Vue file level)
const loadPlanCycleInfoLocal = async () => {
  if (!planVer.value) return;
  try {
    const { fetchPlanCycleInfo: fetchPCI } = await import("./reExecutePlan");
    const result = await fetchPCI(planVer.value);
    if (result && result.data) {
      currentPlanCycleSource.value = result.data;
    } else {
      currentPlanCycleSource.value = {};
    }
  } catch {
    console.error("PlanCycleInfo 조회 오류");
    currentPlanCycleSource.value = {};
  }
};

onMounted(async () => {
  await loadPlanCycleInfoLocal();
});

// planVer가 host에서 주입된 후에도 다시 로드
watch(planVer, async () => {
  await loadPlanCycleInfoLocal();
});

const callWatch = watch(
  [
    planVer,
    custIsSuccess,
    itemGroupIsSuccess,
    regionIsSuccess,
    demandTypeIsSuccess,
    getOperGroupSourceIsSuccess,
    getOperSourceIsSuccess,
    getBufferSourceIsSuccess,
  ],
  () => {
    if (
      planVer.value &&
      custIsSuccess.value &&
      itemGroupIsSuccess.value &&
      regionIsSuccess.value &&
      demandTypeIsSuccess.value &&
      getOperGroupSourceIsSuccess.value &&
      getOperSourceIsSuccess.value &&
      getBufferSourceIsSuccess.value
    ) {
      nextTick(() => {
        onLoad();
        callWatch();
      });
    }
  },
  { immediate: true, flush: "post" },
);

watch([planVer, pivotDataSource], () => {
  setTimeout(() => {
    if (localState.collapsibleSubtotals) {
      // toggleCollapsibleSubtotals();
    }
  }, 100);
});
</script>
<style scoped lang="scss">
.re-execute-plan-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.re-execute-pane {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modify-demand-pane {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

// 음수 값 스타일
:deep(.negative-number) {
  span {
    color: #dc5a5a !important;
  }
}

.info-frozen-plan-wrapper {
  max-width: fit-content;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  border: 1px solid #bac6d4;
  border-radius: 50px;
  background-color: #f8f8fd;
  margin-right: 5px;
  padding: 0 10px;

  .info-frozen-plan-icon {
    width: 14px;
    height: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #4568e0;
    border: 1.5px solid #4568e0;
    border-radius: 50%;
  }

  .info-frozen-plan-text {
    font-size: 13px;
    color: #434c60;
    word-break: break-all;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
  }

  .info-frozen-plan-ver {
    color: #4568e0;
  }
}

:deep(.include-qty-uom) {
  .wj-cell-text {
    width: 100% !important;
  }
}

:deep(.wj-aggregate:not(.wj-header)) {
  background-color: white !important;
}
:deep(.wj-cell:not(.wj-header):not(.wj-aggregate) + .wj-aggregate) {
  background-color: #d6def8 !important;
}

.ver-info-container {
  border-radius: 4px;
  border: 1px solid #e1e3f0;
  background: #f8f8fd;
  padding: 12px 29px 12px 12px;
  gap: 10px;
  display: flex;
  flex-direction: column;

  .ver-info-item {
    display: flex;
    font-size: 12px;
    justify-content: space-between;

    .title {
      font-weight: 500;
      color: #28364e;
    }

    .value {
      color: #565f6e;
    }
  }
}
</style>
