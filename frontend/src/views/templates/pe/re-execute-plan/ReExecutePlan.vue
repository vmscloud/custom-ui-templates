<template>
  <div class="re-execute-plan-page">
  <Controller
    :navigations="navigations"
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
        <div ref="pivotPaneRef" class="re-execute-pane">
          <!-- 원본은 월 헤더 셀에 단위를 붙였다. 피벗 헤더에는 열 필드명 셀이 없어 그리드 위에 표시한다. -->
          <div class="pivot-uom-label">{{ uomLabel }}</div>
          <div class="pivot-grid-wrapper">
            <MozGrid
              name="re-execute-plan-pivot"
              class="prod-plan-ins-main"
              :coreConfig="pivotConfig"
              height="100%"
              :useToolBox="false"
              :useToolBoxSetting="false"
              :loading="false"
              @ready="pivotOnReady"
              @data:loaded="onPivotDataLoaded"
              @cell:click="onPivotCellClick"
            />
          </div>
          <!-- 그리드 내장 loading 은 끄고, fetch + 피벗 집계 전 구간을 overlay 로 커버. -->
          <div v-if="isPivotRendering" class="pivot-rendering-overlay">
            <div class="pivot-rendering-spinner"></div>
            <div class="pivot-rendering-text">{{ t('text-loading') || '로딩 중...' }}</div>
          </div>
        </div>
      </Pane>
      <Pane size="40%" min-size="30%">
        <div ref="demandPaneRef" class="modify-demand-pane">
          <MozGrid
            class="demand-grid"
            name="re-execute-plan-extend-grid"
            :coreConfig="demandGridConfig"
            height="100%"
            :loading="getDemandSourceIsPending"
            :contextMenuConfig="{
              useViewSelectColumn: true,
              useBulkEditColumn: true,
            }"
            @ready="onDemandGridReady"
            @data:loaded="onDemandDataLoaded"
          />
        </div>
      </Pane>
    </SplitPane>
  </div>

  <ReExecutePlanPop
    v-if="isOpen"
    :visible="isOpen"
    :popupDataSource="(useReExecutePlan.popupDataSource.value as any[]) || []"
    :demandSource="(useReExecutePlan.mergedDemandSource.value as any[]) || []"
    :alwaysEditedData="(useReExecutePlan.alwaysEditedData.value as any[]) || []"
    :editedDemandFields="useReExecutePlan.editedDemandFields.value"
    :propColumns="useReExecutePlan.propColumns.value"
    :executionFlowSource="useReExecutePlan.executionFlowSource.value"
    :scenarioList="useReExecutePlan.scenarioList.value"
    :inboundSource="useReExecutePlan.inboundSource.value"
    :scenarioModuleDataSource="useReExecutePlan.scenarioModuleDataSource.value"
    :scenarioConfigSource="useReExecutePlan.scenarioConfigSource.value"
    :phaseColumns="useReExecutePlan.phaseColumns.value"
    :inboundItemOptions="useReExecutePlan.inboundItemOptions.value"
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
    @demand-edited="onPopupDemandEdited"
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
} from "@vmscloud/moz-ui-components-vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { CellAttributesFn, GridChrome, MozGridCoreProps, PureSheet } from "@vmscloud/moz-ui-grid-vue";
import { useTranslation } from "i18next-vue";
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  shallowRef,
  watch,
} from "vue";
import { useHostPlanCycle, useHostNavigations } from "@/composables/useHostStores";
import { IconLineEdit, IconReExecute } from "@moz-shared/icons";
import { buildDemandFields, useReExecutePlanQuery } from "./reExecutePlan";
import ReExecutePlanPop from "./ReExecutePlanPop.vue";

const { t } = useTranslation(); // 다국어
const navigations = useHostNavigations(() => [t("text-menu-production_planning"), t("text-re_plan_excute")]);
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

  // 수요 그리드 변경 추적
  syncDemandChanges,
  mergedDemandSource,

  // 계획 재실행 pop
  isOpen,
  open: originalOpen,

  // api 호출
  onLoad,
  isPageFetching,
  loadParams,
  isPivotRendering,

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

