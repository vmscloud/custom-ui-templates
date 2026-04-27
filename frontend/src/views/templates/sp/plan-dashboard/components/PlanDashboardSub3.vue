<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <div class="panel-title">
          {{ t("text-plan_dashboard_isu-replan_rtf_report") }}

          <Button
            style="margin-top: 2px"
            class="small"
            type="icon"
            @click="
              openLinkNewTab({
                path: `/sp/OnTimeRescheduledPlanResult`,
                query: {
                  planVer: planVer || '',
                  region: rtfReportRegion,
                },
              }, true)
            "
          >
            <icon-open :height="14" :width="14" />
          </Button>
        </div>
        <span class="unit-label">{{
          qtyUom ? t("text-fgs_stock_report_qty_uom", { unit: qtyUom }) : ""
        }}</span>
      </div>
      <div class="kpi-section">
        <span class="kpi-value">{{ planRtfRatio }}%</span>
        <span class="kpi-description"
          >({{ t("text-isu_replan_otd_rate") }})</span
        >
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
      <div v-else class="no-data">{{ t("msg-data_empty") }}</div>
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
import {
  normalizeRatios,
  round2,
  type usePlanDashboard,
} from "../planDashboard";
import IconTime from "../assets/IconTime.vue";
import { useHostPlanCycle } from "@/composables/useHostStores";
import { Button } from "@vmscloud/moz-ui-components";
import IconOpen from "../assets/IconOpen.vue";

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
const { dashboardData, region } = planDashboard;
const openLinkNewTab = inject<(route: any, force?: boolean) => void>(
  "openLinkNewTab",
  () => {},
);
const { planVer } = useHostPlanCycle();

// Dashboard region (ex. "RTF_대구") → OnTimeRescheduledPlanResult region param.
//   원본 patch(#3929): "RTF" 또는 null 은 'default' 로, "RTF_xxx" 는 "xxx" 로 변환.
//   파라미터를 넘기지 않으면 RTF 리포트가 기본 region 으로 뜨고 대시보드 값과 불일치함.
const rtfReportRegion = computed(() => {
  const v = region.value;
  if (!v || v === "RTF") return "default";
  return v.replace("RTF_", "");
});

const COLORS = {
  ontime: "#6daafa",
  early: "#aac7e8",
  late: "#feb34e",
  short: "#dc5a5a",
};

const plan = computed(() => dashboardData.value?.rtfSummary?.plan);
const frozen = computed(() => dashboardData.value?.rtfSummary?.frozen);

const hasData = computed(() => {
  return plan.value != null || frozen.value != null;
});

const qtyUom = computed(() => plan.value?.qtyUom ?? frozen.value?.qtyUom ?? "");

const planRtfRatio = computed(() => {
  if (plan.value?.rtfRatio != null) {
    return plan.value.rtfRatio.toFixed(1);
  }
  return "0.0";
});

const legendItems = computed(() => [
  { label: t("text-plan_dashboard-on_time"), color: COLORS.ontime },
  { label: t("text-plan_dashboard-early"), color: COLORS.early },
  { label: t("text-plan_dashboard-late"), color: COLORS.late },
  { label: t("text-plan_dashboard-short"), color: COLORS.short },
]);

const chartOption = computed(() => {
  const p = plan.value;
  const f = frozen.value;

  // 소수점 2자리 반올림 + 총합 100% 보정 (4 segments, no upcoming)
  const [fOntime, fEarly, fLate, fShort] = normalizeRatios([
    f?.ontimeRatio ?? 0,
    f?.earlyRatio ?? 0,
    f?.lateRatio ?? 0,
    f?.shortRatio ?? 0,
  ]);
  const [pOntime, pEarly, pLate, pShort] = normalizeRatios([
    p?.ontimeRatio ?? 0,
    p?.earlyRatio ?? 0,
    p?.lateRatio ?? 0,
    p?.shortRatio ?? 0,
  ]);

  const makeLabelFormatter = () => {
    return (params: any) =>
      params.value > 5 ? round2(params.value) + "%" : "";
  };

  // 각 bar별로 마지막 non-zero 세그먼트에 오른쪽 borderRadius 적용
  const segmentsDef = [
    {
      name: t("text-plan_dashboard-on_time"),
      color: COLORS.ontime,
      frozen: fOntime,
      plan: pOntime,
    },
    {
      name: t("text-plan_dashboard-early"),
      color: COLORS.early,
      frozen: fEarly,
      plan: pEarly,
    },
    {
      name: t("text-plan_dashboard-late"),
      color: COLORS.late,
      frozen: fLate,
      plan: pLate,
    },
    {
      name: t("text-plan_dashboard-short"),
      color: COLORS.short,
      frozen: fShort,
      plan: pShort,
    },
  ];

  let lastFrozenIdx = -1;
  let lastPlanIdx = -1;
  for (let i = segmentsDef.length - 1; i >= 0; i--) {
    if (lastFrozenIdx < 0 && segmentsDef[i].frozen > 0) lastFrozenIdx = i;
    if (lastPlanIdx < 0 && segmentsDef[i].plan > 0) lastPlanIdx = i;
    if (lastFrozenIdx >= 0 && lastPlanIdx >= 0) break;
  }

  const series = segmentsDef.map((seg, idx) => ({
    name: seg.name,
    type: "bar" as const,
    stack: "total",
    barWidth: 36,
    data: [
      {
        value: seg.frozen,
        itemStyle: {
          color: seg.color,
          borderRadius: idx === lastFrozenIdx ? [0, 8, 8, 0] : [0, 0, 0, 0],
        },
      },
      {
        value: seg.plan,
        itemStyle: {
          color: seg.color,
          borderRadius: idx === lastPlanIdx ? [0, 8, 8, 0] : [0, 0, 0, 0],
        },
      },
    ],
    label: {
      show: true,
      position: "inside" as const,
      color: "#fff",
      fontSize: 12,
      formatter: makeLabelFormatter(),
    },
  }));

  return {
    tooltip: {
      trigger: "axis" as const,
      axisPointer: { type: "shadow" as const },
      appendTo: () => document.body,
      confine: false,
    },
    legend: { show: false },
    grid: { top: 10, bottom: 24, left: 130, right: 10 },
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
      data: [
        t("text-isu_current_month_otd_expected_rate"),
        t("text-isu_replan_otd_rate"),
      ],
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

.link-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-left: 4px;
  vertical-align: middle;
  &:hover svg path {
    stroke: #4568e0;
  }
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
