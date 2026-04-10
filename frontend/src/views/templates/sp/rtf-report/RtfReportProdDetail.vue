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
      <ExtendPivotGrid
        ref="extendPivotGridRef"
        :emptyState="{ isLoading: loading, isReadOnly: !loading && (!data || data.length === 0) }"
        name="rtfProdDetailPivot"
        height="100%"
        :itemsSource="data"
        :engine-option="{
          fields: pivotFields,
          rowFields: rowFieldNames,
          columnFields: columnFieldNames,
          valueFields: valueFieldNames,
          showRowTotals: showTotalsNone,
          showColumnTotals: showTotalsGrand,
          showZeros: false,
          totalsBeforeData: false,
        }"
        :useContextMenu="false"
        :initialized="onInitialized"
        :use-pivot-chart="false"
        :use-tool-box="true"
        :loading="!data || data.length === 0"
      />
    </div>

    <!-- Peg Info Popup -->
    <Popup v-model:visible="pegInfoPopupVisible" title="Peg 정보 상세">
      <template #default>
        <div class="popup-content">
          <!-- Demand Info Section -->
          <h4 class="popup-section-title">수요 정보</h4>
          <div class="popup-grid-wrapper popup-grid-small">
            <ExtendFlexGrid
              name="rtfDemandInfoGrid"
              :itemsSource="demandInfoData"
              height="100%"
              :isReadOnly="true"
              :use-tool-box="false"
            >
              <WjFlexGridColumn binding="demand_id" header="수요 ID" :width="120" />
              <WjFlexGridColumn binding="item_id" header="제품 ID" :width="120" />
              <WjFlexGridColumn binding="site_id" header="사이트" :width="80" />
              <WjFlexGridColumn binding="buffer_id" header="버퍼" :width="80" />
              <WjFlexGridColumn binding="demand_qty" header="수요량" :width="90" align="right" format="n0" />
              <WjFlexGridColumn binding="due_date" header="납기일" :width="100" />
            </ExtendFlexGrid>
          </div>

          <!-- Peg Info Detail Section -->
          <h4 class="popup-section-title">Peg 상세</h4>
          <div class="popup-grid-wrapper popup-grid-large">
            <ExtendFlexGrid
              name="rtfPegInfoDetailGrid"
              :itemsSource="pegInfoData"
              height="100%"
              :isReadOnly="true"
              :use-tool-box="false"
            >
              <WjFlexGridColumn binding="wip_id" header="WIP ID" :width="120" />
              <WjFlexGridColumn binding="item_id" header="제품 ID" :width="120" />
              <WjFlexGridColumn binding="wip_qty" header="WIP 수량" :width="90" align="right" format="n0" />
              <WjFlexGridColumn binding="peg_qty" header="Peg 수량" :width="90" align="right" format="n0" />
              <WjFlexGridColumn binding="target_qty" header="Target 수량" :width="100" align="right" format="n0" />
              <WjFlexGridColumn binding="site_id" header="사이트" :width="80" />
              <WjFlexGridColumn binding="buffer_id" header="버퍼" :width="80" />
              <WjFlexGridColumn binding="oper_id" header="공정" :width="80" />
              <WjFlexGridColumn binding="stage_id" header="스테이지" :width="90" />
              <WjFlexGridColumn binding="routing_id" header="라우팅" :width="100" />
              <WjFlexGridColumn binding="pegging_key" header="Pegging Key" :width="120" />
            </ExtendFlexGrid>
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
            <ExtendPivotGrid
              name="rtfBufferPlanTargetPivot"
              height="100%"
              :itemsSource="bufferPlanTargetData"
              :engine-option="{
                fields: bufferPlanFields,
                rowFields: bufferPlanRowFieldNames,
                columnFields: bufferPlanColumnFieldNames,
                valueFields: bufferPlanValueFieldNames,
                showRowTotals: showTotalsNone,
                showColumnTotals: showTotalsNone,
                showZeros: false,
                totalsBeforeData: false,
              }"
              :useContextMenu="false"
              :use-pivot-chart="false"
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
import {
  ExtendFlexGrid,
  ExtendPivotGrid,
  type ExtendGrid,
} from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { Aggregate, DataType } from "@vmscloud/moz-wijmo-grid/wijmo";
import { type PivotGrid, ShowTotals } from "@vmscloud/moz-wijmo-grid/wijmo.olap";
import { Popup, Button } from "@vmscloud/moz-ui-components";
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

