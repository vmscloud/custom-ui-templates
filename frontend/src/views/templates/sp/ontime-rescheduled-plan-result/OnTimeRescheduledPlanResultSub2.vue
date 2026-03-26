<template>
  <div class="rtf-report-sub2-wrapper">
    <!-- Detail Grid -->
    <ExtendFlexGrid
      name="onTimeReplanDetail"
      :itemsSource="data"
      height="100%"
      :isReadOnly="true"
      allowSorting="None"
      :initialized="onInitialized"
      :selectionChanged="onSelectionChanged"
      :formatItem="onFormatItem"
      :loading="loading"
      :use-tool-box="false"
      class="rtf-report-sub2"
      :setContextMenuProps="{
        useFlexGridSetting: true,
        useFilter: true,
        useExportExcel: true,
      }"
    >
      <WjFlexGridColumnGroup binding="itemID" :header="t('text-item_id')" dataType="String" />
      <WjFlexGridColumnGroup binding="demandID" :header="t('text-isu_mo_id')" :width="80" align="left" />
      <WjFlexGridColumnGroup binding="showDetailCol" :header="t('text-simple_short_reason')" :width="80" />
      <WjFlexGridColumnGroup binding="custID" :header="t('text-cust_name')" :width="150" />
      <WjFlexGridColumnGroup
        :width="110"
        binding="ratio_rtf"
        :header="t('text-isu_otd_expected_rate')"
        dataType="Number"
        align="right"
      />
      <WjFlexGridColumnGroup
        :width="110"
        binding="rtfQty"
        :header="t('text-isu_otd_expected_qty')"
        dataType="Number"
        align="right"
      />
      <WjFlexGridColumnGroup :header="t('text-isu_rtf_rate')" align="center">
        <WjFlexGridColumnGroup
          :width="80"
          binding="ratio_early"
          :header="t('text-isu_early')"
          dataType="Number"
          align="right"
        />
        <WjFlexGridColumnGroup
          :width="80"
          binding="ratio_ontime"
          :header="t('text-isu_ontime')"
          dataType="Number"
          align="right"
        />
        <WjFlexGridColumnGroup
          :width="80"
          binding="ratio_late"
          :header="t('text-isu_late')"
          dataType="Number"
          align="right"
        />
        <WjFlexGridColumnGroup
          :width="80"
          binding="ratio_short"
          :header="t('text-isu_short')"
          dataType="Number"
          align="right"
        />
      </WjFlexGridColumnGroup>
      <WjFlexGridColumnGroup :header="t('text-isu_prod_qty')" align="center">
        <WjFlexGridColumnGroup
          :width="80"
          binding="earlyQty"
          :header="t('text-isu_early')"
          dataType="Number"
          align="right"
        />
        <WjFlexGridColumnGroup
          :width="80"
          binding="onTimeQty"
          :header="t('text-isu_ontime')"
          dataType="Number"
          align="right"
        />
        <WjFlexGridColumnGroup
          :width="80"
          binding="lateQty"
          :header="t('text-isu_late')"
          dataType="Number"
          align="right"
        />
        <WjFlexGridColumnGroup
          :width="80"
          binding="shortQty"
          :header="t('text-isu_short')"
          dataType="Number"
          align="right"
        />
      </WjFlexGridColumnGroup>
    </ExtendFlexGrid>

    <!-- Short Detail Popup -->
    <Popup
      :width="700"
      :height="500"
      v-model:visible="shortPopupVisible"
      :title="t('text-short-reason-detail-view')"
      preset="close"
      :onCancel="() => (shortPopupVisible = false)"
    >
      <ExtendFlexGrid
        name="onTimeReplanShortDetail"
        :itemsSource="shortData"
        height="100%"
        :isReadOnly="true"
        allowSorting="None"
        :use-tool-box="false"
      >
        <WjFlexGridColumnGroup binding="short_type" :header="t('text-short_type')" :width="100" align="center" />
        <WjFlexGridColumnGroup binding="short_category" :header="t('text-short_category')" :width="100" />
        <WjFlexGridColumnGroup binding="short_reason" :header="t('text-short_reason')" :width="150" />
        <WjFlexGridColumnGroup binding="short_qty" :header="t('text-short_qty')" dataType="Number" :width="90" align="right" format="n0" />
        <WjFlexGridColumnGroup binding="qty_uom" :header="t('text-qty_uom')" :width="80" :visible="false" />
      </ExtendFlexGrid>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumnGroup } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { type FlexGrid, CellRange } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { Popup } from "@vmscloud/moz-ui-components";
import type { ReplanRtfDetail, ShortData } from "./onTimeRescheduledPlanResult";