// 피벗 셀 선택으로 거는 수요 그리드 필터의 그룹 키. 사용자가 건 컬럼 필터와 별도로 관리된다.
const PIVOT_SELECTION_FILTER_KEY = "pivotSelection";

// 피봇 셀 선택 해제 함수
const clearPivotSelection = () => {
  isPivotCellSelected.value = false;
  selectedDemandList.value = [];

  pivotGrid.value?.cells.clearCellSelection();

  applyDemandFilter();
};

// 피벗에서 고른 수요(demand_id)만 수요 그리드에 남긴다.
const applyDemandFilter = async () => {
  const grid = demandGrid.value;
  if (!grid) {
    return;
  }

  const demandIDs = selectedDemandList.value ?? [];
  await grid.setFilterGroup(
    PIVOT_SELECTION_FILTER_KEY,
    isPivotCellSelected.value && demandIDs.length > 0
      ? {
          type: "values",
          priority: 0,
          applied: true,
          states: [{ id: "demand_id", operator: "in", filterValue: demandIDs, sequence: 0 }],
        }
      : null,
  );

  grid.scrollToRow(0);
  grid.cells.clearCellSelection();
};

// 수요 그리드
const demandGrid = shallowRef<PureSheet | null>(null);
const demandPaneRef = ref<HTMLElement | null>(null);

const demandGridConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["demand_id"],
  editable: true,
  data: demandSource.value ?? [],
  fields: buildDemandFields(t, propColumns.value, "main"),
}));

const onDemandGridReady = (grid: PureSheet, chrome: GridChrome) => {
  demandGrid.value = grid;
  // 셀 편집·일괄 편집·행 추가/삭제가 모두 changes:changed 로 모인다.
  chrome.on("changes:changed", () => syncDemandChanges(grid));
  syncDemandChanges(grid);
};

// 원본은 행을 다시 그릴 때마다 그룹을 0레벨까지 접었다.
const onDemandDataLoaded = () => {
  const grid = demandGrid.value;
  if (grid?.rowGroup.getConfig()) {
    grid.rowGroup.collapseAll();
  }
};

const isSameValue = (a: unknown, b: unknown) => {
  if (a == null && b == null) return true;
  if (a instanceof Date && b instanceof Date) return a.getTime() === b.getTime();
  return a === b;
};

// 팝업 그리드에서 고친 값을 메인 수요 그리드의 변경 추적에 반영한다.
//   메인 그리드가 변경의 기준이므로 수정 건수·수정 데이터·재실행 요청이 모두 이 값을 따른다.
const onPopupDemandEdited = async (rows: Record<string, any>[]) => {
  const grid = demandGrid.value;
  if (!grid) return;

  const current = new Map<string, any>(
    mergedDemandSource.value.map((item: any) => [String(item?.demand_id), item]),
  );
  for (const row of rows) {
    const rowId = row?.demand_id;
    const target = current.get(String(rowId));
    if (rowId == null || !target) continue;
    for (const [field, value] of Object.entries(row)) {
      if (field.startsWith("__") || isSameValue(target[field], value)) continue;
      await grid.changes.updateCellById(String(rowId), field, value as any);
    }
  }
};

// 팝업 열기 함수
const openReExecute = () => {
  originalOpen();
};

const closeReExecute = () => {
  useReExecutePlan.close();
};

// ─────────────────────────────────────────────────────────────────
// 피벗 그리드
//   행: 공정그룹 / 집계값 / 계획구분, 열: 월 / 주 / 일, 값: 수량 합계.
//   열 소계·총합계를 표시하고, 행 합계는 표시하지 않는다(원본 ShowTotals 설정과 동일).
// ─────────────────────────────────────────────────────────────────
const pivotGrid = shallowRef<PureSheet | null>(null);
const pivotPaneRef = ref<HTMLElement | null>(null);

// 피벗 컬럼 ID 는 열 필드 값 경로 + 값 필드를 이 구분자로 잇는다(예: 월␞주␞일␞qty).
const PIVOT_COL_SEP = "\u001E";
const PIVOT_SUBTOTAL_KEY = "__subtotal__";
const PIVOT_GRANDTOTAL_KEY = "__grandtotal__";

