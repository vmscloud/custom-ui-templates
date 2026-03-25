<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <span class="panel-title">
          {{ t('text-plan_dashboard_isu-frozen_act_comparison_report') }}
          <button class="link-btn" @click="openLinkNewTab({ path: '/pa/ActualPlanResult' }, true)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5 1h8v8M13 1L6 8" stroke="#8998b5" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </span>
        <span class="unit-label">{{ frozenData.qtyUom ? t('text-fgs_stock_report_qty_uom', { unit: frozenData.qtyUom }) : '' }}</span>
      </div>
      <div class="kpi-section">
        <div class="kpi-row">
          <div class="kpi-dual">
            <div class="kpi-item">
              <span class="kpi-value">{{ formatNumber(frozenData.demandQty) }}</span>
              <span class="kpi-sub">({{ t('text-plan_dashboard_isu-total_plan_qty_by_month') }})</span>
            </div>
            <div class="kpi-separator"></div>
            <div class="kpi-item">
              <span class="kpi-value">{{ formatNumber(actualData.demandQty) }}</span>
              <span class="kpi-sub">({{ t('text-cumulative_performance_volume') }})</span>
            </div>
          </div>
          <Radio
            :valueExpr="'value'"
            :display-expr="'label'"
            :items-source="planOptionSource"
            v-model="planOption"
          />
        </div>
      </div>
    </div>
    <div class="container-body-wrapper">
      <div v-if="hasData" class="grid-wrapper">
        <SimpleGrid
          :itemsSource="gridData"
          :simpleColumns="simpleColumns"
          :simpleFormatItem="simpleFormatItem"
        />
      </div>
      <div v-else class="no-data">{{ t('msg-data_empty') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useTranslation } from "i18next-vue";
import { Radio } from "@vmscloud/moz-ui-components";
import type { usePlanDashboard } from "../planDashboard";
import type { RTFSummary } from "../planDashboard";
import SimpleGrid from "./SimpleGrid.vue";

const { t } = useTranslation();

type PlanDashboardContext = ReturnType<typeof usePlanDashboard>;
const planDashboard = inject<PlanDashboardContext>("planDashboard")!;
const { dashboardData } = planDashboard;
const openLinkNewTab = inject<(route: any, force?: boolean) => void>('openLinkNewTab', () => {});

const planOption = ref("ITEMGROUP");
const planOptionSource = computed(() => [
  { value: "ITEMGROUP", label: t('text-isu_item_group') },
  { value: "DEMANDTYPE", label: t('text-isu_prod_type') },
]);

const EMPTY_SUMMARY: RTFSummary = {
  demandQty: 0,
  earlyQty: 0,
  earlyRatio: 0,
  ontimeQty: 0,
  ontimeRatio: 0,
  lateQty: 0,
  lateRatio: 0,
  shortQty: 0,
  shortRatio: 0,
  rtfQty: 0,
  rtfRatio: 0,
  upcomingQty: 0,
  upcomingRatio: 0,
  qtyUom: "",
  uomType: "",
};

const hasData = computed(() => {
  const summary = dashboardData.value?.rtfSummary;
  return summary?.frozen != null || summary?.actual != null;
});

const frozenData = computed<RTFSummary>(() =>
  dashboardData.value?.rtfSummary?.frozen ?? EMPTY_SUMMARY,
);

const actualData = computed<RTFSummary>(() =>
  dashboardData.value?.rtfSummary?.actual ?? EMPTY_SUMMARY,
);

function formatNumber(val: number): string {
  if (val == null) return "0";
  return val.toLocaleString();
}

const simpleColumns = computed(() => [
  { binding: "category", id: 0, header: t('text-type'), type: "string", width: 70 },
  { binding: "demandQty", id: 1, header: t('text-total_qty'), type: "number", width: 90 },
  { binding: "earlyQty", id: 2, header: "Early", type: "number", width: 80 },
  { binding: "ontimeQty", id: 3, header: "On-time", type: "number", width: 90 },
  { binding: "lateQty", id: 4, header: "Late", type: "number", width: 80 },
  { binding: "shortQty", id: 5, header: "Short", type: "number", width: 80 },
  { binding: "rtfRatio", id: 6, header: t('text-plan_dashboard-rtf_ratio'), type: "string", width: 70 },
]);

const gridData = computed(() => {
  const f = frozenData.value;
  const a = actualData.value;
  return [
    {
      category: "Frozen",
      type: "FROZEN",
      demandQty: f.demandQty,
      earlyQty: f.earlyQty,
      ontimeQty: f.ontimeQty,
      lateQty: f.lateQty,
      shortQty: f.shortQty,
      rtfRatio: f.rtfRatio.toFixed(1) + "%",
    },
    {
      category: "Actual",
      type: "ACT",
      demandQty: a.demandQty,
      earlyQty: a.earlyQty,
      ontimeQty: a.ontimeQty,
      lateQty: a.lateQty,
      shortQty: a.shortQty,
      rtfRatio: a.rtfRatio.toFixed(1) + "%",
    },
  ];
});

const simpleFormatItem = (
  element: HTMLElement,
  _rowIndex: number,
  columnKey: string,
  _value: any,
  rowData: any,
) => {
  // Category cells: centered with header-like background
  if (columnKey === "category") {
    element.style.background = "#eef1fc";
    element.style.textAlign = "center";
    element.style.fontWeight = "500";
    element.style.fontSize = "13px";
    element.style.color = "#565f6e";
    // Override cell-value alignment
    const cellValue = element.querySelector(".cell-value") as HTMLElement | null;
    if (cellValue) {
      cellValue.style.justifyContent = "center";
    }
    return;
  }

  // Row background based on type
  if (rowData.type === "FROZEN") {
    element.style.backgroundColor = "#F8F8FD";
  } else {
    element.style.backgroundColor = "#FFFFFF";
  }
};
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
}

.kpi-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.kpi-dual {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-item {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #28364e;
  line-height: 1.4;
  position: relative;
  z-index: 2;
  display: inline-block;
  width: fit-content;

  &::after {
    display: block;
    position: absolute;
    content: '';
    left: 0;
    bottom: 1px;
    width: 100%;
    height: 8px;
    background-color: #4568e04d;
    z-index: -1;
  }
}

.kpi-sub {
  font-size: 12px;
  font-weight: 500;
  color: #6a7184;
  margin-top: 2px;
}

.kpi-separator {
  width: 1px;
  height: 22px;
  background-color: #bac6d4;
  flex-shrink: 0;
}

.container-body-wrapper {
  flex: 1;
  min-height: 0;
  padding: 20px;
  overflow: auto;
}

.grid-wrapper {
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
