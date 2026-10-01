<template>
  <!-- 합계 행(하단 고정)은 구조 행이라 클릭 이벤트가 없어 래퍼에서 mousedown 을 받는다 -->
  <div class="rtf-report-sub1-grid" @mousedown="onWrapperMouseDown">
    <MozGrid
      :key="summaryType"
      name="onTimeReplanSummary"
      :coreConfig="coreConfig"
      height="100%"
      :loading="loading"
      :use-tool-box="false"
      :use-sort="false"
      @ready="onGridReady"
      @data:loaded="onDataLoaded"
      @cell:click="onCellClick"
      @rowGroup:toggle="onGroupToggle"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type {
  FieldDef,
  MaskConfig,
  MozGridCoreProps,
  PureSheet,
} from "@vmscloud/moz-ui-grid-vue";
import { GRID_ROW_KEY, withRowKey } from "./onTimeRescheduledPlanResult";
import type { ReplanRtfSummary } from "./onTimeRescheduledPlanResult";

const { t } = useTranslation();

// === Props & Emits ===

interface Props {
  data: ReplanRtfSummary[];
  summaryType: string;
  aggType: string;
  loading: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "row-selected", item: ReplanRtfSummary): void;
}>();

// === Local State ===

let summaryGrid: PureSheet | null = null;
const summaryRows = ref<ReplanRtfSummary[]>([]);
const summaryTotalRowData = ref<any>(null);
const isTempGroupColumnTitle = ref<boolean>(true);

// === Computed ===

const groupingColumnHeader = computed(() => {
  if (!isTempGroupColumnTitle.value) {
    switch (props.summaryType) {
      case "itemGroup":
        return t('text-item_group');
      case "cust":
        return t('text-customer');
      case "prodType":
        return t('text-prod_type');
    }
  }
  return props.aggType === "MONTH" ? t('text-due_month') : t('text-due_week');
});

// === Ratio Formatting ===

const formatNumber = (num: number) => {
  const truncated = Number(num.toFixed(1));
  if (truncated % 1 === 0)
    return truncated.toLocaleString("en-US", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
  return truncated.toLocaleString("en-US", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
};

// 데이터 행·그룹 행(평균) 비율 표시
const RATIO_MASK: MaskConfig = {
  type: "function",
  formatter: (value: unknown) =>
    typeof value === "number" ? `${formatNumber(value)}%` : "",
};

const RATIO_IDS = ["ratio_early", "ratio_ontime", "ratio_late", "ratio_short", "ratio_rtf"];

// ratio_rtf 헤더 아래 보조 문구
const renderRtfRatioHeader = ({ header }: { header: string }) => {
  const headerDiv = document.createElement("div");
  headerDiv.style.display = "flex";
  headerDiv.style.flexDirection = "column";
  headerDiv.style.alignItems = "center";
  headerDiv.style.justifyContent = "center";
  headerDiv.style.height = "100%";

  const mainHeader = document.createElement("div");
  mainHeader.textContent = header;
  mainHeader.classList.add("rtf-ratio-main-header");

  const subHeader = document.createElement("div");
  subHeader.textContent = t('text-isu_early_ontime_late');
  subHeader.classList.add("rtf-ratio-sub-header");

  headerDiv.appendChild(mainHeader);
  headerDiv.appendChild(subHeader);
  return headerDiv;
};

// 그룹 행에는 unmergeOnGroupRow 컬럼만 자기 셀에 집계값(aggregate)을 보여 준다.
const fields = computed<FieldDef[]>(() => [
  { id: "due", header: groupingColumnHeader.value, dataType: "string", width: 120, align: "center" },
  // 그룹 값은 그룹 행 제목에 보이므로 컬럼은 숨긴다
  { id: "group_name", header: "그룹", dataType: "string", width: 80, align: "center", hidden: true },
  { id: "ratio_early", header: t('text-isu_early'), dataType: "number", width: 90, align: "right", mask: RATIO_MASK, aggregate: "avg", unmergeOnGroupRow: true },
  { id: "ratio_ontime", header: t('text-isu_ontime'), dataType: "number", width: 90, align: "right", mask: RATIO_MASK, aggregate: "avg", unmergeOnGroupRow: true },
  { id: "ratio_late", header: t('text-isu_late'), dataType: "number", width: 90, align: "right", mask: RATIO_MASK, aggregate: "avg", unmergeOnGroupRow: true },
  { id: "ratio_short", header: t('text-isu_short'), dataType: "number", width: 90, align: "right", mask: RATIO_MASK, aggregate: "avg", unmergeOnGroupRow: true },
  {
    id: "ratio_rtf",
    header: t('text-isu_otd_expected_rate'),
    dataType: "number",
    width: 110,
    align: "right",
    mask: RATIO_MASK,
    aggregate: "avg",
    unmergeOnGroupRow: true,
    headerRenderer: renderRtfRatioHeader,
  },
]);

// 펼친 그룹 행 위에 구분선을 긋는다 (행 DOM 재사용을 고려해 toggle)
const formatRow = (info: any) => {
  if (info.type !== "group-row") return;
  info.ctx.element.classList.toggle("rtf-report-group-separator", !info.ctx.collapsed);
};

const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: summaryRows.value,
  fields: fields.value,
  columnGroups: [
    {
      id: "rtfRate",
      header: t('text-isu_rtf_rate'),
      children: ["ratio_early", "ratio_ontime", "ratio_late", "ratio_short"],
    },
  ],
  rowGroupConfig: { columns: ["group_name"], defaultCollapsed: true },
  formatRow,
}));

