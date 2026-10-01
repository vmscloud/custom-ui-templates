<template>
  <!-- 합계 행(하단 고정)은 구조 행이라 클릭 이벤트가 없어 래퍼에서 mousedown 을 받는다 -->
  <div class="rtf-report-summary" @mousedown="onWrapperMouseDown">
    <MozGrid
      :key="summaryType"
      name="rtfReportSummary"
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
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type {
  FieldDef,
  MozGridCoreProps,
  PureSheet,
} from "@vmscloud/moz-ui-grid-vue";
import { GRID_ROW_KEY, withRowKey } from "./rtfReport";
import type { RtfSummaryData } from "./rtfReport";

// === Props & Emits ===

interface Props {
  data: RtfSummaryData[];
  summaryType: string;
  aggType: string;
  loading: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "row-selected", item: RtfSummaryData): void;
}>();

// === Local State ===

let summaryGrid: PureSheet | null = null;
const summaryRows = ref<RtfSummaryData[]>([]);
const summaryTotalRowData = ref<any>();
const isTempGroupColumnTitle = ref<boolean>(true);

// === Computed ===

const groupingColumnHeader = computed(() => {
  if (!isTempGroupColumnTitle.value) {
    switch (props.summaryType) {
      case "itemGroup":
        return "제품 그룹";
      case "cust":
        return "고객";
      case "region":
        return "지역";
      case "demandType":
        return "수요 유형";
    }
  }
  return props.aggType === "MONTH" ? "기간 (Month)" : "기간 (Week)";
});

// 그룹 행에는 unmergeOnGroupRow 컬럼만 자기 셀에 집계값(aggregate)을 보여 준다.
// 숨김 컬럼에 aggregate 를 주면 그룹 행 제목에 집계 문구가 붙으므로 숨김 컬럼은 집계하지 않는다.
const fields = computed<FieldDef[]>(() => [
  { id: "due", header: groupingColumnHeader.value, dataType: "string", width: 120, align: "center" },
  // 그룹 값은 그룹 행 제목에 보이므로 컬럼은 숨긴다
  { id: "group_name", header: "그룹", dataType: "string", width: 80, align: "center", hidden: true },
  { id: "demandCnt", header: "수요 건수", dataType: "number", width: 80, aggregate: "sum", unmergeOnGroupRow: true },
  { id: "demandQty", header: "수요 수량", dataType: "number", width: 90, align: "right", mask: { type: "numeric", pattern: "#,##0" }, aggregate: "sum", unmergeOnGroupRow: true },
  { id: "rtfQty", header: "RTF 수량", dataType: "number", width: 90, align: "right", mask: { type: "numeric", pattern: "#,##0" }, aggregate: "sum", unmergeOnGroupRow: true },
  { id: "qtyUom", header: "단위", dataType: "string", width: 90, hidden: true },
  { id: "onTimeRatio", header: "정시 생산 비율", dataType: "number", width: 90, align: "right", aggregate: "avg", unmergeOnGroupRow: true },
  { id: "onTimeQty", header: "On-Time 수량", dataType: "number", width: 90, align: "right", hidden: true, mask: { type: "numeric", pattern: "#,##0" } },
  { id: "lateRatio", header: "지연 비율", dataType: "number", width: 90, align: "right", aggregate: "avg", unmergeOnGroupRow: true },
  { id: "lateQty", header: "Late 수량", dataType: "number", width: 90, align: "right", hidden: true, mask: { type: "numeric", pattern: "#,##0" } },
  { id: "rtfRatio", header: "RTF 비율", dataType: "number", width: 90, align: "right", aggregate: "avg", unmergeOnGroupRow: true },
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
  rowGroupConfig: { columns: ["group_name"], defaultCollapsed: true },
  formatRow,
}));

// === Grid Initialization ===

const onGridReady = (grid: PureSheet) => {
  summaryGrid = grid;

  // 하단 TOTAL 행 — 컬럼 집계값을 보여 주는 구조 행
  grid.rows.addPinnedBottom({
    structural: true,
    variant: "grandtotal",
    pinned: "bottom",
    className: "summary-footer",
    aggregates: [
      { columnId: "due", func: "count", formatter: () => "[TOTAL]" },
      { columnId: "demandCnt", func: "sum" },
      { columnId: "demandQty", func: "sum", formatter: formatQty },
      { columnId: "rtfQty", func: "sum", formatter: formatQty },
      { columnId: "onTimeRatio", func: "avg" },
      { columnId: "onTimeQty", func: "sum", formatter: formatQty },
      { columnId: "lateRatio", func: "avg" },
      { columnId: "lateQty", func: "sum", formatter: formatQty },
      { columnId: "rtfRatio", func: "avg" },
    ],
  });
};

const onDataLoaded = () => {
  summaryGrid?.rows.refreshPinned();
};

function formatQty(value: unknown) {
  return typeof value === "number" ? value.toLocaleString() : "";
}

// === Data Processing ===

async function processData(rawData: RtfSummaryData[]) {
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

  summaryTotalRowData.value = totalRow;

  // Grouping by group_name
  summaryRows.value = withRowKey(dataRows);

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
  const dataItem = e?.row as RtfSummaryData | undefined;
  if (dataItem && Object.keys(dataItem)?.length) {
    emit("row-selected", dataItem);
  }
};

// TOTAL 행 클릭 → 서버 TOTAL 행 emit 후 셀 선택 해제
const onWrapperMouseDown = (e: MouseEvent) => {
  if (!(e.target as HTMLElement | null)?.closest(".ps-pinned-bottom")) return;
  if (summaryTotalRowData.value) {
    emit("row-selected", {
      ...summaryTotalRowData.value,
      due: "[TOTAL]",
    });
  }
  summaryGrid?.cells.clearCellSelection();
};
</script>

<style lang="scss">
.rtf-report-summary {
  height: 100%;
  width: 100%;
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

.rtf-report-summary .ps-group-row {
  font-weight: 500;
}
</style>
