<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <div class="panel-title">
          {{ t("text-plan_dashboard_isu-frozen_act_comparison_report") }}

          <Button
            style="margin-top: 2px"
            class="small"
            type="icon"
            @click="
              openLinkNewTab({
                path: `/pa/ActualPlanResult`,
              }, true)
            "
          >
            <IconOpen :height="14" :width="14" />
          </Button>
        </div>
        <span class="unit-label">{{
          frozenData.qtyUom
            ? t("text-fgs_stock_report_qty_uom", { unit: frozenData.qtyUom })
            : ""
        }}</span>
      </div>
      <div class="kpi-section">
        <div class="kpi-row">
          <div class="kpi-dual">
            <div class="kpi-item">
              <span class="kpi-value">{{
                formatNumber(frozenData.demandQty)
              }}</span>
              <span class="kpi-sub"
                >({{
                  t("text-plan_dashboard_isu-total_plan_qty_by_month")
                }})</span
              >
            </div>
            <div class="kpi-separator"></div>
            <div class="kpi-item">
              <span class="kpi-value">{{
                formatNumber(actualData.demandQty)
              }}</span>
              <span class="kpi-sub"
                >({{ t("text-cumulative_performance_volume") }})</span
              >
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
      <div v-else class="no-data">{{ t("msg-data_empty") }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useTranslation } from "i18next-vue";
import { Button, Radio } from "@vmscloud/moz-ui-components";
import type { usePlanDashboard } from "../planDashboard";
import SimpleGrid from "./SimpleGrid.vue";
import IconOpen from "../assets/IconOpen.vue";

const { t } = useTranslation();

type PlanDashboardContext = ReturnType<typeof usePlanDashboard>;
const planDashboard = inject<PlanDashboardContext>("planDashboard")!;
const { dashboardData } = planDashboard;
const openLinkNewTab = inject<(route: any, force?: boolean) => void>(
  "openLinkNewTab",
  () => {},
);

const planOption = ref("ITEMGROUP");
const planOptionSource = computed(() => [
  { value: "ITEMGROUP", label: t("text-isu_item_group") },
  { value: "DEMANDTYPE", label: t("text-isu_prod_type") },
]);

const otdData = computed(() => dashboardData.value?.otdSummary);

const frozenData = computed(() => ({
  qtyUom: otdData.value?.qtyUom ?? "",
  demandQty: otdData.value?.frozenQty ?? 0,
}));

const actualData = computed(() => ({
  demandQty: otdData.value?.actQty ?? 0,
}));

const hasData = computed(() => {
  return (otdData.value?.list?.length ?? 0) > 0 || (otdData.value?.frozenQty ?? 0) > 0;
});

function formatNumber(val: number): string {
  if (val == null) return "0";
  return val.toLocaleString();
}

const simpleColumns = computed(() => [
  {
    binding: "category",
    id: 0,
    header: t("text-type"),
    type: "string",
    width: 100,
  },
  {
    binding: "total_qty",
    id: 1,
    header: t("text-total_qty"),
    type: "number",
    width: 90,
  },
  { binding: "current_due_bucket_prod_qty", id: 2, header: "Early", type: "number", width: 80 },
  { binding: "previous_due_bucket_prod_qty", id: 3, header: "On-time", type: "number", width: 90 },
  { binding: "next_due_bucket_prod_qty", id: 4, header: "Late", type: "number", width: 80 },
  { binding: "after_next_due_bucket_prod_qty", id: 5, header: "Short", type: "number", width: 80 },
  {
    binding: "rtfRatio",
    id: 6,
    header: t("text-plan_dashboard-rtf_ratio"),
    type: "string",
    width: 70,
  },
]);

const gridData = computed(() => {
  const list = otdData.value?.list ?? [];
  const frozenRows = list.filter((r: any) => r.type === "FROZEN");
  const actRows = list.filter((r: any) => r.type === "ACT");

  const rtfFrozen = dashboardData.value?.rtfSummary?.frozen;
  const rtfActual = dashboardData.value?.rtfSummary?.actual;

  const rows: any[] = [];
  for (const row of frozenRows) {
    rows.push({ ...row, category: row.category, rtfRatio: "" });
  }
  if (frozenRows.length === 0 && rtfFrozen) {
    rows.push({
      category: "Frozen",
      type: "FROZEN",
      total_qty: rtfFrozen.demandQty,
      current_due_bucket_prod_qty: rtfFrozen.earlyQty,
      previous_due_bucket_prod_qty: rtfFrozen.ontimeQty,
      next_due_bucket_prod_qty: rtfFrozen.lateQty,
      after_next_due_bucket_prod_qty: rtfFrozen.shortQty,
      rtfRatio: rtfFrozen.rtfRatio.toFixed(1) + "%",
    });
  }
  for (const row of actRows) {
    rows.push({ ...row, category: row.category, rtfRatio: "" });
  }
  if (actRows.length === 0 && rtfActual) {
    rows.push({
      category: "Actual",
      type: "ACT",
      total_qty: rtfActual.demandQty,
      current_due_bucket_prod_qty: rtfActual.earlyQty,
      previous_due_bucket_prod_qty: rtfActual.ontimeQty,
      next_due_bucket_prod_qty: rtfActual.lateQty,
      after_next_due_bucket_prod_qty: rtfActual.shortQty,
      rtfRatio: rtfActual.rtfRatio.toFixed(1) + "%",
    });
  }
  return rows;
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
    const cellValue = element.querySelector(
      ".cell-value",
    ) as HTMLElement | null;
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
    content: "";
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