const RE_DATE = /^\d{4}-\d{2}-\d{2}$/;
const RE_LEADING_DIGIT_PREFIX = /^\d+_/;
const NUMBER_FMT = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

// 컬럼 ID → 소계 여부·소계 범위(월/주 경로)·일자. 컬럼 수만큼만 계산되도록 캐시한다.
type PivotColumnMeta = { isTotal: boolean; scope: string[]; date: string | null };
const pivotColumnMetaCache = new Map<string, PivotColumnMeta>();
const getPivotColumnMeta = (columnId: string): PivotColumnMeta => {
  let meta = pivotColumnMetaCache.get(columnId);
  if (!meta) {
    const path = columnId.split(PIVOT_COL_SEP).slice(0, -1);
    const totalIndex = path.findIndex((p) => p === PIVOT_SUBTOTAL_KEY || p === PIVOT_GRANDTOTAL_KEY);
    const isTotal = totalIndex >= 0;
    const date = !isTotal && RE_DATE.test(path[2] ?? "") ? path[2] : null;
    meta = { isTotal, scope: isTotal ? path.slice(0, totalIndex) : path, date };
    pivotColumnMetaCache.set(columnId, meta);
  }
  return meta;
};

const isDiffRow = (rowData?: Record<string, any>) => String(rowData?.plan_type ?? "").includes("DIFF");

// DIFF 행의 일자 셀 목록(일자 오름차순). 행 객체마다 한 번만 만든다.
type DiffLeaf = { weekPath: string; date: string; value: unknown };
const diffLeafCache = new WeakMap<object, DiffLeaf[]>();
const getDiffLeaves = (rowData: Record<string, any>) => {
  let leaves = diffLeafCache.get(rowData);
  if (!leaves) {
    leaves = [];
    for (const key of Object.keys(rowData)) {
      if (!key.includes(PIVOT_COL_SEP)) continue;
      const meta = getPivotColumnMeta(key);
      if (meta.isTotal || !meta.date) continue;
      leaves.push({ weekPath: meta.scope.slice(0, 2).join(PIVOT_COL_SEP), date: meta.date, value: rowData[key] });
    }
    leaves.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
    diffLeafCache.set(rowData, leaves);
  }
  return leaves;
};

// DIFF(누적) 행의 소계·총합계는 합계 대신 마지막 값을 보여준다.
//   - 월 소계·총합계: 행 전체에서 가장 마지막 일자의 값
//   - 주 소계: 그 주까지(왼쪽) 일자 중 0 이 아닌 마지막 값, 없으면 마지막 숫자 값
const resolveDiffValue = (rowData: Record<string, any> | undefined, columnId: string | undefined) => {
  if (!rowData || !columnId || !isDiffRow(rowData)) return null;
  const meta = getPivotColumnMeta(columnId);
  if (!meta.isTotal) return null;

  const leaves = getDiffLeaves(rowData);
  if (meta.scope.length < 2) {
    const last = leaves[leaves.length - 1]?.value;
    return typeof last === "number" ? last : null;
  }

  const weekPath = meta.scope.slice(0, 2).join(PIVOT_COL_SEP);
  const candidates = leaves.filter((leaf) => leaf.weekPath <= weekPath).reverse();
  const nonZero = candidates.find((leaf) => typeof leaf.value === "number" && !isNaN(leaf.value) && leaf.value !== 0);
  const anyNumber = nonZero ?? candidates.find((leaf) => typeof leaf.value === "number" && !isNaN(leaf.value));
  return anyNumber ? (anyNumber.value as number) : null;
};

const resolveQtyValue = (value: unknown, rowData?: Record<string, any>, columnId?: string) => {
  const diffValue = resolveDiffValue(rowData, columnId);
  return diffValue ?? value;
};

const formatQty = (value: unknown, rowData?: Record<string, any>, columnId?: string) => {
  const shown = resolveQtyValue(value, rowData, columnId);
  if (shown === null || shown === undefined || shown === "") return "";
  const n = Number(shown);
  if (isNaN(n)) return String(shown);
  return NUMBER_FMT.format(Math.round(n * 100) / 100);
};

