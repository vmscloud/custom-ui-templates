<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <div class="panel-title">{{ t('text-isu_current_month_otd_fcst_rate', { month: '' }).trim() }}</div>
        <span class="unit-label">{{ qtyUom ? t('text-fgs_stock_report_qty_uom', { unit: qtyUom }) : '' }}</span>
      </div>
      <div class="kpi-section">
        <span class="kpi-value">{{ rtfRatio }}%</span>
        <span class="kpi-description">({{ t('text-plan_dashboard-rtf_ratio') }})</span>
      </div>
    </div>
    <div class="container-body-wrapper">
      <div v-if="hasData" class="chart-body">
        <v-chart class="chart" :option="chartOption" autoresize />
        <div class="legend-grid">
          <div
            class="legend-item"
            v-for="item in legendItems"
            :key="item.title"
          >
            <div class="legend-icon" :style="{ backgroundColor: item.color }">
              <icon-time :width="20" :height="20" :color="'white'" />
            </div>
            <div class="legend-text">
              <div class="title">{{ item.title }}</div>
              <div class="value">{{ item.ratio }}%</div>
              <div class="sub-value">{{ item.qty }}</div>
            </div>
          </div>
        </div>
      </div>
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
import { PieChart } from "@vmscloud/moz-ui-chart/echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GraphicComponent,
} from "@vmscloud/moz-ui-chart/echarts/components";
import {
  normalizeRatios,
  type usePlanDashboard,
} from "../planDashboard";
import IconTime from "../assets/IconTime.vue";

const { t } = useTranslation();

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GraphicComponent,
]);

type PlanDashboardContext = ReturnType<typeof usePlanDashboard>;
const planDashboard = inject<PlanDashboardContext>("planDashboard")!;
const { dashboardData } = planDashboard;

const COLORS = {
  early: "#aac7e8",
  ontime: "#6daafa",
  late: "#feb34e",
  short: "#dc5a5a",
};

const frozen = computed(() => dashboardData.value?.rtfSummary?.frozen);

const hasData = computed(() => {
  return frozen.value != null && frozen.value.demandQty > 0;
});

const qtyUom = computed(() => frozen.value?.qtyUom ?? "");

const rtfRatio = computed(() => {
  if (frozen.value?.rtfRatio != null) {
    return frozen.value.rtfRatio.toFixed(1);
  }
  return "0.0";
});

// 소수점 2자리 반올림 + 총합 100% 보정
const ratios = computed(() => {
  const f = frozen.value;
  if (!f) return [0, 0, 0, 0];
  return normalizeRatios([
    f.earlyRatio,
    f.ontimeRatio,
    f.lateRatio,
    f.shortRatio,
  ]);
});

const earlyQty = computed(() => frozen.value?.earlyQty ?? 0);
const ontimeQty = computed(() => frozen.value?.ontimeQty ?? 0);
const lateQty = computed(() => frozen.value?.lateQty ?? 0);
const shortQty = computed(() => frozen.value?.shortQty ?? 0);

const legendItems = computed(() => {
  const [early, ontime, late, short] = ratios.value;
  return [
    {
      title: t('text-plan_dashboard-early'),
      color: COLORS.early,
      ratio: early.toFixed(2),
      qty: earlyQty.value.toLocaleString(),
    },
    {
      title: t('text-plan_dashboard-on_time'),
      color: COLORS.ontime,
      ratio: ontime.toFixed(2),
      qty: ontimeQty.value.toLocaleString(),
    },
    {
      title: t('text-plan_dashboard-late'),
      color: COLORS.late,
      ratio: late.toFixed(2),
      qty: lateQty.value.toLocaleString(),
    },
    {
      title: t('text-plan_dashboard-short'),
      color: COLORS.short,
      ratio: short.toFixed(2),
      qty: shortQty.value.toLocaleString(),
    },
  ];
});

const chartOption = computed(() => {
  const [early, ontime, late, short] = ratios.value;
  const data = [
    { value: early, name: t('text-plan_dashboard-early'), itemStyle: { color: COLORS.early } },
    { value: ontime, name: t('text-plan_dashboard-on_time'), itemStyle: { color: COLORS.ontime } },
    { value: late, name: t('text-plan_dashboard-late'), itemStyle: { color: COLORS.late } },
    { value: short, name: t('text-plan_dashboard-short'), itemStyle: { color: COLORS.short } },
  ];

  return {
    tooltip: {
      trigger: "item" as const,
      formatter: "{b}: {d}%",
      appendTo: () => document.body,
      confine: false,
    },
    legend: { show: false },
    series: [
      {
        name: t('text-plan_dashboard-rtf_ratio'),
        type: "pie" as const,
        radius: ["50%", "85%"],
        center: ["50%", "50%"],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: "inside" as const,
          color: "#fff",
          fontSize: 11,
          formatter: (p: any) => (p.value > 0 ? `${p.value.toFixed(1)}%` : ""),
        },
        emphasis: {
          scale: true,
          label: { show: true },
        },
        labelLine: { show: false },
        data,
      },
    ],
    graphic: {
      type: "text" as const,
      left: "center",
      top: "center",
      style: {
        text: `${rtfRatio.value}%`,
        fontSize: 20,
        fontWeight: "bold" as const,
        fill: "#28364e",
        textAlign: "center" as const,
      },
    },
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

.chart-body {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 28px;
  padding: 16px 20px 20px 20px;
  height: 100%;
  overflow: hidden;
}

.chart {
  flex-shrink: 0;
  width: 35%;
  min-width: 140px;
  max-width: 200px;
  aspect-ratio: 1;
}

.legend-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  row-gap: 20px;
  column-gap: 20px;
  flex-shrink: 1;
  min-width: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.legend-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.legend-text {
  .title {
    font-size: 0.75rem;
    font-weight: 500;
    color: #6a7184;
  }

  .value {
    font-size: 24px;
    font-weight: 700;
    color: #28364e;
  }

  .sub-value {
    font-size: 0.875rem;
    font-weight: 400;
    color: #96a5be;
  }
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
