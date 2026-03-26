<template>
  <div class="ontime-replan-detail">
    <!-- Production Plan Grid -->
    <div class="pivot-container">
      <ExtendFlexGrid
        name="onTimeReplanProdDetail"
        :itemsSource="gridData"
        height="100%"
        :isReadOnly="true"
        allowSorting="None"
        :initialized="onInitialized"
        :formatItem="onFormatItem"
        :loading="loading"
        :use-tool-box="true"
        :emptyState="{
          isLoading: loading,
          contentMsg: !gridData || gridData.length === 0 ? '수요를 선택하세요' : '',
        }"
      >
        <WjFlexGridColumn binding="oper_group_id" :header="t('text-oper_group_id')" :width="120" />
        <WjFlexGridColumn binding="item_id" :header="t('text-item_id')" :width="120" />
        <WjFlexGridColumn binding="total_prod_qty" :header="t('text-isu_used_total')" align="right" :width="100" />
        <WjFlexGridColumn binding="oper_id" :header="t('text-oper_id')" :width="100" :visible="false" />
        <WjFlexGridColumn binding="site_id" :header="t('text-site_id')" :width="80" :visible="false" />
        <WjFlexGridColumn binding="item_type" :header="t('text-item_type')" :width="90" :visible="false" />
        <WjFlexGridColumn binding="wip_qty" header="WIP" dataType="Number" align="right" :width="90" format="n0" :visible="false" />
        <WjFlexGridColumn binding="peg_qty" :header="t('text-peg_qty')" dataType="Number" align="right" :width="90" format="n0" :visible="false" />
        <WjFlexGridColumn binding="prod_qty" :header="t('text-prod_qty')" dataType="Number" align="right" :width="100" format="n2" />
        <WjFlexGridColumn binding="plan_date" :header="t('text-plan_date')" :width="100" align="center" />
        <WjFlexGridColumn binding="plan_month" :header="t('text-plan_month')" :width="90" align="center" />
        <WjFlexGridColumn
          v-for="period in periodColumns"
          :key="period"
          :binding="`date_${period}`"
          :header="period"
          dataType="Number"
          align="right"
          :width="90"
          format="n2"
        />
      </ExtendFlexGrid>
    </div>

    <!-- Demand Info Popup -->
    <Popup
      v-model:visible="demandInfoPopupVisible"
      :title="t('text-demand_info')"
      :width="600"
      :height="400"
      preset="close"
      :onCancel="() => (demandInfoPopupVisible = false)"
    >
      <ExtendFlexGrid
        name="onTimeReplanDemandInfo"
        :itemsSource="demandInfoData"
        height="100%"
        :isReadOnly="true"
        :use-tool-box="false"
      >
        <WjFlexGridColumn binding="demand_id" :header="t('text-demand_id')" :width="120" />
        <WjFlexGridColumn binding="item_id" :header="t('text-item_id')" :width="120" />
        <WjFlexGridColumn binding="cust_id" :header="t('text-cust_name')" :width="100" />
        <WjFlexGridColumn binding="due_date" :header="t('text-due_date')" :width="110" />
        <WjFlexGridColumn binding="demand_qty" :header="t('text-demand_qty')" :width="90" align="right" format="n0" />
      </ExtendFlexGrid>
    </Popup>

    <!-- Peg Info Popup -->
    <Popup
      v-model:visible="pegInfoPopupVisible"
      :title="t('text-peg_info_detail')"
      :width="700"
      :height="500"
      preset="close"
      :onCancel="() => (pegInfoPopupVisible = false)"
    >
      <ExtendFlexGrid
        name="onTimeReplanPegInfo"
        :itemsSource="pegInfoData"
        height="100%"
        :isReadOnly="true"
        :use-tool-box="false"
      >
        <WjFlexGridColumn binding="demand_id" :header="t('text-demand_id')" :width="120" />
        <WjFlexGridColumn binding="item_id" :header="t('text-item_id')" :width="120" />
        <WjFlexGridColumn binding="peg_qty" :header="t('text-peg_qty')" :width="90" align="right" format="n0" />
        <WjFlexGridColumn binding="plan_date" :header="t('text-plan_date')" :width="110" />
      </ExtendFlexGrid>
    </Popup>

    <!-- BOM Map Popup -->
    <Popup
      v-model:visible="bomMapPopupVisible"
      :title="t('text-bom_structure')"
      :width="800"
      :height="600"
      preset="close"
      :onCancel="() => (bomMapPopupVisible = false)"
    >
      <ExtendFlexGrid
        name="onTimeReplanBomMap"
        :itemsSource="bomMapData"
        height="100%"
        :isReadOnly="true"
        :use-tool-box="false"
      >
        <WjFlexGridColumn binding="item_id" :header="t('text-item_id')" :width="120" />
        <WjFlexGridColumn binding="bom_id" :header="t('text-bom_id')" :width="120" />
        <WjFlexGridColumn binding="routing_id" :header="t('text-routing_id')" :width="120" />
        <WjFlexGridColumn binding="oper_id" :header="t('text-oper_id')" :width="100" />
        <WjFlexGridColumn binding="qty" :header="t('text-short_qty')" :width="90" align="right" format="n0" />
      </ExtendFlexGrid>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useTranslation } from "i18next-vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { type FlexGrid, CellType } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { Popup } from "@vmscloud/moz-ui-components";
