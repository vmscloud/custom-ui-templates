<template>
  <ExtendFlexGrid
    :key="summaryType"
    name="onTimeReplanSummary"
    :itemsSource="summaryDataSource"
    height="100%"
    :isReadOnly="true"
    allowSorting="None"
    :initialized="onInitialized"
    :selectionChanged="onSelectionChanged"
    :formatItem="formatItem"
    :loading="loading"
    :use-tool-box="false"
    class="rtf-report-sub1-grid"
  >
    <WjFlexGridColumnGroup
      binding="due"
      :header="groupingColumnHeader"
      aggregate="Cnt"
      :width="120"
      align="center"
      dataType="String"
    />
    <WjFlexGridColumnGroup
      binding="group_name"
      header="그룹"
      :width="80"
      :visible="true"
      align="center"
    />
    <WjFlexGridColumnGroup :header="t('text-isu_rtf_rate')" align="center">
      <WjFlexGridColumnGroup
        binding="ratio_early"
        :header="t('text-isu_early')"
        align="right"
        :width="90"
        aggregate="Avg"
      />
      <WjFlexGridColumnGroup
        binding="ratio_ontime"
        :header="t('text-isu_ontime')"
        align="right"
        :width="90"
        aggregate="Avg"
      />
      <WjFlexGridColumnGroup
        binding="ratio_late"
        :header="t('text-isu_late')"
        align="right"
        :width="90"
        aggregate="Avg"
      />
      <WjFlexGridColumnGroup
        binding="ratio_short"
        :header="t('text-isu_short')"
        align="right"
        :width="90"
        aggregate="Avg"
      />
    </WjFlexGridColumnGroup>
    <WjFlexGridColumnGroup
      binding="ratio_rtf"
      :header="t('text-isu_otd_expected_rate')"
      align="right"
      :width="110"
      aggregate="Avg"
    />
  </ExtendFlexGrid>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumnGroup } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { CollectionView } from "@vmscloud/moz-wijmo-grid/wijmo";
import {
  type FlexGrid,
  GroupRow,
  CellRange,
} from "@vmscloud/moz-wijmo-grid/wijmo.grid";
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

const summaryGrid = ref<FlexGrid>();
const summaryExtendGrid = ref<ExtendGrid | null>(null);
const summaryDataSource = ref<CollectionView>(new CollectionView([]));
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

// === Grid Initialization ===

const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  summaryGrid.value = flexGrid;
  summaryExtendGrid.value = _extendGrid;

  const extraRow = new GroupRow();
  summaryGrid.value.columnFooters.rows.push(extraRow);
};

// === Data Processing ===

async function processData(rawData: ReplanRtfSummary[]) {
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

  summaryDataSource.value = new CollectionView(dataWithGroupName, {
    groupDescriptions: ["group_name"],
  });

  isTempGroupColumnTitle.value = false;

  await nextTick();
  if (summaryGrid.value) {
    summaryGrid.value.collapseGroupsToLevel(0);

    // Hide group_name column after grouping
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

// === FormatItem ===

const formatItem = (s: FlexGrid, e: any) => {
  const binding = e.getColumn()?.binding;

  // ----- Column Header: ratio_rtf sub-text -----
  if (e.panel === s.columnHeaders && binding === "ratio_rtf") {
    const headerText = e.cell.textContent || e.cell.innerText;
    e.cell.innerHTML = "";

    const headerDiv = document.createElement("div");
    headerDiv.style.display = "flex";
    headerDiv.style.flexDirection = "column";
    headerDiv.style.alignItems = "center";
    headerDiv.style.justifyContent = "center";
    headerDiv.style.height = "100%";

    const mainHeader = document.createElement("div");
    mainHeader.textContent = headerText;
    mainHeader.classList.add("rtf-ratio-main-header");

    const subHeader = document.createElement("div");
    subHeader.textContent = t('text-isu_early_ontime_late');
    subHeader.classList.add("rtf-ratio-sub-header");

    headerDiv.appendChild(mainHeader);
    headerDiv.appendChild(subHeader);
    e.cell.appendChild(headerDiv);
  }

  // ----- TOTAL Footer (cellType === 5) -----
  if (e.panel.cellType === 5) {
    e.cell.classList.add("summary-footer");
    e.cell.addEventListener("mousedown", () => {
      if (summaryTotalRowData.value) {
        emit("row-selected", { ...summaryTotalRowData.value, due: "[TOTAL]" });
      }
      summaryGrid.value?.select(new CellRange(-1, -1), false);
    });

    const totalValue = summaryTotalRowData.value?.[binding];

    if (
      binding === "ratio_rtf" ||
      binding === "ratio_early" ||
      binding === "ratio_ontime" ||
      binding === "ratio_late" ||
      binding === "ratio_short"
    ) {
      e.cell.innerHTML = `${formatNumber(Number(totalValue ?? 0))}%`;
    } else if (binding === "due") {
      e.cell.innerText = "[TOTAL]";
    }
    return;
  }

  // ----- Group Row -----
  if (e.panel !== s.columnHeaders && s.rows[e.row] instanceof GroupRow) {
    const row = s.rows[e.row];
    if (row instanceof GroupRow && !row.isCollapsed) {
      e.cell.classList.add("rtf-report-group-separator");
    }

    // First visible column: keep expand button + group name
    const visibleColumns = e.panel.columns.filter(
      (column: any) => column.visible,
    );
    const visibleColumnIndex = visibleColumns.indexOf(
      e.panel.columns[e.col],
    );

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

    const value = Number(e.cell.innerText) || 0;

    if (
      binding === "ratio_rtf" ||
      binding === "ratio_early" ||
      binding === "ratio_ontime" ||
      binding === "ratio_late" ||
      binding === "ratio_short"
    ) {
      e.cell.innerHTML = `${formatNumber(value)}%`;
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
    case "demandQty":
    case "onTimeQty":
    case "shortQty":
    case "earlyQty":
    case "lateQty":
      if (typeof item[binding] === "number")
        cell.textContent = item[binding].toLocaleString();
      break;
    case "ratio_early":
    case "ratio_ontime":
    case "ratio_late":
    case "ratio_short":
    case "ratio_rtf":
      if (typeof item[binding] === "number")
        cell.textContent = `${formatNumber(Number(item[binding] ?? 0))}%`;
      break;
    default:
      break;
  }
};
</script>

<style lang="scss">
.rtf-report-sub1-grid {
  .wj-group {
    font-weight: 500;
  }

  .wj-flexgrid .wj-cell .wj-btn.wj-btn-glyph {
    width: 20px;
    height: 12px;
  }

  .wj-glyph-right,
  .wj-glyph-down-right {
    color: #8998b5 !important;
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
</style>