// === Grid Initialization ===

const onGridReady = (grid: PureSheet) => {
  summaryGrid = grid;

  // 하단 TOTAL 행 — 서버가 준 [TOTAL] 행의 비율을 그대로 보여 준다
  grid.rows.addPinnedBottom({
    structural: true,
    variant: "grandtotal",
    pinned: "bottom",
    className: "summary-footer",
    aggregates: [
      { columnId: "due", func: "count", formatter: () => "[TOTAL]" },
      ...RATIO_IDS.map((columnId) => ({
        columnId,
        func: "avg" as const,
        formatter: () =>
          `${formatNumber(Number(summaryTotalRowData.value?.[columnId] ?? 0))}%`,
      })),
    ],
  });
};

const onDataLoaded = () => {
  summaryGrid?.rows.refreshPinned();
};

// === Data Processing ===

async function processData(rawData: ReplanRtfSummary[]) {
  isTempGroupColumnTitle.value = true;

  if (!rawData || rawData.length === 0) {
    summaryRows.value = [];
    summaryTotalRowData.value = null;
    return;
  }

  // Filter [SUB TOTAL], separate [TOTAL] row
  const data = rawData.filter((item) => item.due !== "[SUB TOTAL]");
  const totalRow = data.find((item) => item.due === "[TOTAL]") ?? null;
  const dataRows = data.filter((item) => item.due !== "[TOTAL]");

  // Assign group_name for grouping
  const dataWithGroupName = dataRows.map((item) => ({
    ...item,
    group_name:
      props.summaryType === "cust"
        ? item.custID
        : props.summaryType === "prodType"
          ? item.prodType
          : item.itemGroupID,
  }));

  summaryTotalRowData.value = totalRow;

  summaryRows.value = withRowKey(dataWithGroupName);

  isTempGroupColumnTitle.value = false;

  // Auto-select first group after data loads
  await nextTick();
  emitGroupSubTotal(summaryRows.value[0]?.group_name);
}

watch(
  [() => props.data, () => props.summaryType],
  () => processData(props.data),
  { immediate: true },
);

// === Selection ===

// 그룹 행 → 그룹의 첫 행을 due="[SUB TOTAL]" 로 emit
function emitGroupSubTotal(groupName: unknown) {
  if (groupName === undefined) return;
  const firstItem = summaryRows.value.find(
    (item) => String(item.group_name ?? "") === String(groupName ?? ""),
  );
  if (!firstItem) return;
  emit("row-selected", { ...firstItem, due: "[SUB TOTAL]" });
}

// 그룹 행은 선택 대상이 아니라 펼침/접힘 클릭을 그룹 선택으로 받는다
const onGroupToggle = (e: any) => {
  if (e?.source !== "user" || typeof e.groupId !== "string") return;
  emitGroupSubTotal(e.groupId.slice(e.groupId.indexOf(":") + 1));
};

const onCellClick = (e: any) => {
  const dataItem = e?.row as ReplanRtfSummary | undefined;
  if (dataItem && Object.keys(dataItem)?.length) {
    emit("row-selected", dataItem);
  }
};

// TOTAL 행 클릭 → 서버 TOTAL 행 emit 후 셀 선택 해제
const onWrapperMouseDown = (e: MouseEvent) => {
  if (!(e.target as HTMLElement | null)?.closest(".ps-pinned-bottom")) return;
  if (summaryTotalRowData.value) {
    emit("row-selected", { ...summaryTotalRowData.value, due: "[TOTAL]" });
  }
  summaryGrid?.cells.clearCellSelection();
};
</script>

<style lang="scss">
.rtf-report-sub1-grid {
  height: 100%;
  width: 100%;

  .ps-group-row {
    font-weight: 500;
  }

  .rtf-ratio-main-header {
    font-weight: 500;
    margin-bottom: 2px;
  }

  .rtf-ratio-sub-header {
    font-size: 0.65rem;
    color: #6b7280;
    font-weight: 400;
    white-space: nowrap;
  }
}

.summary-footer .ps-cell {
  border-right: 1px solid #c1c1d8 !important;
  border-bottom: 1px solid #c1c1d8;
  background-color: #d6def8 !important;
  font-weight: 500;
  cursor: pointer;
}

.rtf-report-group-separator {
  box-shadow: 0px -1px 0px 0px #6a7184;
}
</style>