const extendPivotGridRef = ref<InstanceType<typeof ExtendPivotGrid> | null>(null);
const pegInfoPopupVisible = ref(false);
const bufferPlanPopupVisible = ref(false);

// ShowTotals constants
const showTotalsNone = ShowTotals.None;
const showTotalsGrand = ShowTotals.GrandTotals;

// === Formatting Helpers ===

function formatQty(val: any): string {
  if (val == null) return "-";
  return Number(val).toLocaleString();
}

function formatRatio(val: any): string {
  if (val == null) return "0";
  return Number(val).toLocaleString(undefined, { maximumFractionDigits: 1 });
}

// === Main Pivot Grid Fields ===

const pivotFields = computed(() => [
  {
    binding: "operGroupID",
    header: "공정 그룹",
    dataType: DataType.String,
    align: "left" as const,
    width: 100,
  },
  {
    binding: "operID",
    header: "공정",
    dataType: DataType.String,
    align: "left" as const,
    width: 100,
  },
  {
    binding: "itemID",
    header: "제품",
    dataType: DataType.String,
    align: "left" as const,
    width: 120,
  },
  {
    binding: "siteID",
    header: "사이트",
    dataType: DataType.String,
    align: "left" as const,
    width: 80,
  },
  {
    binding: "itemType",
    header: "제품 유형",
    dataType: DataType.String,
    align: "left" as const,
    width: 80,
  },
  {
    binding: "wipQty",
    header: "WIP 수량",
    dataType: DataType.Number,
    align: "right" as const,
    aggregate: Aggregate.Sum,
  },
  {
    binding: "pegQty",
    header: "Peg 수량",
    dataType: DataType.Number,
    align: "right" as const,
    aggregate: Aggregate.Sum,
  },
  {
    binding: "usedTotalQty",
    header: "사용 총량",
    dataType: DataType.Number,
    align: "right" as const,
    aggregate: Aggregate.Sum,
  },
  {
    binding: "outPlanQty",
    header: "계획 산출량",
    dataType: DataType.Number,
    align: "right" as const,
    width: 76,
    aggregate: Aggregate.Sum,
  },
  {
    binding: "planDate",
    header: "계획일",
    dataType: DataType.String,
    align: "right" as const,
    width: 76,
  },
  {
    binding: "planMonth",
    header: "계획월",
    dataType: DataType.String,
    align: "right" as const,
    width: 76,
  },
]);

const rowFieldNames = [
  "공정 그룹",
  "공정",
  "제품",
  "사이트",
  "제품 유형",
  "WIP 수량",
  "Peg 수량",
  "사용 총량",
];
const columnFieldNames = ["계획월", "계획일"];
const valueFieldNames = ["계획 산출량"];

// === Buffer Plan Target Pivot Fields ===

const bufferPlanFields = computed(() => [
  {
    binding: "oper_group_id",
    header: "공정 그룹",
    dataType: DataType.String,
    align: "left" as const,
    width: 100,
  },
  {
    binding: "oper_id",
    header: "공정",
    dataType: DataType.String,
    align: "left" as const,
    width: 100,
  },
  {
    binding: "item_id",
    header: "제품",
    dataType: DataType.String,
    align: "left" as const,
    width: 120,
  },
  {
    binding: "plan_type",
    header: "계획 유형",
    dataType: DataType.String,
    align: "left" as const,
    width: 80,
  },
  {
    binding: "qty",
    header: "수량",
    dataType: DataType.Number,
    align: "right" as const,
    width: 76,
    aggregate: Aggregate.Sum,
  },
  {
    binding: "date",
    header: "날짜",
    dataType: DataType.String,
    align: "right" as const,
    width: 76,
  },
  {
    binding: "month",
    header: "월",
    dataType: DataType.String,
    align: "right" as const,
    width: 76,
  },
]);

const bufferPlanRowFieldNames = ["공정 그룹", "공정", "제품", "계획 유형"];
const bufferPlanColumnFieldNames = ["월", "날짜"];
const bufferPlanValueFieldNames = ["수량"];

// === Grid Initialization ===

function onInitialized(pivotGrid: PivotGrid, _extendGrid: ExtendGrid) {
  // Set default column width
  pivotGrid.columns.defaultSize = 100;
}

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
