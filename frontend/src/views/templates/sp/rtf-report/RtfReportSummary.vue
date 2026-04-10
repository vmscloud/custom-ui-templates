<template>
  <ExtendFlexGrid
    :key="summaryType"
    name="rtfReportSummary"
    :itemsSource="summaryDataSource"
    height="100%"
    :isReadOnly="true"
    allowSorting="None"
    :initialized="onInitialized"
    :selectionChanged="onSelectionChanged"
    :formatItem="formatItem"
    :loading="loading"
    :use-tool-box="false"
  >
    <WjFlexGridColumn
      binding="due"
      :header="groupingColumnHeader"
      aggregate="Cnt"
      :width="120"
      align="center"
      dataType="String"
    />
    <WjFlexGridColumn
      binding="group_name"
      header="그룹"
      :width="80"
      :visible="true"
      align="center"
    />
    <WjFlexGridColumn
      binding="demandCnt"
      header="수요 건수"
      aggregate="Sum"
      :width="80"
    />
    <WjFlexGridColumn
      binding="demandQty"
      header="수요 수량"
      dataType="Number"
      aggregate="Sum"
      :width="90"
      align="right"
      format="n0"
    />
    <WjFlexGridColumn
      binding="rtfQty"
      header="RTF 수량"
      dataType="Number"
      aggregate="Sum"
      :width="90"
      align="right"
      format="n0"
    />
    <WjFlexGridColumn
      binding="qtyUom"
      header="단위"
      dataType="String"
      :width="90"
      :visible="false"
    />
    <WjFlexGridColumn
      binding="onTimeRatio"
      header="정시 생산 비율"
      dataType="Number"
      aggregate="Avg"
      align="right"
      :width="90"
    />
    <WjFlexGridColumn
      binding="onTimeQty"
      header="On-Time 수량"
      dataType="Number"
      aggregate="Sum"
      align="right"
      :width="90"
      :visible="false"
      format="n0"
    />
    <WjFlexGridColumn
      binding="lateRatio"
      header="지연 비율"
      dataType="Number"
      aggregate="Avg"
      align="right"
      :width="90"
    />
    <WjFlexGridColumn
      binding="lateQty"
      header="Late 수량"
      dataType="Number"
      aggregate="Sum"
      align="right"
      :width="90"
      :visible="false"
      format="n0"
    />
    <WjFlexGridColumn
      binding="rtfRatio"
      header="RTF 비율"
      dataType="Number"
      aggregate="Avg"
      align="right"
      :width="90"
    />
  </ExtendFlexGrid>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { CollectionView } from "@vmscloud/moz-wijmo-grid/wijmo";
import {
  type FlexGrid,
  GroupRow,
  CellRange,
} from "@vmscloud/moz-wijmo-grid/wijmo.grid";
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

const summaryGrid = ref<FlexGrid>();
const summaryExtendGrid = ref<ExtendGrid | null>(null);
const summaryDataSource = ref<CollectionView>(new CollectionView([]));
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

// === Grid Initialization ===

const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  summaryGrid.value = flexGrid;
  summaryExtendGrid.value = _extendGrid;

  const extraRow = new GroupRow();
  summaryGrid.value.columnFooters.rows.push(extraRow);
};

// === Data Processing ===

async function processData(rawData: RtfSummaryData[]) {
  isTempGroupColumnTitle.value = true;

  if (!rawData || rawData.length === 0) {
    summaryDataSource.value = new CollectionView([]);
    summaryTotalRowData.value = null;
    return;
  }

  // Filter [SUB TOTAL], separate [TOTAL] row
  const data = rawData.filter((item) => item.due !== "[SUB TOTAL]");
  const totalRow = data.find((item) => item.due === "[TOTAL]") ?? null;
  const dataRows = data.filter((item) => item.due !== "[TOTAL]");

  summaryTotalRowData.value = totalRow;

  // Grouping by group_name
  summaryDataSource.value = new CollectionView(dataRows, {
    groupDescriptions: ["group_name"],
  });

  isTempGroupColumnTitle.value = false;

  await nextTick();
  if (summaryGrid.value) {
    summaryGrid.value.collapseGroupsToLevel(0);

    // Hide group_name column after grouping (value shown in GroupRow header)
    const groupNameCol = summaryGrid.value.columns.getColumn("group_name");
    if (groupNameCol) groupNameCol.visible = false;
  }
}

watch(
  [() => props.data, () => props.summaryType],
  () => processData(props.data),
  { immediate: true },
);

// Auto-select first row after data loads
watch(summaryDataSource, (newDS) => {
  if (newDS?.items?.length) {
    nextTick(() => {
      if (summaryGrid.value) {
        summaryGrid.value.select(new CellRange(-1, -1), true);
        summaryGrid.value.select(new CellRange(0, 0, 0, 0), true);
      }
      summaryExtendGrid.value?.refresh();
    });
  }
});

// === Selection Changed ===

const onSelectionChanged = (s: FlexGrid, e: any) => {
  const { row, col } = s.selection;
  if (row < 0 && col < 0) return;

  let dataItem: any;

  if (e.getRow() instanceof GroupRow) {
    // Group row → emit first item with due="[SUB TOTAL]"
    const group = e.getRow()?.dataItem;
    if (!group) return;
    const firstItem = group.items?.[0];
    if (!firstItem) return;
    dataItem = { ...firstItem, due: "[SUB TOTAL]" };
  } else {
    dataItem = e.getRow()?.dataItem;
  }

  if (dataItem && Object.keys(dataItem)?.length) {
    emit("row-selected", dataItem);
  }
};

// === Ratio Helpers ===