// 셀 클래스: 음수 / 주 소계·그 외 소계 배경 / 실적 기간 일자 하이라이트
const qtyCellAttributes: CellAttributesFn = ({ value, row, columnId }) => {
  const classes: string[] = [];
  const shown = Number(resolveQtyValue(value, row, columnId));
  if (!isNaN(shown) && shown < 0) {
    classes.push("negative-number");
  }

  const meta = getPivotColumnMeta(columnId);
  if (meta.isTotal) {
    classes.push(meta.scope.length === 2 ? "pivot-week-total" : "pivot-total");
  } else if (meta.date && actStartDate.value && actEndDate.value) {
    if (meta.date >= actStartDate.value && meta.date <= actEndDate.value) {
      classes.push("date-range-highlight");
    }
  }
  return classes.length ? { class: classes.join(" ") } : undefined;
};

// 집계 기준(summaryType)에 맞춘 집계값 헤더
const aggrValueHeader = computed(() => {
  const agg = loadParams.value.aggregateType;
  if (agg === "itemGroup") return t("text-item_group");
  if (agg === "demandType") return t("text-demand_type");
  if (agg === "region") return t("text-upper-region");
  if (agg === "cust") return t("text-upper-customer");
  return t("text-aggr_value");
});

const uomLabel = computed(() => (loadParams.value.uomType === "DEFAULT" ? "(단위: EA)" : "(단위: m²)"));

const pivotConfig = computed<MozGridCoreProps>(() => ({
  mode: "pivot",
  data: pivotDataSource.value,
  rowFields: [
    { field: "oper_group_id", header: t("text-oper_group_id"), dataType: "string" },
    { field: "aggr_value", header: aggrValueHeader.value, dataType: "string" },
    { field: "plan_type", header: t("text-plan_type"), dataType: "string" },
  ],
  columnFields: [
    { field: "month", header: t("text-month"), dataType: "string" },
    { field: "week", header: t("text-week"), dataType: "string" },
    { field: "date", header: t("text-date"), dataType: "string" },
  ],
  valueFields: [
    {
      field: "qty",
      header: t("text-sum"),
      aggregate: "sum",
      dataType: "number",
      align: "right",
      mask: { type: "function", formatter: formatQty },
      cellAttributes: qtyCellAttributes,
    },
  ],
  showRowSubTotals: false,
  showRowGrandTotals: false,
  showColumnSubTotals: true,
  showColumnGrandTotals: true,
  showZeros: false,
}));

// 계획구분 값의 정렬용 접두어(1_ / 2_ / 3_)를 떼고, DIFF 는 누적임을 표시한다.
const toPlanTypeLabel = (value: string) => {
  const label = value.replace(RE_LEADING_DIGIT_PREFIX, "");
  return label === "DIFF" ? "DIFF(cum)" : label;
};

const replaceCellText = (element: HTMLElement, from: string, to: string) => {
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (node.nodeValue?.trim() === from) {
      node.nodeValue = to;
      return;
    }
  }
};

const pivotOnReady = (grid: PureSheet) => {
  pivotGrid.value = grid;

  grid.formatRow.addHandler("planTypeLabel", (info: any) => {
    if (info.type !== "data") return;
    const cell = info.ctx.cells["plan_type"];
    if (!cell || cell.value == null) return;
    const raw = String(cell.value);
    const label = toPlanTypeLabel(raw);
    if (label !== raw) {
      replaceCellText(cell.element, raw, label);
    }
  });
};

// 같은 조회 결과로 접기를 반복하지 않도록 마지막으로 접은 데이터를 기억한다.
let collapsedPivotData: unknown = null;

const onPivotDataLoaded = async () => {
  // 원본과 같이 주 단위까지만 펼친다(일자 열은 접어 주 소계로 표시).
  if (pivotGrid.value && pivotDataSource.value.length && collapsedPivotData !== pivotDataSource.value) {
    collapsedPivotData = pivotDataSource.value;
    await pivotGrid.value.pivot.collapseColumnAtLevel(1);
  }
  // 피벗 집계·렌더가 끝난 시점. 한 프레임 뒤에 스피너 내림.
  if (isPivotRendering.value) {
    requestAnimationFrame(() => {
      isPivotRendering.value = false;
    });
  }
};

