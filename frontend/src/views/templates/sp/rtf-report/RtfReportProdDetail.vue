<template>
  <div class="rtf-report-prod-detail">
    <!-- Demand Summary Bar -->
     <div class="summary-bar-container">
      <div v-if="demandSummaryData.length > 0" class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">수요량</span>
        <span class="summary-value">{{
          formatQty(demandSummaryData[0]?.demand_qty)
        }}</span>
      </div>
      <span class="divider">|</span>
      <div class="summary-item">
        <span class="summary-label">출하량</span>
        <span class="summary-value">{{
          formatQty(demandSummaryData[0]?.shipment_qty)
        }}</span>
      </div>
      <span class="divider">|</span>
      <div class="summary-item">
        <span class="summary-label">WIP</span>
        <span class="summary-value">{{
          formatQty(demandSummaryData[0]?.wip_qty)
        }}</span>
      </div>
      <span class="divider">|</span>
      <div class="summary-item">
        <span class="summary-label">Peg</span>
        <span class="summary-value"
          >{{ formatQty(demandSummaryData[0]?.peg_qty) }} ({{
            formatRatio(demandSummaryData[0]?.peg_ratio)
          }}%)</span
        >
      </div>
      <span class="divider">|</span>
      <div class="summary-item">
        <span class="summary-label">입고일</span>
        <span class="summary-value">{{
          demandSummaryData[0]?.warehousing_date || "-"
        }}</span>
      </div>
      <span class="divider">|</span>
      <div class="summary-item">
        <span class="summary-label">출하일</span>
        <span class="summary-value">{{
          demandSummaryData[0]?.shipment_date || "-"
        }}</span>
      </div>


    </div>

    <!-- Empty Summary Bar -->
    <div v-else class="summary-bar summary-bar-empty">
      <span class="summary-placeholder">수요를 선택하면 요약 정보가 표시됩니다</span>
    </div>

          <!-- Zoom Toggle -->
          <button class="zoom-btn" :title="isZoomed ? '축소' : '확대'" @click="emit('toggle-zoom')">
        {{ isZoomed ? "▼" : "▲" }}
      </button>
     </div>
    

    <!-- Production Plan Pivot Grid -->
    <div class="pivot-container">
      <MozGrid
        name="rtfProdDetailPivot"
        :coreConfig="pivotCoreConfig"
        height="100%"
        :useContextMenu="false"
        :use-tool-box="true"
        :loading="loading"
      />
    </div>

    <!-- Peg Info Popup -->
    <Popup v-model:visible="pegInfoPopupVisible" title="Peg 정보 상세">
      <template #default>
        <div class="popup-content">
          <!-- Demand Info Section -->
          <h4 class="popup-section-title">수요 정보</h4>
          <div class="popup-grid-wrapper popup-grid-small">
            <MozGrid
              name="rtfDemandInfoGrid"
              :coreConfig="demandInfoCoreConfig"
              height="100%"
              :use-tool-box="false"
            />
          </div>

          <!-- Peg Info Detail Section -->
          <h4 class="popup-section-title">Peg 상세</h4>
          <div class="popup-grid-wrapper popup-grid-large">
            <MozGrid
              name="rtfPegInfoDetailGrid"
              :coreConfig="pegInfoCoreConfig"
              height="100%"
              :use-tool-box="false"
            />
          </div>
        </div>
      </template>
      <template #footer>
        <Button @click="pegInfoPopupVisible = false">닫기</Button>
      </template>
    </Popup>

    <!-- Buffer Plan Target Popup -->
    <Popup v-model:visible="bufferPlanPopupVisible" title="Target vs Plan">
      <template #default>
        <div class="popup-content">
          <div class="popup-pivot-wrapper">
            <MozGrid
              name="rtfBufferPlanTargetPivot"
              :coreConfig="bufferPlanCoreConfig"
              height="100%"
              :useContextMenu="false"
              :use-tool-box="false"
            />
          </div>
        </div>
      </template>
      <template #footer>
        <Button @click="bufferPlanPopupVisible = false">닫기</Button>
      </template>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { MaskConfig, MozGridCoreProps } from "@vmscloud/moz-ui-grid-vue";
