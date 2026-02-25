<template>
  <div class="grid-chart-group-container">
    <!-- Group Header -->
    <div
      :class="['group-header', { 'group-header-close': !isOpen }]"
      @dblclick="toggleOpen"
    >
      <div class="group-name">
        <div class="group-label">
          <span class="group-title"
            >Demand Distribution by {{ displayName }}</span
          >
          <span v-if="unit" class="group-unit">({{ unit }})</span>
        </div>
      </div>
      <div class="icon-wrapper" @click="toggleOpen">
        <span v-if="isOpen">&#9650;</span>
        <span v-else>&#9660;</span>
      </div>
    </div>

    <!-- Group Body -->
    <div v-show="isOpen" class="group-body">
      <!-- Left Pane: Pivot Grid -->
      <div class="pane grid-pane">
        <ExtendPivotGrid
          ref="extendPivotGridRef"
          :emptyState="{ isLoading: isLoading }"
          :name="`demandDistribution_${displayName}_${idx + 1}`"
          height="100%"
          :itemsSource="data"
          :engine-option="{
            fields: fields,
            rowFields: [displayName],
            columnFields: columnFieldNames,
            valueFields: valueFieldNames,
            showRowTotals: dataState.showRowTotals,
            showColumnTotals: dataState.showColumnTotals,
            showZeros: dataState.showZeros,
            totalsBeforeData: dataState.totalsBeforeData,
          }"
          :useContextMenu="false"
          :initialized="onInitialized"
          :formatItem="formatItem"
          :use-pivot-chart="false"
          :use-tool-box="false"
          :loading="isLoading"
          :use-extend-footer="true"
          :on-filter-restored="onFilterRestored"
        />
      </div>

      <!-- Right Pane: Chart -->
      <div class="pane chart-pane">
        <div class="chart-wrapper">
          <EChart
            :id="`demandDistribution_chart_${column}_${idx}`"
            :items-source="filteredData"
            v-model:view-def="masterViewDef"
            v-model:filter-def="masterFilterDef"
            v-model:chart-def="masterChartDef"
            :chart-def-template="chartDefTemplate"
            :use-tool-box="true"
            :use-chart-setting="false"
            :is-fetching="isLoading"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, toRefs, watch } from "vue";
import { ExtendPivotGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { Aggregate, DataType } from "@vmscloud/moz-wijmo-grid/wijmo";
import { CellType, type FormatItemEventArgs } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { type PivotGrid, ShowTotals } from "@vmscloud/moz-wijmo-grid/wijmo.olap";
import {
  EChart,
  type ViewDef,
  type ChartField,
} from "@vmscloud/moz-ui-chart";
import type { DemandDistributionData } from "./demandDistribution";

// Total marker constants (unicode ordering for pivot grid sorting)
const TOTAL_FOR_GRID = "🚀-text-total";
// Chart total marker (zero-width space prefix prevents i18n auto-conversion)
const TOTAL_FOR_CHART = "\u200BTotal";

// PivotGrid filterModule type
type PivotFilterModule = {
  setGrid: (grid: PivotGrid, immediate?: boolean) => void;
  applyFilter: (filters: any[]) => void;
  setFilter: (filters: any[], immediate?: boolean) => void;
  getFilter: () => any[];
};

// Props
interface Props {
  isLoading: boolean;
  column: string;
  displayName: string;
  idx: number;
  data: DemandDistributionData[];
  unit: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  unit: null,
});

const { isLoading, displayName, idx, data, column, unit } = toRefs(props);

// Open state
const isOpen = ref(true);

function toggleOpen() {
  isOpen.value = !isOpen.value;
}

// Filtered data for chart (exclude total rows)
const filteredData = computed(() =>
  data.value.filter((d) => d.due_date !== "🚀-text-demand-total"),
);

// ===== Pivot Grid Configuration =====

interface FieldType {
  binding: string;
  header: string;
  dataType: DataType;
  aggregate?: Aggregate;
  align: "left" | "center" | "right";
  format?: string;
  width?: number;
}

