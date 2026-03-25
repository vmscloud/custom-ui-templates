<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <div class="panel-title">{{ t('text-plan_dashboard_isu-act_rtf_report') }}</div>
        <span class="unit-label">{{ qtyUom ? t('text-fgs_stock_report_qty_uom', { unit: qtyUom }) : '' }}</span>
      </div>
      <div class="kpi-section">
        <span class="kpi-value">{{ actualRtfRatio }}%</span>
        <span class="kpi-description">({{ t('text-plan_dashboard-rtf_ratio') }})</span>
      </div>
    </div>
    <div class="container-body-wrapper">
      <template v-if="hasData">
        <div class="chart-legend">
          <div
            class="legend-item"
            v-for="item in legendItems"
            :key="item.label"
          >
            <span class="legend-icon" :style="{ backgroundColor: item.color }">
              <icon-time :width="14" :height="14" :color="'white'" />
            </span>
            <span class="legend-title">{{ item.label }}</span>
          </div>
        </div>
        <v-chart class="chart" :option="chartOption" autoresize />
      </template>
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
import { BarChart } from "@vmscloud/moz-ui-chart/echarts/charts";
import {
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from "@vmscloud/moz-ui-chart/echarts/components";
import { normalizeRatios, round2, type usePlanDashboard } from "../planDashboard";
import IconTime from "../assets/IconTime.vue";

const { t } = useTranslation();

use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
]);

type PlanDashboardContext = ReturnType<typeof usePlanDashboard>;
const planDashboard = inject<PlanDashboardContext>("planDashboard")!;
const { dashboardData } = planDashboard;

const COLORS = {
  ontime: "#6daafa",
  early: "#aac7e8",
  late: "#feb34e",
  short: "#dc5a5a",
  upcoming: "#b6b7c1",
};

const actual = computed(() => dashboardData.value?.rtfSummary?.actual);
const frozen = computed(() => dashboardData.value?.rtfSummary?.frozen);

const hasData = computed(() => {
  return actual.value != null || frozen.value != null;
});

const qtyUom = computed(
  () => actual.value?.qtyUom ?? frozen.value?.qtyUom ?? "",
);

const actualRtfRatio = computed(() => {
  if (actual.value?.rtfRatio != null) {
    return actual.value.rtfRatio.toFixed(1);
  }
  return "0.0";
});

const legendItems = computed(() => [
  { label: t('text-plan_dashboard-on_time'), color: COLORS.ontime },
  { label: t('text-plan_dashboard-early'), color: COLORS.early },
  { label: t('text-plan_dashboard-late'), color: COLORS.late },
  { label: t('text-plan_dashboard-short'), color: COLORS.short },
  { label: t('text-plan_dashboard_isu-upcoming_ratio'), color: COLORS.upcoming },
]);

const chartOption = computed(() => {
  const a = actual.value;
  const f = frozen.value;

  // 소수점 2자리 반올림 + 총합 100% 보정
  const [fOntime, fEarly, fLate, fShort, fUpcoming] = normalizeRatios([
    f?.ontimeRatio ?? 0, f?.earlyRatio ?? 0, f?.lateRatio ?? 0, f?.shortRatio ?? 0, f?.upcomingRatio ?? 0,
  ]);
  const [aOntime, aEarly, aLate, aShort, aUpcoming] = normalizeRatios([
    a?.ontimeRatio ?? 0, a?.earlyRatio ?? 0, a?.lateRatio ?? 0, a?.shortRatio ?? 0, a?.upcomingRatio ?? 0,
  ]);

  const makeLabelFormatter = () => {
    return (p: any) => (p.value > 5 ? round2(p.value) + "%" : "");
  };

  // 각 bar(frozen / actual)별로 마지막 데이터가 있는 세그먼트에 오른쪽 borderRadius 적용
  const segmentsDef = [
    { name: t('text-plan_dashboard-on_time'), color: COLORS.ontime, frozen: fOntime, actual: aOntime },
    { name: t('text-plan_dashboard-early'), color: COLORS.early, frozen: fEarly, actual: aEarly },
    { name: t('text-plan_dashboard-late'), color: COLORS.late, frozen: fLate, actual: aLate },
    { name: t('text-plan_dashboard-short'), color: COLORS.short, frozen: fShort, actual: aShort },
    { name: t('text-plan_dashboard_isu-upcoming_ratio'), color: COLORS.upcoming, frozen: fUpcoming, actual: aUpcoming },
  ];

  // 각 row별 마지막 non-zero 세그먼트 인덱스
  let lastFrozenIdx = -1;
  let lastActualIdx = -1;
  for (let i = segmentsDef.length - 1; i >= 0; i--) {
    if (lastFrozenIdx < 0 && segmentsDef[i].frozen > 0) lastFrozenIdx = i;
    if (lastActualIdx < 0 && segmentsDef[i].actual > 0) lastActualIdx = i;
    if (lastFrozenIdx >= 0 && lastActualIdx >= 0) break;
  }

  const series = segmentsDef.map((seg, idx) => ({
    name: seg.name,
    type: "bar" as const,
    stack: "total",
    barWidth: 36,
    data: [
      { value: seg.frozen, itemStyle: { color: seg.color, borderRadius: idx === lastFrozenIdx ? [0, 8, 8, 0] : [0, 0, 0, 0] } },
      { value: seg.actual, itemStyle: { color: seg.color, borderRadius: idx === lastActualIdx ? [0, 8, 8, 0] : [0, 0, 0, 0] } },
    ],
    label: { show: true, position: "inside" as const, color: "#fff", fontSize: 12, formatter: makeLabelFormatter() },
  }));

  return {
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "shadow" as const },
      appendTo: () => document.body,
      confine: false,
    },
    legend: { show: false },
    grid: { top: 10, bottom: 24, left: 120, right: 10 },
    xAxis: {
      type: "value" as const,
      max: 100,
      axisLabel: { formatter: "{value}", color: "#96A5BE" },
      splitLine: {
        lineStyle: { color: "rgba(221,221,226,1)", type: "dashed" as const },
      },
    },
    yAxis: {
      type: "category" as const,
      data: [t('text-isu_current_month_otd_expected_rate'), t('text-isu_act_otd_rate')],
      axisLabel: { color: "#96A5BE", fontSize: 12 },
      axisTick: { show: false },
    },
    series,
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

.container-body-wrapper {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 20px;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 1rem;
  font-weight: 500;
  color: #565f6e;
}

.unit-label {
  font-size: 12px;
  font-weight: 400;
  color: #939aac;
  line-height: 14.4px;
}

.kpi-section {
  margin-top: 4px;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.kpi-description {
  font-size: 0.75rem;
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

.chart-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 12px;
}

.chart-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-legend .legend-icon {
  width: 14px;
  height: 14px;
  padding: 6px;
  border-radius: 50%;
  box-sizing: content-box;
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.chart-legend .legend-title {
  font-size: 12px;
  color: #6a7184;
}

.container-body-wrapper {
  display: flex;
  flex-direction: column;
}

.chart {
  width: 100%;
  flex: 1;
  min-height: 100px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 14px;
  color: rgba(40, 54, 78, 1);
  font-weight: 500;
}
</style>