import type {
  ProdDetailResponse,
} from "./onTimeRescheduledPlanResult";

const { t } = useTranslation();

// === Props & Emits ===

interface Props {
  data: ProdDetailResponse | null;
  demandInfoData: any[];
  pegInfoData: any[];
  bomMapData: any[];
  planVer: string;
  demandId: string;
  isZoomed: boolean;
  loading: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "load-demand-info", demandID: string): void;
  (e: "load-peg-info", demandID: string): void;
  (e: "load-bom-map", demandID: string): void;
}>();

// === Local State ===

const grid = ref<FlexGrid | null>(null);
const demandInfoPopupVisible = ref(false);
const pegInfoPopupVisible = ref(false);
const bomMapPopupVisible = ref(false);

// === Computed ===

/** Period columns from prod-detail response */
const periodColumns = computed(() => {
  if (!props.data?.period) return [];
  return props.data.period;
});

/** Flattened grid data: merge detail rows with date columns */
const gridData = computed(() => {
  if (!props.data?.detail || props.data.detail.length === 0) return [];
  return props.data.detail.map((row) => ({
    ...row,
    total_prod_qty: formatDecimal(row.total_prod_qty),
  }));
});

// === Helpers ===

function formatDecimal(value: any): string {
  if (typeof value !== "number" || isNaN(value)) return String(value ?? "");
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

// === Grid Initialization ===

const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
};

// === FormatItem ===

const onFormatItem = (_s: FlexGrid, e: any) => {
  // Only format data cells
  if (e.panel.cellType !== CellType.Cell) return;

  const binding = e.getColumn()?.binding;
  if (!binding) return;

  // Highlight negative values in red
  const item = e.getRow()?.dataItem;
  if (!item) return;

  if (binding.startsWith("date_") && typeof item[binding] === "number") {
    if (item[binding] < 0) {
      e.cell.classList.add("negative-number");
    }
  }
};

// === Public Methods (called from parent context menu) ===

function openDemandInfo() {
  if (!props.demandId) return;
  emit("load-demand-info", props.demandId);
  demandInfoPopupVisible.value = true;
}

function openPegInfo() {
  if (!props.demandId) return;
  emit("load-peg-info", props.demandId);
  pegInfoPopupVisible.value = true;
}

function openBomMap() {
  if (!props.demandId) return;
  emit("load-bom-map", props.demandId);
  bomMapPopupVisible.value = true;
}

defineExpose({ openDemandInfo, openPegInfo, openBomMap });
</script>

<style lang="scss" scoped>
.ontime-replan-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 4px;
}

.pivot-container {
  flex: 1;
  overflow: hidden;
}
</style>

<style lang="scss">
.negative-number span {
  color: #dc5a5a !important;
}
</style>