const fields = computed<FieldType[]>(() => {
  const defaultFields: FieldType[] = [
    {
      binding: "due_date",
      header: "Due Date",
      dataType: DataType.String,
      align: "right",
      width: 76,
    },
    {
      binding: "item_cnt",
      header: "Item Count",
      dataType: DataType.Number,
      align: "right",
      aggregate: Aggregate.Sum,
    },
    {
      binding: "qty",
      header: "Demand Qty",
      dataType: DataType.Number,
      align: "right",
      width: 76,
      aggregate: Aggregate.Sum,
    },
  ];

  defaultFields.push({
    binding: column.value,
    header: displayName.value,
    align: "left",
    dataType: DataType.String,
  });

  return defaultFields;
});

// Engine option field name arrays (must match field headers exactly)
const columnFieldNames = ["Due Date"];
const valueFieldNames = ["Demand Qty"];

const dataState = reactive<{
  showRowTotals: ShowTotals;
  showColumnTotals: ShowTotals;
  showZeros: boolean;
  totalsBeforeData: boolean;
}>({
  showRowTotals: ShowTotals.None,
  showColumnTotals: ShowTotals.None,
  showZeros: true,
  totalsBeforeData: false,
});

// Pivot grid refs
const extendGrid = ref<ExtendGrid>();
const extendPivot = ref<PivotGrid>();
const pivotFilterModule = ref<PivotFilterModule | null>(null);
const extendPivotGridRef = ref<InstanceType<typeof ExtendPivotGrid> | null>(
  null,
);

const onInitialized = (pivotGrid: PivotGrid, _extendGrid: ExtendGrid) => {
  extendPivot.value = pivotGrid;
  extendGrid.value = _extendGrid;

  if (extendPivotGridRef.value?.filterModule) {
    pivotFilterModule.value = extendPivotGridRef.value.filterModule;
    pivotFilterModule.value.setGrid(pivotGrid);
  }
};

const formatItem = (s: PivotGrid, e: FormatItemEventArgs) => {
  let col = 0;
  const row = s.rows.length - 1;
  if (e.panel.cellType === CellType.RowHeader) {
    if (e.cell.innerText === TOTAL_FOR_GRID) {
      e.cell.innerText = "Total";
      col = e.col;
    }
  } else if (col <= e.col && row === e.row) {
    e.cell.classList.add("wj-aggregate");
  }

  const lastCol = s.columns.length - 1;
  if (e.panel.cellType === CellType.ColumnHeader) {
    if (e.cell.innerText === "🚀-text-demand-total") {
      e.cell.innerText = "Total";
    }
  } else if (lastCol === e.col) {
    e.cell.classList.add("wj-aggregate");
  }
};

/**
 * Layout restore: convert grid filters to chart filters
 */
const onFilterRestored = (filters: any[]) => {
  masterFilterDef.value = filters.map((filter: any, index: number) => ({
    sequence: filter.sequence ?? index,
    header: filter.header || "",
    binding: filter.binding || "",
    logical: filter.logical || "AND",
    comparison: filter.comparison || "%",
    comparisonObj: {
      symbol: filter.comparison || "%",
      label: filter.comparison || "%",
    },
    type: filter.type ?? DataType.String,
    variable: filter.variable,
  }));
};

// ===== Chart Configuration =====

const masterChartDef = ref<Record<string, any>>({
  series: [{ name: "Demand Qty", mozType: "bar" }],
});

/**
 * Chart definition template: Total series → line chart + dual Y-axis
 * Replaces 🚀-text-total marker with "Total" display name
 */
const chartDefTemplate = computed(() => {
  if (!masterChartDef.value?.series || !masterChartDef.value.legend) return {};

  // Transform legend: rename total marker → "Total", move to end
  const legendData = masterChartDef.value.legend[0]?.getData?.();
  const newLegendData = legendData
    ?.map((l: string) => (l === TOTAL_FOR_GRID ? TOTAL_FOR_CHART : l))
    .sort((a: string, b: string) => {
      if (a === TOTAL_FOR_CHART && b !== TOTAL_FOR_CHART) return 1;
      if (a !== TOTAL_FOR_CHART && b === TOTAL_FOR_CHART) return -1;
      return 0;
    });

  // Transform series: Total → line chart on secondary Y-axis
  const newSeries = (masterChartDef.value.series as any[]).map((s) => {
    if (s.name === TOTAL_FOR_GRID) {
      return {
        ...s,
        name: TOTAL_FOR_CHART,
        yAxisIndex: 1,
        type: "line",
        mozType: "line",
        showInLegend: false,
        data: s.getData?.() ?? s.data,
      };
    }
    return {
      ...s,
      yAxisIndex: 0,
      showInLegend: false,
    };
  });

  // Dual Y-axis: left for bar values, right for total line
  const yAxisData = [
    { type: "value", position: "left", name: "Value", min: 0 },
    { type: "value", position: "right", name: "Total" },
  ];

  return {
    series: newSeries,
    yAxis: yAxisData,
    legend: newLegendData
      ? [{ id: "default", data: newLegendData }]
      : undefined,
  };
});

