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
        <MozGrid
          :name="`demandDistribution_${displayName}_${idx + 1}`"
          height="100%"
          :coreConfig="coreConfig"
          :sourceFields="sourceFields"
          :useContextMenu="false"
          :useChart="false"
          :useToolBox="false"
          :useExtendFooter="true"
          :loading="isLoading"
          @ready="onGridReady"
          @filter:changed="onGridFilterChanged"
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
import { ref, computed, toRefs, watch } from "vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type {
  GridChrome,
  MozGridCoreProps,
  PureSheet,
  FilterState,
  IFilterDef,
  ComparisonOperator,
} from "@vmscloud/moz-ui-grid-vue";
import {
  EChart,
  DataType,
  type ViewDef,
  type ChartField,
} from "@vmscloud/moz-ui-chart-vue";
import type { DemandDistributionData } from "./demandDistribution";

// Total marker constants (server sends these values for total rows/columns)
const TOTAL_FOR_GRID = "🚀-text-total";
const DEMAND_TOTAL = "🚀-text-demand-total";
// Grid total label (pivot field formulas map the markers to this label)
const TOTAL_LABEL = "Total";
// Chart total marker (zero-width space prefix prevents i18n auto-conversion)
const TOTAL_FOR_CHART = "\u200BTotal";
// Total row/column cell style
const TOTAL_CELL_STYLE =
  "background-color: var(--color-grid-point); font-weight: bold;";

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
  data.value.filter((d) => d.due_date !== DEMAND_TOTAL),
);

// ===== Pivot Grid Configuration =====

// Pivot field catalog (candidates in the pivot field panel)
const sourceFields = computed(() => [
  { field: "due_date", header: "Due Date", dataType: "string" as const, width: 76 },
  { field: "item_cnt", header: "Item Count", dataType: "number" as const, aggregate: "sum" as const },
  { field: "qty", header: "Demand Qty", dataType: "number" as const, width: 76, aggregate: "sum" as const },
  { field: column.value, header: displayName.value, dataType: "string" as const },
]);

// Total row/column cells are highlighted
const totalCellAttributes = (params: {
  row: Record<string, unknown>;
  pivotValues?: unknown[];
}) =>
  params.row[column.value] === TOTAL_LABEL ||
  params.pivotValues?.[0] === TOTAL_LABEL
    ? { style: TOTAL_CELL_STYLE }
    : undefined;

const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "pivot",
  data: data.value,
  rowFields: [
    {
      field: column.value,
      header: displayName.value,
      dataType: "string",
      formula: (row: Record<string, unknown>) =>
        row[column.value] === TOTAL_FOR_GRID ? TOTAL_LABEL : row[column.value],
    },
  ],
  columnFields: [
    {
      field: "due_date",
      header: "Due Date",
      dataType: "string",
      width: 76,
      formula: (row: Record<string, unknown>) =>
        row.due_date === DEMAND_TOTAL ? TOTAL_LABEL : row.due_date,
    },
  ],
  valueFields: [
    {
      field: "qty",
      header: "Demand Qty",
      dataType: "number",
      width: 76,
      aggregate: "sum",
      cellAttributes: totalCellAttributes,
    },
  ],
  showRowGrandTotals: false,
  showColumnGrandTotals: false,
  showRowSubTotals: false,
  showColumnSubTotals: false,
  showZeros: true,
}));

// Total label always sorts last (other labels keep ascending order)
const totalLastSortKey = (value: unknown) =>
  value === TOTAL_LABEL ? "1" : `0${String(value ?? "")}`;

// Pivot grid chrome (filter controller)
const gridChrome = ref<GridChrome | null>(null);

const onGridReady = (grid: PureSheet, chrome: GridChrome) => {
  gridChrome.value = chrome;
  grid.sort([
    { id: column.value, direction: "asc", sequence: 1, sortKey: totalLastSortKey },
    { id: "due_date", direction: "asc", sequence: 2, sortKey: totalLastSortKey },
  ]);
  // Re-apply chart filters after grid (re)initialization
  lastSyncedFilterKey = filterKey([]);
  applyChartFiltersToGrid(masterFilterDef.value);
};

// ===== Grid <-> Chart filter sync =====

const MOZ_TO_COMPARISON: Record<string, ComparisonOperator> = {
  eq: "=",
  neq: "≠",
  contains: "%",
  notContains: "!%",
  isNull: "∅",
  isNotNull: "●",
  gt: ">",
  gte: "≥",
  lt: "<",
  lte: "≤",
};

// Filter identity key (skips echoes between grid and chart)
const filterKey = (
  filters: {
    binding: string;
    comparison: string;
    variable: unknown;
    logical?: string;
  }[],
) =>
  JSON.stringify(
    filters.map((f) => [
      f.binding,
      f.comparison,
      f.variable ?? null,
      (f.logical ?? "AND").toUpperCase(),
    ]),
  );

let lastSyncedFilterKey = filterKey([]);

/**
 * Grid filter change (layout restore, grid filter UI) -> chart filters
 */
const onGridFilterChanged = (payload: unknown) => {
  const { filters = [] } = (payload ?? {}) as { filters?: FilterState[] };
  const headerOf = (id: string) =>
    sourceFields.value.find((f) => f.field === id)?.header ?? id;

  // Value-list filters (in/notIn) have no chart comparison and are skipped
  const chartFilters = filters
    .filter((f) => MOZ_TO_COMPARISON[f.operator])
    .map((f, index) => {
      const comparison = MOZ_TO_COMPARISON[f.operator];
      return {
        sequence: f.sequence ?? index,
        header: headerOf(f.id),
        binding: f.id,
        logical: f.logical === "or" ? "OR" : "AND",
        comparison,
        comparisonObj: { symbol: comparison, label: comparison },
        type: DataType.String,
        variable: (f as { filterValue?: unknown }).filterValue,
      };
    });

  const key = filterKey(chartFilters);
  if (key === lastSyncedFilterKey) return;
  lastSyncedFilterKey = key;
  masterFilterDef.value = chartFilters;
};

/**
 * Chart filters -> pivot grid
 */
function applyChartFiltersToGrid(newFilters: any[]) {
  if (!gridChrome.value) return;

  const pivotFilters: IFilterDef[] = newFilters.map(
    (filter: any, filterIdx: number) => ({
      sequence: filter.sequence ?? filterIdx,
      header: filter.header || "",
      binding: filter.binding || "",
      logical: filter.logical || "AND",
      comparison: filter.comparison || (filter.comparisonObj?.symbol ?? "%"),
      type: "string",
      variable: filter.variable,
    }),
  );

  const validFilters = pivotFilters.filter(
    (f) => f.variable != null || f.comparison === "∅" || f.comparison === "●",
  );

  const key = filterKey(validFilters);
  if (key === lastSyncedFilterKey) return;
  lastSyncedFilterKey = key;
  gridChrome.value.filter.setFilter(validFilters);
}

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
watch(masterFilterDef, (newFilters) => applyChartFiltersToGrid(newFilters), {
  deep: true,
});
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