const calcFormula = (
  panel: any,
  row: number,
  binding1: string,
  binding2: string,
) =>
  (panel.getCellData(
    row,
    panel.columns.findIndex((col: any) => col.binding === binding1),
    false,
  ) /
    panel.getCellData(
      row,
      panel.columns.findIndex((col: any) => col.binding === binding2),
      false,
    )) *
  100;

const formatNumber = (num: number) => {
  const truncated = Number(num.toFixed(1));
  if (truncated % 1 === 0) return truncated.toFixed(0);
  return truncated.toFixed(1);
};

// === FormatItem ===

const formatItem = (s: FlexGrid, e: any) => {
  const binding = e.getColumn()?.binding;

  // ----- TOTAL Footer (cellType === 5) -----
  if (e.panel.cellType === 5) {
    e.cell.classList.add("summary-footer");
    e.cell.addEventListener("mousedown", () => {
      if (summaryTotalRowData.value) {
        emit("row-selected", {
          ...summaryTotalRowData.value,
          due: "[TOTAL]",
        });
      }
      summaryGrid.value?.select(new CellRange(-1, -1), false);
    });

    if (binding === "rtf_ratio") {
      const val = calcFormula(s.columnFooters, 0, "rtf_qty", "demand_qty");
      if (val != null && !Number.isNaN(val))
        e.cell.innerHTML = `${formatNumber(val)}%`;
    } else if (binding === "on_time_ratio") {
      const val = calcFormula(
        s.columnFooters,
        0,
        "on_time_qty",
        "demand_qty",
      );
      if (val != null && !Number.isNaN(val))
        e.cell.innerHTML = `${formatNumber(val)}%`;
    } else if (binding === "late_ratio") {
      const val = calcFormula(s.columnFooters, 0, "late_qty", "demand_qty");
      if (val != null && !Number.isNaN(val))
        e.cell.innerHTML = `${formatNumber(val)}%`;
    } else if (binding === "due") {
      e.cell.innerText = "[TOTAL]";
    }
    return;
  }

  // ----- Group Row -----
  if (
    e.panel !== s.columnHeaders &&
    s.rows[e.row] instanceof GroupRow
  ) {
    const row = s.rows[e.row];
    if (row instanceof GroupRow && !row.isCollapsed) {
      e.cell.classList.add("rtf-report-group-separator");
    }

    // First visible column: keep expand button + group name
    const visibleColumns = e.panel.columns.filter(
      (column: any) => column.visible,
    );
    const visibleColumnIndex = visibleColumns.indexOf(e.panel.columns[e.col]);

    if (visibleColumnIndex === 0) {
      const btn = e.cell.childNodes[0];
      const spanEl = document.createElement("span");
      spanEl.style.width = "90%";
      spanEl.textContent = s.rows[e.row]?.dataItem?.name;
      spanEl.classList.add("wj-cell-text");
      e.cell.innerHTML = "";
      e.cell.append(btn);
      e.cell.append(spanEl);
    } else {
      const spanEl = document.createElement("span");
      spanEl.classList.add("wj-cell-text");
      spanEl.innerText = e.cell.innerText;
      e.cell.innerHTML = "";
      e.cell.append(spanEl);
    }

    // Recalculate ratio columns for group rows
    if (binding === "rtf_ratio") {
      const val = calcFormula(s, e.row, "rtf_qty", "demand_qty");
      e.cell.innerHTML = `${formatNumber(val) || "0"}%`;
    } else if (binding === "on_time_ratio") {
      const val = calcFormula(s, e.row, "on_time_qty", "demand_qty");
      e.cell.innerHTML = `${formatNumber(val) || "0"}%`;
    } else if (binding === "late_ratio") {
      const val = calcFormula(s, e.row, "late_qty", "demand_qty");
      e.cell.innerHTML = `${formatNumber(val) || "0"}%`;
    }
    return;
  }

  // ----- Separator line before next group -----
  if (s.rows[e.row + 1] instanceof GroupRow) {
    e.cell.classList.add("rtf-report-separator");
  }

  // ----- Regular Data Cell -----
  if (e.panel !== s.cells) return;
  const item = e.getRow()?.dataItem;
  if (!item) return;

  const cell =
    e.cell.querySelector("span") != null
      ? e.cell.querySelector("span")
      : e.cell;

  switch (binding) {
    case "demand_qty":
    case "on_time_qty":
    case "rtf_qty":
    case "late_qty":
      if (typeof item[binding] === "number")
        cell.textContent = item[binding].toLocaleString();
      break;
    case "on_time_ratio":
    case "rtf_ratio":
    case "late_ratio":
      if (typeof item[binding] === "number")
        cell.textContent = `${item[binding].toLocaleString()}%`;
      break;
    default:
      break;
  }
};
</script>

<style lang="scss">
.summary-footer {
  border-right: 1px solid #c1c1d8 !important;
  border-bottom: 1px solid #c1c1d8;
  background-color: #d6def8 !important;
  font-weight: 500;
  cursor: pointer;
  &:focus {
    color: #4568e0;
    &::after {
      content: "";
      border: 2px solid #4568e0;
      width: 100%;
      height: 100%;
      left: 0;
      top: 0;
      position: absolute;
      border-radius: 1px;
    }
  }
}

.rtf-report-separator {
  border-bottom: 1px solid #6a7184 !important;
}

.rtf-report-group-separator {
  box-shadow: 0px -1px 0px 0px #6a7184;
}

:deep(.wj-group) {
  font-weight: 500;
}

:deep(.wj-flexgrid .wj-cell .wj-btn.wj-btn-glyph) {
  width: 20px;
  height: 12px;
}

:deep(.wj-glyph-right),
:deep(.wj-glyph-down-right) {
  color: #8998b5 !important;
}
</style>