import { Popup, Button } from "@vmscloud/moz-ui-components-vue";
import { GRID_ROW_KEY, withRowKey } from "./rtfReport";
import type { RtfProdDetailData, RtfDemandSummaryData } from "./rtfReport";

// === Props & Emits ===

interface Props {
  data: RtfProdDetailData[];
  demandSummaryData: RtfDemandSummaryData[];
  demandInfoData: any[];
  pegInfoData: any[];
  bomMapData: any[];
  bufferPlanTargetData: any[];
  planVer: string;
  demandId: string;
  uomType: string;
  isZoomed: boolean;
  loading?: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "toggle-zoom"): void;
  (e: "load-demand-info", demandID: string): void;
  (e: "load-peg-info", demandID: string): void;
  (e: "load-bom-map", demandID: string): void;
  (e: "load-buffer-plan-target", demandID: string): void;
}>();

// === Local State ===

const pegInfoPopupVisible = ref(false);
const bufferPlanPopupVisible = ref(false);

// === Formatting Helpers ===

function formatQty(val: any): string {
  if (val == null) return "-";
  return Number(val).toLocaleString();
}

function formatRatio(val: any): string {
  if (val == null) return "0";
  return Number(val).toLocaleString(undefined, { maximumFractionDigits: 1 });
}

const N0_MASK: MaskConfig = { type: "numeric", pattern: "#,##0" };

// === Main Pivot Grid ===

// 행 합계 없음 · 열 총합계만 표시. 값 컬럼 기본 너비 100
const pivotCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "pivot",
  data: props.data,
  rowFields: [
    { field: "operGroupID", header: "공정 그룹", dataType: "string", width: 100 },
    { field: "operID", header: "공정", dataType: "string", width: 100 },
    { field: "itemID", header: "제품", dataType: "string", width: 120 },
    { field: "siteID", header: "사이트", dataType: "string", width: 80 },
    { field: "itemType", header: "제품 유형", dataType: "string", width: 80 },
    { field: "wipQty", header: "WIP 수량", dataType: "number" },
    { field: "pegQty", header: "Peg 수량", dataType: "number" },
    { field: "usedTotalQty", header: "사용 총량", dataType: "number" },
  ],
  columnFields: [
    { field: "planMonth", header: "계획월", dataType: "string" },
    { field: "planDate", header: "계획일", dataType: "string" },
  ],
  valueFields: [
    { field: "outPlanQty", header: "계획 산출량", dataType: "number", aggregate: "sum", width: 100, align: "right", mask: N0_MASK },
  ],
  showRowGrandTotals: false,
  showColumnGrandTotals: true,
  showZeros: false,
}));

// === Buffer Plan Target Pivot ===

const bufferPlanCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "pivot",
  data: props.bufferPlanTargetData,
  rowFields: [
    { field: "oper_group_id", header: "공정 그룹", dataType: "string", width: 100 },
    { field: "oper_id", header: "공정", dataType: "string", width: 100 },
    { field: "item_id", header: "제품", dataType: "string", width: 120 },
    { field: "plan_type", header: "계획 유형", dataType: "string", width: 80 },
  ],
  columnFields: [
    { field: "month", header: "월", dataType: "string" },
    { field: "date", header: "날짜", dataType: "string" },
  ],
  valueFields: [
    { field: "qty", header: "수량", dataType: "number", aggregate: "sum", width: 76, align: "right", mask: N0_MASK },
  ],
  showRowGrandTotals: false,
  showColumnGrandTotals: false,
  showZeros: false,
}));

// === Popup Grids ===

const demandInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.demandInfoData),
  fields: [
    { id: "demand_id", header: "수요 ID", dataType: "string", width: 120 },
    { id: "item_id", header: "제품 ID", dataType: "string", width: 120 },
    { id: "site_id", header: "사이트", dataType: "string", width: 80 },
    { id: "buffer_id", header: "버퍼", dataType: "string", width: 80 },
    { id: "demand_qty", header: "수요량", dataType: "number", width: 90, align: "right", mask: N0_MASK },
    { id: "due_date", header: "납기일", dataType: "string", width: 100 },
  ],
}));

const pegInfoCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.pegInfoData),
  fields: [
    { id: "wip_id", header: "WIP ID", dataType: "string", width: 120 },
    { id: "item_id", header: "제품 ID", dataType: "string", width: 120 },
    { id: "wip_qty", header: "WIP 수량", dataType: "number", width: 90, align: "right", mask: N0_MASK },
    { id: "peg_qty", header: "Peg 수량", dataType: "number", width: 90, align: "right", mask: N0_MASK },
    { id: "target_qty", header: "Target 수량", dataType: "number", width: 100, align: "right", mask: N0_MASK },
    { id: "site_id", header: "사이트", dataType: "string", width: 80 },
    { id: "buffer_id", header: "버퍼", dataType: "string", width: 80 },
    { id: "oper_id", header: "공정", dataType: "string", width: 80 },
    { id: "stage_id", header: "스테이지", dataType: "string", width: 90 },
    { id: "routing_id", header: "라우팅", dataType: "string", width: 100 },
    { id: "pegging_key", header: "Pegging Key", dataType: "string", width: 120 },
  ],
}));

// === Demand ID Change → Open Modals ===

function openPegInfo() {
  if (!props.demandId) return;
  emit("load-demand-info", props.demandId);
  emit("load-peg-info", props.demandId);
  pegInfoPopupVisible.value = true;
}

function openBufferPlanTarget() {
  if (!props.demandId) return;
  emit("load-buffer-plan-target", props.demandId);
  bufferPlanPopupVisible.value = true;
}

// Expose for potential parent usage
defineExpose({ openPegInfo, openBufferPlanTarget });
</script>

<style scoped lang="scss">
.rtf-report-prod-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.summary-bar-container {
  display: flex;
  justify-content: space-between;
}
// Demand Summary Bar
.summary-bar {
  // display: flex;
  // align-items: center;
  // gap: 8px;
  // padding: 6px 12px;
  // background: var(--color-bg-100, #f9fafb);
  // font-size: 13px;
  // min-height: 36px;
  // flex-shrink: 0;

  // &.summary-bar-empty {
  //   justify-content: space-between;
  // }
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  height: 29px;
  margin-bottom: 10px;

  line-height: 16px;
    margin-right: auto;
    font-size: 12px;
    border: 1px solid #bbc6d9;
    border-radius: 4px;
    padding: 6px 10px;
    background-color: #f8f9fd;

    font-weight: 400;
}

.summary-placeholder {
  color: var(--color-text-350, #9ca3af);
  font-style: italic;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.summary-label {
  color: var(--color-text-350, #6b7280);
  font-weight: 500;
}

.summary-value {
  color: var(--color-text-500, #1f2937);
  font-weight: 600;
}

.divider {
  color: var(--color-text-200, #d1d5db);
}

.zoom-btn {
  margin-left: auto;
  width: 28px;
  height: 28px;
  border: 1px solid var(--color-grid-border, #e5e7eb);
  border-radius: 4px;
  background: var(--color-bg-primary, #fff);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--color-text-350, #6b7280);

  &:hover {
    background: var(--color-bg-hover, #f3f4f6);
  }
}

// Pivot Container
.pivot-container {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

// Popup Styles
.popup-content {
  width: 800px;
  max-width: 90vw;
}

.popup-section-title {
  font-size: 14px;
  font-weight: 600;
  margin: 12px 0 8px 0;
  color: var(--color-text-500, #1f2937);

  &:first-child {
    margin-top: 0;
  }
}

.popup-grid-wrapper {
  border: 1px solid var(--color-grid-border, #e5e7eb);
  border-radius: 4px;
  overflow: hidden;
}

.popup-grid-small {
  height: 160px;
}

.popup-grid-large {
  height: 320px;
}

.popup-pivot-wrapper {
  height: 450px;
  min-height: 350px;
}
</style>
