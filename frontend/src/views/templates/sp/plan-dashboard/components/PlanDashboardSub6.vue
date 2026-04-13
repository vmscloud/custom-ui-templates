<template>
  <div class="container">
    <div class="container-header-wrapper">
      <div class="header-top">
        <div class="panel-title">
          {{ t("text-plan_dashboard_isu-frozen_replan_comparison_report") }}

          <Button
            style="margin-top: 2px"
            class="small"
            type="icon"
            @click="
              openLinkNewTab(
                {
                  path: '/pe/ReExecutePlan',
                  query: { planVer: planVer || '' },
                },
                true,
              )
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
                >({{ t("text-frozen_planned_total") }})</span
              >
            </div>
            <div class="kpi-separator"></div>
            <div class="kpi-item">
              <span class="kpi-value">{{
                formatNumber(planData.demandQty)
              }}</span>
              <span class="kpi-sub"
                >({{ t("text-current_planned_total") }})</span
              >
            </div>
          </div>
          <Radio
            :valueExpr="'value'"
            :display-expr="'label'"
            :items-source="replanOptionSource"
            v-model="replanOption"
          />
        </div>
      </div>
    </div>
    <div class="container-body-wrapper">
      <div v-if="otdLoading" class="loading-wrapper">
        <div class="loading-spinner" />
      </div>
      <div v-else-if="hasData" class="grid-wrapper">
        <SimpleGrid
          :itemsSource="gridData"
          :simpleColumns="simpleColumns"
          :simpleFormatItem="simpleFormatItem"
          :enableCellMerge="true"
          :mergeColumnIndex="0"
        />
      </div>
      <div v-else class="no-data">{{ t("msg-data_empty") }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, ref, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { Button, Radio } from "@vmscloud/moz-ui-components";
import type { usePlanDashboard } from "../planDashboard";
import SimpleGrid from "./SimpleGrid.vue";
import { useHostPlanCycle } from "@/composables/useHostStores";
import IconOpen from "../assets/IconOpen.vue";

const { t } = useTranslation();

type PlanDashboardContext = ReturnType<typeof usePlanDashboard>;
const planDashboard = inject<PlanDashboardContext>("planDashboard")!;
const { dashboardData } = planDashboard;
const openLinkNewTab = inject<(route: any, force?: boolean) => void>(
  "openLinkNewTab",
  () => {},
);
const { planVer } = useHostPlanCycle();

const replanOption = ref("ITEMGROUP");
const replanOptionSource = computed(() => [
  { value: "ITEMGROUP", label: t("text-isu_item_group") },
  { value: "DEMANDTYPE", label: t("text-isu_prod_type") },
]);

const { refreshOtdSummary } = planDashboard;

const otdData = computed(() => dashboardData.value?.otdSummaryPlan ?? dashboardData.value?.otdSummary);

const otdLoading = ref(false);

// Radio 전환 시 Sub6(PLAN) OTD만 재조회
watch(replanOption, async (newVal) => {
  if (planVer.value) {
    otdLoading.value = true;
    await refreshOtdSummary(planVer.value, newVal, "PLAN");
    otdLoading.value = false;
  }
});

const frozenData = computed(() => ({
  qtyUom: otdData.value?.qtyUom ?? "",
  demandQty: otdData.value?.frozenQty ?? 0,
}));

const planData = computed(() => ({
  demandQty: otdData.value?.planQty ?? 0,
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
    header: t("text-isu_item_group"),
    type: "string",
    width: 90,
  },
  {
    binding: "rowType",
    id: 1,
    header: t("text-type"),
    type: "string",
    width: 55,
  },
  { binding: "previous_due_bucket_prod_qty", id: 2, header: t("text-previous_month"), type: "number", width: 60 },
  { binding: "current_due_bucket_prod_qty", id: 3, header: t("text-current_month"), type: "number", width: 60 },
  { binding: "next_due_bucket_prod_qty", id: 4, header: t("text-next_month"), type: "number", width: 60 },
  { binding: "after_next_due_bucket_prod_qty", id: 5, header: t("text-after_next_month"), type: "number", width: 60 },
  {
    binding: "total_qty",
    id: 6,
    header: t("text-total"),
    type: "number",
    width: 60,
  },
]);

const gridData = computed(() => {
  const list = otdData.value?.list ?? [];
  const frozenRows = list.filter((r: any) => r.type === "FROZEN");
  const planRows = list.filter((r: any) => r.type === "PLAN");

  // item_group별 월초+재수립 2행 병합 구조 (APS 원본과 동일)
  const frozenMap = new Map<string, any>();
  for (const row of frozenRows) frozenMap.set(row.category, row);

  const planMap = new Map<string, any>();
  for (const row of planRows) planMap.set(row.category, row);

  const categories = [...new Set([...frozenMap.keys(), ...planMap.keys()])].sort();
  const rows: any[] = [];

  for (const cat of categories) {
    const frozen = frozenMap.get(cat);
    const plan = planMap.get(cat);

    // 월초 행
    rows.push({
      category: cat,
      rowType: t("text-early_in_the_month"),
      previous_due_bucket_prod_qty: frozen?.previous_due_bucket_prod_qty ?? 0,
      current_due_bucket_prod_qty: frozen?.current_due_bucket_prod_qty ?? 0,
      next_due_bucket_prod_qty: frozen?.next_due_bucket_prod_qty ?? 0,
      after_next_due_bucket_prod_qty: frozen?.after_next_due_bucket_prod_qty ?? 0,
      total_qty: frozen?.total_qty ?? 0,
      _isFrozen: true,
    });
    // 재수립 행
    rows.push({
      category: cat,
      rowType: t("text-isu_revised_plan_qty"),
      previous_due_bucket_prod_qty: plan?.previous_due_bucket_prod_qty ?? 0,
      current_due_bucket_prod_qty: plan?.current_due_bucket_prod_qty ?? 0,
      next_due_bucket_prod_qty: plan?.next_due_bucket_prod_qty ?? 0,
      after_next_due_bucket_prod_qty: plan?.after_next_due_bucket_prod_qty ?? 0,
      total_qty: plan?.total_qty ?? 0,
      _isFrozen: false,
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

  // 유형 셀 스타일
  if (columnKey === "rowType") {
    element.style.textAlign = "center";
    element.style.fontSize = "12px";
    element.style.color = "#565f6e";
    const cv = element.querySelector(".cell-value") as HTMLElement | null;
    if (cv) cv.style.justifyContent = "center";
  }

  // 월초(frozen) 행: 연한 배경 / 재수립 행: 흰색
  if (rowData._isFrozen) {
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

.loading-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e1e3f0;
  border-top: 3px solid #4568e0;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