// 문서 전체 클릭 이벤트 (피봇 그리드 외부 클릭 감지)
const onDocumentClick = (e: MouseEvent) => {
  if (!pivotGrid.value) return;

  if (!e.isTrusted) {
    return;
  }

  const pivotElement = pivotPaneRef.value;
  const target = e.target as Element;

  const isModifyDemandPaneClick = demandPaneRef.value?.contains(target) || target.closest(".modify-demand-pane");

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

// 피봇 그리드 셀 클릭 이벤트 핸들러 — 데이터·행 헤더 셀 모두 해당 행 기준으로 처리
const onPivotCellClick = (payload: unknown) => {
  const row = (payload as { row?: Record<string, any> } | undefined)?.row;
  if (!row || row.__pivotType !== "data") return;
  getRowDataWithTotalFilter(row);
};

const PIVOT_ROW_KEYS = ["oper_group_id", "aggr_value", "plan_type"];
const TOTAL_MATCH_KEYS = ["aggr_value", "buffer_id", "plan_type"];

// 클릭한 피벗 행의 date 가 TOTAL 인 원본 행에서 demandIDs 를 찾아 수요 그리드를 거른다.
const getRowDataWithTotalFilter = (pivotRow: Record<string, any>) => {
  try {
    // 피벗 행을 이루는 첫 원본 행(행 키 정보). buffer_id 처럼 행 필드가 아닌 값은 여기서 얻는다.
    const rowKeyInfo = pivotDataSource.value.find((item: any) =>
      PIVOT_ROW_KEYS.every((key) => isSameValue(item[key], pivotRow[key])),
    );
    if (!rowKeyInfo) {
      console.warn("행 데이터를 찾을 수 없습니다.");
      return;
    }

    const sourceTotalData = (fullDataSource.value || []).filter(
      (item: any) =>
        item.date === "TOTAL" && TOTAL_MATCH_KEYS.every((key) => isSameValue(rowKeyInfo[key], item[key])),
    );

    if (sourceTotalData.length > 0 && sourceTotalData[0].demandIDs) {
      selectedDemandList.value = sourceTotalData[0].demandIDs;
      isPivotCellSelected.value = true;
      applyDemandFilter();
    } else {
      clearPivotSelection();
    }
  } catch (error) {
    console.error("행 데이터 처리 실패:", error);
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

// Demand source loading helper
const loadDemandSourceData = async () => {
  await loadDemandSource({
    plan_ver: planVer.value,
    schema_name: "Demand",
  });
};

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
});

// 컴포넌트 언마운트 시 이벤트 리스너 정리
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
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
  width: 100%;
  position: relative;
  display: flex;
  flex-direction: column;

  .pivot-uom-label {
    flex: 0 0 auto;
    padding: 2px 4px 4px;
    font-size: 12px;
    color: #434c60;
  }

  .pivot-grid-wrapper {
    flex: 1;
    min-height: 0;
  }
}

.pivot-rendering-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(1px);
  z-index: 20;
  pointer-events: auto;
}

.pivot-rendering-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #d6def8;
  border-top-color: #4568e0;
  border-radius: 50%;
  animation: pivot-rendering-spin 0.8s linear infinite;
}

.pivot-rendering-text {
  font-size: 12px;
  color: #434c60;
  font-weight: 500;
}

@keyframes pivot-rendering-spin {
  to {
    transform: rotate(360deg);
  }
}

.modify-demand-pane {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;

  .demand-grid {
    width: 100%;
  }
}

// 음수 값 스타일
:deep(.ps-cell.negative-number) {
  color: #dc5a5a !important;
}

// 실적 기간(actStartDate ~ actEndDate) 일자 셀
:deep(.ps-cell.date-range-highlight) {
  background-color: #357e631a;
}

// 열 소계: 일자 바로 뒤의 주 소계는 강조, 월 소계·총합계는 흰 배경
:deep(.ps-cell.pivot-total) {
  background-color: white !important;
}
:deep(.ps-cell.pivot-week-total) {
  background-color: #d6def8 !important;
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
