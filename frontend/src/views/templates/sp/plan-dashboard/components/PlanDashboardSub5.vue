<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <span class="panel-title">
          {{ t('text-plan_dashboard_isu-oper_group_utilization_report') }}
          <button class="link-btn" @click="openLinkNewTab({ path: '/sp/LoadFactorByOperGroup', query: { planVer: planVer || '' } }, true)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5 1h8v8M13 1L6 8" stroke="#8998b5" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </span>
        <span class="unit-label">(%)</span>
      </div>
      <div class="kpi-section">
        <span class="kpi-value">{{ avgUtilization }}%</span>
        <span class="kpi-sub">({{ t('text-average_load_factor') }})</span>
      </div>
    </div>
    <div class="container-body-wrapper">
      <v-chart v-if="hasData" class="chart" :option="chartOption" autoresize />
      <div v-else class="no-data">{{ t('msg-data_empty') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useTranslation } from "i18next-vue";
import VChart from "vue-echarts";
import { use } from "@vmscloud/moz-ui-chart/echarts/core";
import { CanvasRenderer } from "@vmscloud/moz-ui-chart/echarts/renderers";
import { BarChart, LineChart } from "@vmscloud/moz-ui-chart/echarts/charts";
import {
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
  DataZoomComponent,
} from "@vmscloud/moz-ui-chart/echarts/components";
import type { usePlanDashboard } from "../planDashboard";
import { useHostPlanCycle } from "@/composables/useHostStores";

const { t } = useTranslation();

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
  DataZoomComponent,
]);

type PlanDashboardContext = ReturnType<typeof usePlanDashboard>;
const planDashboard = inject<PlanDashboardContext>("planDashboard")!;
const { dashboardData } = planDashboard;
const openLinkNewTab = inject<(route: any, force?: boolean) => void>('openLinkNewTab', () => {});
const { planVer } = useHostPlanCycle();

const hasData = computed(() => {
  return (dashboardData.value?.operGroupCapa?.length ?? 0) > 0;
});

/** Group by oper_group_id and average utilization across time_keys */
const groupedData = computed(() => {
  const capaData = dashboardData.value?.operGroupCapa ?? [];
  const groupMap = new Map<string, number[]>();

  for (const row of capaData) {
    const id = (row.oper_group_id ?? row.operGroupId ?? "") as string;
    const util = Number(row.utilization ?? row.util_rate ?? 0);
    if (!groupMap.has(id)) {
      groupMap.set(id, []);
    }
    groupMap.get(id)!.push(util);
  }

  const categories: string[] = [];
  const utilValues: number[] = [];

  for (const [id, values] of groupMap) {
    categories.push(id);
    const avg = values.reduce((sum, v) => sum + v, 0) / values.length;
    utilValues.push(avg);
  }

  return { categories, utilValues };
});

const avgUtilization = computed(() => {
  const { utilValues } = groupedData.value;
  if (utilValues.length === 0) return "0.0";
  const avg = utilValues.reduce((sum, v) => sum + v, 0) / utilValues.length;
  return avg.toFixed(1);
});

/** Detect base_line value from data if present */
const baseLineValue = computed(() => {
  const capaData = dashboardData.value?.operGroupCapa ?? [];
  for (const row of capaData) {
    if (row.base_line != null || row.baseLine != null) {
      return Number(row.base_line ?? row.baseLine);
    }
  }
  return null;
});

const chartOption = computed(() => {
  const { categories, utilValues } = groupedData.value;
  const blValue = baseLineValue.value;

  const series: any[] = [
    {
      name: t('text-average_load_factor'),
      type: "bar" as const,
      barMaxWidth: 80,
      barCategoryGap: "40%",
      data: utilValues.map((val) => ({
        value: val,
        itemStyle: {
          color: "#618FF97A",
          borderRadius: [6, 6, 0, 0],
        },
        label: {
          show: true,
          position: "top" as const,
          fontSize: 11,
          formatter: `${val.toFixed(1)}%`,
          fontWeight: val >= 100 ? ("bold" as const) : ("normal" as const),
          color: val >= 100 ? "#4568E0" : "#858e9e",
        },
      })),
    },
  ];

  // Base line series if value exists
  if (blValue != null) {
    series.push({
      type: "line" as const,
      name: "Base Line",
      data: categories.map(() => blValue),
      showSymbol: false,
      lineStyle: { color: "#4568E0", width: 1, type: "solid" as const },
      z: 100,
      animation: false,
    });
  }

  return {
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "shadow" as const },
      appendTo: () => document.body,
      confine: false,
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.name}<br/>${t('text-average_load_factor')}: ${p.value.toFixed(1)}%`;
      },
    },
    grid: {
      top: 60,
      bottom: 35,
      left: 30,
      right: 40,
      containLabel: true,
    },
    xAxis: {
      type: "category" as const,
      data: categories,
      axisLabel: {
        color: "#96A5BE",
        interval: 0,
        overflow: "truncate" as const,
        lineHeight: 16,
      },
    },
    yAxis: {
      type: "value" as const,
      min: 0,
      axisLabel: {
        formatter: "{value}%",
        color: (value: number) => (value === 100 ? "#4568E0" : "#96A5BE"),
      },
      splitLine: {
        lineStyle: { color: "#eeeeee" },
      },
    },
    series,
    dataZoom: [
      {
        type: "slider" as const,
        bottom: 20,
        height: 10,
        showDetail: false,
      },
      {
        type: "inside" as const,
        zoomOnMouseWheel: false,
        moveOnMouseWheel: true,
      },
    ],
  };
});
</script>

<style scoped lang="scss">
.container {
  height: 100%;
  width: 100%;
  border: 1px solid #bbc6d9;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.container-header-wrapper {
  min-height: 92px;
  background-color: #f8f8fd;
  border-bottom: 1px solid #bbc6d9;
  padding: 12px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title {
  font-size: 1rem;
  font-weight: 500;
  color: #565f6e;
}

.link-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-left: 4px;
  vertical-align: middle;
  &:hover svg path { stroke: #4568e0; }
}

.unit-label {
  font-size: 12px;
  font-weight: 400;
  color: #939aac;
}

.kpi-section {
  margin-top: 4px;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.kpi-sub {
  font-size: 12px;
  font-weight: 500;
  color: #6a7184;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 34px;
  font-weight: 700;
  color: #28364e;
  line-height: 2.5rem;
  position: relative;
  z-index: 2;
  display: inline-block;
  width: fit-content;

  &::after {
    display: block;
    position: absolute;
    content: "";
    left: 0;
    bottom: 3px;
    width: 100%;
    height: 10px;
    background-color: #4568e0;
    opacity: 0.3;
    z-index: -1;
  }
}

.container-body-wrapper {
  flex: 1;
  min-height: 0;
  padding: 20px;
  overflow: auto;
}

.chart {
  width: 100%;
  height: 100%;
}

.no-data {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #939aac;
  font-size: 13px;
  height: 100%;
}
</style>