const masterViewDef = computed<ViewDef>(() => {
  const columnFieldsDef = [
    { binding: "due_date", header: "Due Date", dataType: DataType.String },
  ] as ChartField[];

  const rowFieldsDef = [
    {
      binding: column.value,
      header: displayName.value,
      dataType: DataType.String,
    },
  ] as ChartField[];

  const valueFieldsDef = [
    { binding: "qty", header: "Demand Qty", dataType: DataType.Number },
  ] as ChartField[];

  const masterFields = [...columnFieldsDef, ...rowFieldsDef, ...valueFieldsDef];

  return {
    fields: masterFields,
    columnFields: columnFieldsDef,
    rowFields: rowFieldsDef,
    valueFields: valueFieldsDef,
  };
});

const masterFilterDef = ref<any[]>([]);

/**
 * Sync chart filters back to pivot grid
 */
watch(
  masterFilterDef,
  (newFilters) => {
    if (!pivotFilterModule.value || !extendPivot.value) return;

    const pivotFilters = newFilters.map((filter: any, filterIdx: number) => ({
      sequence: filter.sequence ?? filterIdx,
      header: filter.header || "",
      binding: filter.binding || "",
      logical: filter.logical || "AND",
      comparison: filter.comparison || (filter.comparisonObj?.symbol ?? "%"),
      type: filter.type ?? DataType.String,
      variable: filter.variable,
    }));

    const validFilters = pivotFilters.filter(
      (f: any) =>
        f.variable != null || f.comparison === "∅" || f.comparison === "●",
    );

    pivotFilterModule.value.setFilter(validFilters, true);
  },
  { deep: true },
);
</script>

<style scoped lang="scss">
.grid-chart-group-container {
  border: 1px solid var(--color-grid-border, #e5e7eb);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary, #ffffff);

  .group-header {
    display: flex;
    width: 100%;
    justify-content: space-between;
    align-items: center;
    padding: 0 14px;
    height: 44px;
    border-radius: 8px 8px 0 0;
    user-select: none;
    background: var(--color-bg-100, #f9fafb);
    border-bottom: 1px solid var(--color-grid-border, #e5e7eb);
    cursor: pointer;

    &.group-header-close {
      border-radius: 8px;
      border-bottom: none;
    }

    .group-name {
      font-size: 16px;
      font-weight: 500;
      color: var(--color-text-500, #1f2937);
      display: flex;
      align-items: center;

      .group-label {
        display: flex;
        align-items: center;
        gap: 4px;

        .group-title {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .group-unit {
          color: var(--color-text-350, #6b7280);
          font-size: 12px;
          font-weight: 400;
        }
      }
    }

    .icon-wrapper {
      width: 24px;
      height: 24px;
      background-color: var(--color-bg-400, #e5e7eb);
      border-radius: 50%;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      font-size: 10px;
      color: var(--color-text-secondary, #6b7280);

      &:hover {
        background-color: var(--color-bg-hover, #d1d5db);
      }
    }
  }

  .group-body {
    display: flex;
    gap: 10px;
    padding: 10px;
    height: 500px;
    min-height: 400px;
    max-height: 678px;

    .pane {
      flex: 1;
      min-width: 0;
      height: 100%;
      overflow: hidden;
    }

    .grid-pane {
      max-width: 50%;
    }

    .chart-pane {
      max-width: 50%;
      display: flex;
    }

    .chart-wrapper {
      width: 100%;
      height: 100%;
    }
  }
}
</style>