const { t } = useTranslation();

// === Props & Emits ===

interface Props {
  data: ReplanRtfDetail[];
  loading: boolean;
  planVer: string;
  uomType: string;
  shortData: ShortData[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "demand-selected", demandID: string): void;
  (e: "load-short", demandID: string): void;
}>();

// === Local State ===

const grid = ref<FlexGrid | null>(null);
const extendGrid = ref<ExtendGrid | null>(null);
const shortPopupVisible = ref(false);

// === Grid Initialization ===

const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
  extendGrid.value = _extendGrid;
};

// Auto-select first row when data changes
watch(
  () => props.data,
  (newData) => {
    if (newData && newData.length > 0 && grid.value) {
      setTimeout(() => {
        if (grid.value) {
          grid.value.select(new CellRange(0, 0, 0, 0), true);
        }
      }, 100);
    }
  },
);

// === Selection Changed ===

const onSelectionChanged = (s: FlexGrid, e: any) => {
  const { row, col } = s.selection;
  if (row < 0 || col < 0) return;

  const dataItem = e.getRow()?.dataItem;
  if (dataItem?.demandID) {
    emit("demand-selected", dataItem.demandID);
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

const onFormatItem = (s: FlexGrid, e: any) => {
  // Column header: ratio_rtf / rtfQty sub-text
  if (e.panel === s.columnHeaders) {
    const col = e.getColumn();
    if (col?.binding === "ratio_rtf" || col?.binding === "rtfQty") {
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
      subHeader.textContent = t("text-isu_early_ontime_late");
      subHeader.classList.add("rtf-ratio-sub-header");

      headerDiv.appendChild(mainHeader);
      headerDiv.appendChild(subHeader);
      e.cell.appendChild(headerDiv);
    }
  }

  // Data cells only
  if (e.panel !== s.cells) return;

  const item = e.getRow()?.dataItem;
  if (!item) return;

  const binding = e.getColumn()?.binding;
  const cell =
    e.cell.querySelector("span") != null
      ? e.cell.querySelector("span")
      : e.cell;

  if (!cell) return;

  switch (binding) {
    case "rtfQty":
    case "demandQty":
    case "onTimeQty":
    case "shortQty":
    case "lateQty":
    case "earlyQty":
      if (typeof item[binding] === "number")
        cell.textContent = item[binding].toLocaleString();
      break;

    case "ratio_rtf":
    case "ratio_ontime":
    case "ratio_late":
    case "ratio_early":
    case "ratio_short":
      if (typeof item[binding] === "number")
        cell.textContent = `${formatNumber(Number(item[binding] ?? 0))}%`;
      break;

    case "showDetailCol":
      cell.textContent = t('text-view_detail');
      cell.style.cursor = "pointer";
      cell.style.color = "#4568e0";
      cell.style.textDecoration = "underline";
      cell.addEventListener("click", () => {
        emit("load-short", item.demandID);
        shortPopupVisible.value = true;
      });
      break;

    default:
      break;
  }

  // Short highlighting: red background if rtf_ratio < 100
  if (item.ratio_rtf < 100) {
    e.cell.classList.add("ratio-short");
  }
  // Late highlighting: orange if fully produced but late
  if (item.ratio_rtf === 100 && item.ratio_late > 0) {
    e.cell.classList.add("ratio-late");
  }

  // Short font color for ratio_rtf
  if (binding === "ratio_rtf" && item.ratio_rtf < 100) {
    e.cell.classList.add("ratio-short-font");
  }
};
</script>

<style lang="scss">
.rtf-report-sub2-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.rtf-report-sub2 {
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

// Row coloring for short/late
.rtf-report-sub2 {
  .wj-cells .wj-row {
    .wj-cell.ratio-short {
      background-color: #f6d5d5 !important;

      &.wj-state-multi-selected,
      &.wj-state-active {
        background-color: #d4cde8 !important;
      }
    }

    .wj-cell.ratio-late {
      background-color: #fde6c8 !important;

      &.wj-state-multi-selected,
      &.wj-state-active {
        background-color: #d4cde8 !important;
      }
    }

    &:nth-child(2n) {
      .wj-cell.ratio-short {
        background-color: #f1d0d4 !important;
      }
      .wj-cell.ratio-late {
        background-color: #f8e1c7 !important;
      }
    }

    &:hover {
      .wj-cell.ratio-short:not(.wj-header) {
        background-color: #d4cde8 !important;
      }
      .wj-cell.ratio-late:not(.wj-header) {
        background-color: #d4cde8 !important;
      }
    }
  }

  .ratio-short-font span {
    color: #dc5a5a !important;
  }
}
</style>
