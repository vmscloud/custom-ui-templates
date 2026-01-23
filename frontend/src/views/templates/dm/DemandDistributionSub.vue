<template>
  <div class="grid-chart-group-container">
    <!-- Group Header -->
    <div
      :class="['group-header', { 'group-header-close': !isOpen }]"
      @dblclick="toggleOpen"
    >
      <div class="group-name">
        <div class="group-label">
          <span class="group-title">Demand Distribution by {{ displayName }}</span>
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
      <!-- Left Pane: Grid -->
      <div class="pane grid-pane">
        <ExtendFlexGrid
          :name="`demandDistribution_${column}_${idx}`"
          :items-source="gridData"
          height="100%"
          :use-tool-box="false"
          :use-extend-footer="true"
          :is-read-only="true"
          :loading="isLoading"
          :initialized="onGridInitialized"
        >
          <WjFlexGridColumn
            binding="due_date"
            header="Due Date"
            :width="100"
            align="center"
          />
          <WjFlexGridColumn
            :binding="column"
            :header="displayName"
            :width="120"
          />
          <WjFlexGridColumn
            binding="qty"
            header="Demand Qty"
            :width="100"
            format="n0"
            align="right"
          />
          <WjFlexGridColumn
            binding="item_cnt"
            header="Item Count"
            :width="90"
            format="n0"
            align="right"
          />
        </ExtendFlexGrid>
      </div>

      <!-- Right Pane: Chart -->
      <div class="pane chart-pane">
        <div class="chart-wrapper">
          <EChart
            :id="`demandDistribution_chart_${column}_${idx}`"
            :items-source="chartData"
            v-model:view-def="viewDef"
            v-model:filter-def="filterDef"
            v-model:chart-def="chartDef"
            :on-initialized="onChartInitialized"
            :use-tool-box="true"
            :use-chart-setting="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, toRefs } from "vue";
import {
  ExtendFlexGrid,
  EChart,
  DataType,
  Aggregate,
  type ExtendGrid,
  type MozEChart,
  type ViewDef,
  type FilterDef,
  type ChartField,
} from "@vmscloud/moz-ui-components";
import { WjFlexGridColumn } from "@grapecity/wijmo.vue2.grid";
import type { FlexGrid } from "@grapecity/wijmo.grid";
import type { DemandDistributionData } from "./demandDistribution";

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

// Toggle open/close
function toggleOpen() {
  isOpen.value = !isOpen.value;
}

// Grid data - filter out total rows
const gridData = computed(() => {
  return data.value.filter(
    (d) =>
      d.due_date !== "🚀-text-demand-total" &&
      !String(d[column.value] ?? "").includes("🚀")
  );
});

// Chart data - same as grid data for now
const chartData = computed(() => {
  return gridData.value.map((d) => ({
    due_date: d.due_date,
    category: String(d[column.value] ?? "Unknown"),
    qty: d.qty ?? 0,
    item_cnt: d.item_cnt ?? 0,
  }));
});

// Chart ViewDef
const viewDef = ref<ViewDef>({
  fields: [
    { binding: "due_date", header: "Due Date", dataType: DataType.String },
    { binding: "category", header: "Category", dataType: DataType.String },
    { binding: "qty", header: "Demand Qty", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "item_cnt", header: "Item Count", dataType: DataType.Number, aggregate: Aggregate.Sum },
  ] as ChartField[],
  rowFields: [{ binding: "category", header: "Category", dataType: DataType.String }],
  columnFields: [{ binding: "due_date", header: "Due Date", dataType: DataType.String }],
  valueFields: [
    { binding: "qty", header: "Demand Qty", dataType: DataType.Number, aggregate: Aggregate.Sum },
  ],
});

// Chart FilterDef
const filterDef = ref<FilterDef[]>([]);

// Chart ChartDef
const chartDef = ref({});

// Chart initialization
function onChartInitialized(mozEChart: MozEChart) {
  mozEChart.category = "series";
  // mozEChart.type = props.showStack ? "bar" : "bar";
}

// Grid initialization
function onGridInitialized(flexGrid: FlexGrid, _extendGrid: ExtendGrid) {
  // Format total cells
  flexGrid.formatItem.addHandler((_s, e) => {
    if (e.panel === flexGrid.cells) {
      const item = flexGrid.rows[e.row]?.dataItem;
      if (item) {
        const colValue = item[column.value];
        if (colValue === "🚀-text-total") {
          e.cell.textContent = "Total";
          e.cell.classList.add("wj-aggregate");
        }
        if (item.due_date === "🚀-text-demand-total") {
          e.cell.textContent = e.cell.textContent === "🚀-text-demand-total" ? "Total" : e.cell.textContent;
          e.cell.classList.add("wj-aggregate");
        }
      }
    }
  });
}
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
    height: 450px;
    min-height: 400px;
    max-height: 550px;

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

    .chart-placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      color: var(--color-text-secondary, #9ca3af);
      font-size: 14px;
      background: var(--color-bg-secondary, #f9fafb);
    }
  }
}
</style>
