<template>
  <div class="ontime-replan-detail">
    <!-- Production Plan Grid -->
    <div class="pivot-container">
      <MozGrid
        name="onTimeReplanProdDetail"
        :coreConfig="coreConfig"
        height="100%"
        :loading="loading"
        :use-tool-box="true"
        :use-sort="false"
        :emptyState="{
          contentMsg: !gridData || gridData.length === 0 ? '수요를 선택하세요' : '',
        }"
      />
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
      <MozGrid
        name="onTimeReplanDemandInfo"
        :coreConfig="demandInfoCoreConfig"
        height="100%"
        :use-tool-box="false"
      />
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
      <MozGrid
        name="onTimeReplanPegInfo"
        :coreConfig="pegInfoCoreConfig"
        height="100%"
        :use-tool-box="false"
      />
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
      <MozGrid
        name="onTimeReplanBomMap"
        :coreConfig="bomMapCoreConfig"
        height="100%"
        :use-tool-box="false"
      />
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useTranslation } from "i18next-vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { FieldDef, MaskConfig, MozGridCoreProps } from "@vmscloud/moz-ui-grid-vue";
import { Popup } from "@vmscloud/moz-ui-components-vue";
import { GRID_ROW_KEY, withRowKey } from "./onTimeRescheduledPlanResult";
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

const demandInfoPopupVisible = ref(false);
const pegInfoPopupVisible = ref(false);
const bomMapPopupVisible = ref(false);

const N0_MASK: MaskConfig = { type: "numeric", pattern: "#,##0" };
const N2_MASK: MaskConfig = { type: "numeric", pattern: "#,##0.00" };

// === Computed ===

/** Period columns from prod-detail response */
const periodColumns = computed(() => {
  if (!props.data?.period) return [];
  return props.data.period;
});

/** Flattened grid data: merge detail rows with date columns */
const gridData = computed(() => {
  if (!props.data?.detail || props.data.detail.length === 0) return [];
  return withRowKey(
    props.data.detail.map((row) => ({
      ...row,
      total_prod_qty: formatDecimal(row.total_prod_qty),
    })),
  );
});

const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: gridData.value,
  fields: [
    { id: "oper_group_id", header: t("text-oper_group_id"), dataType: "string", width: 120 },
    { id: "item_id", header: t("text-item_id"), dataType: "string", width: 120 },
    { id: "total_prod_qty", header: t("text-isu_used_total"), dataType: "string", align: "right", width: 100 },
    { id: "oper_id", header: t("text-oper_id"), dataType: "string", width: 100, hidden: true },
    { id: "site_id", header: t("text-site_id"), dataType: "string", width: 80, hidden: true },
    { id: "item_type", header: t("text-item_type"), dataType: "string", width: 90, hidden: true },
    { id: "wip_qty", header: "WIP", dataType: "number", align: "right", width: 90, mask: N0_MASK, hidden: true },
    { id: "peg_qty", header: t("text-peg_qty"), dataType: "number", align: "right", width: 90, mask: N0_MASK, hidden: true },
    { id: "prod_qty", header: t("text-prod_qty"), dataType: "number", align: "right", width: 100, mask: N2_MASK },
    { id: "plan_date", header: t("text-plan_date"), dataType: "string", width: 100, align: "center" },
    { id: "plan_month", header: t("text-plan_month"), dataType: "string", width: 90, align: "center" },
    ...periodColumns.value.map<FieldDef>((period) => ({
      id: `date_${period}`,
      header: period,
      dataType: "number",
      align: "right",
      width: 90,
      mask: N2_MASK,
      // Highlight negative values in red
      cellAttributes: ({ value }: { value: unknown }) =>
        typeof value === "number" && value < 0 ? { class: "negative-number" } : undefined,
    })),
  ],
}));

const demandInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.demandInfoData),
  fields: [
    { id: "demand_id", header: t("text-demand_id"), dataType: "string", width: 120 },
    { id: "item_id", header: t("text-item_id"), dataType: "string", width: 120 },
    { id: "cust_id", header: t("text-cust_name"), dataType: "string", width: 100 },
    { id: "due_date", header: t("text-due_date"), dataType: "string", width: 110 },
    { id: "demand_qty", header: t("text-demand_qty"), dataType: "number", width: 90, align: "right", mask: N0_MASK },
  ],
}));

const pegInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.pegInfoData),
  fields: [
    { id: "demand_id", header: t("text-demand_id"), dataType: "string", width: 120 },
    { id: "item_id", header: t("text-item_id"), dataType: "string", width: 120 },
    { id: "peg_qty", header: t("text-peg_qty"), dataType: "number", width: 90, align: "right", mask: N0_MASK },
    { id: "plan_date", header: t("text-plan_date"), dataType: "string", width: 110 },
  ],
}));

const bomMapCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.bomMapData),
  fields: [
    { id: "item_id", header: t("text-item_id"), dataType: "string", width: 120 },
    { id: "bom_id", header: t("text-bom_id"), dataType: "string", width: 120 },
    { id: "routing_id", header: t("text-routing_id"), dataType: "string", width: 120 },
    { id: "oper_id", header: t("text-oper_id"), dataType: "string", width: 100 },
    { id: "qty", header: t("text-short_qty"), dataType: "number", width: 90, align: "right", mask: N0_MASK },
  ],
}));

// === Helpers ===

function formatDecimal(value: any): string {
  if (typeof value !== "number" || isNaN(value)) return String(value ?? "");
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

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
.negative-number {
  color: #dc5a5a !important;
}
</style>
