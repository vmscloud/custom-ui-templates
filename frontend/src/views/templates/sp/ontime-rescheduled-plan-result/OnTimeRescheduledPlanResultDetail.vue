<template>
  <div class="ontime-replan-detail">
    <!-- Demand Summary Bar -->
    <div class="summary-bar-container">
      <div v-if="demandSummaryData.length > 0" class="summary-bar">
        <div class="summary-item">
          <span class="summary-label">수요량</span>
          <span class="summary-value">{{ formatQty(demandSummaryData[0]?.demand_qty) }}</span>
        </div>
        <span class="divider">|</span>
        <div class="summary-item">
          <span class="summary-label">출하량</span>
          <span class="summary-value">{{ formatQty(demandSummaryData[0]?.shipment_qty) }}</span>
        </div>
        <span class="divider">|</span>
        <div class="summary-item">
          <span class="summary-label">WIP</span>
          <span class="summary-value">{{ formatQty(demandSummaryData[0]?.wip_qty) }}</span>
        </div>
        <span class="divider">|</span>
        <div class="summary-item">
          <span class="summary-label">Peg</span>
          <span class="summary-value">
            {{ formatQty(demandSummaryData[0]?.peg_qty) }}
            ({{ formatRatio(demandSummaryData[0]?.peg_ratio) }}%)
          </span>
        </div>
        <span class="divider">|</span>
        <div class="summary-item">
          <span class="summary-label">입고일</span>
          <span class="summary-value">{{ demandSummaryData[0]?.warehousing_date || "-" }}</span>
        </div>
        <span class="divider">|</span>
        <div class="summary-item">
          <span class="summary-label">출하일</span>
          <span class="summary-value">{{ demandSummaryData[0]?.shipment_date || "-" }}</span>
        </div>
      </div>

      <div v-else class="summary-bar summary-bar-empty">
        <span class="summary-placeholder">수요를 선택하면 요약 정보가 표시됩니다</span>
      </div>

      <!-- Zoom Toggle -->
      <button
        class="zoom-btn"
        :title="isZoomed ? '축소' : '확대'"
        @click="emit('toggle-zoom')"
      >
        {{ isZoomed ? "▼" : "▲" }}
      </button>
    </div>

    <!-- Production Plan Grid (simplified from PivotGrid) -->
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
        <WjFlexGridColumn binding="oper_group_id" header="공정 그룹" :width="120" />
        <WjFlexGridColumn binding="item_id" header="제품 ID" :width="120" />
        <WjFlexGridColumn binding="total_prod_qty" header="사용 합계" align="right" :width="100" />
        <WjFlexGridColumn binding="oper_id" header="공정 ID" :width="100" :visible="false" />
        <WjFlexGridColumn binding="site_id" header="사이트" :width="80" :visible="false" />
        <WjFlexGridColumn binding="item_type" header="제품 유형" :width="90" :visible="false" />
        <WjFlexGridColumn binding="wip_qty" header="WIP 수량" dataType="Number" align="right" :width="90" format="n0" :visible="false" />
        <WjFlexGridColumn binding="peg_qty" header="Peg 수량" dataType="Number" align="right" :width="90" format="n0" :visible="false" />
        <WjFlexGridColumn binding="prod_qty" header="생산 수량" dataType="Number" align="right" :width="100" format="n2" />
        <WjFlexGridColumn binding="plan_date" header="계획일" :width="100" align="center" />
        <WjFlexGridColumn binding="plan_month" header="계획 월" :width="90" align="center" />
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
      title="수요 정보"
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
        <WjFlexGridColumn binding="demand_id" header="수요 ID" :width="120" />
        <WjFlexGridColumn binding="item_id" header="제품 ID" :width="120" />
        <WjFlexGridColumn binding="cust_id" header="고객" :width="100" />
        <WjFlexGridColumn binding="due_date" header="납기일" :width="110" />
        <WjFlexGridColumn binding="demand_qty" header="수요량" :width="90" align="right" format="n0" />
      </ExtendFlexGrid>
    </Popup>

    <!-- Peg Info Popup -->
    <Popup
      v-model:visible="pegInfoPopupVisible"
      title="Peg 정보 상세"
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
        <WjFlexGridColumn binding="demand_id" header="수요 ID" :width="120" />
        <WjFlexGridColumn binding="item_id" header="제품 ID" :width="120" />
        <WjFlexGridColumn binding="peg_qty" header="Peg 수량" :width="90" align="right" format="n0" />
        <WjFlexGridColumn binding="plan_date" header="계획일" :width="110" />
      </ExtendFlexGrid>
    </Popup>

    <!-- BOM Map Popup -->
    <Popup
      v-model:visible="bomMapPopupVisible"
      title="BOM 구조"
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
        <WjFlexGridColumn binding="item_id" header="제품 ID" :width="120" />
        <WjFlexGridColumn binding="bom_id" header="BOM ID" :width="120" />
        <WjFlexGridColumn binding="routing_id" header="라우팅 ID" :width="120" />
        <WjFlexGridColumn binding="oper_id" header="공정 ID" :width="100" />
        <WjFlexGridColumn binding="qty" header="수량" :width="90" align="right" format="n0" />
      </ExtendFlexGrid>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { type FlexGrid, CellType } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { Popup } from "@vmscloud/moz-ui-components";
import type {
  ProdDetailResponse,
  DemandSummaryData,
} from "./onTimeRescheduledPlanResult";

// === Props & Emits ===

interface Props {
  data: ProdDetailResponse | null;
  demandSummaryData: DemandSummaryData[];
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
  (e: "toggle-zoom"): void;
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

function formatQty(value: number | undefined | null): string {
  if (value == null || isNaN(value)) return "-";
  return value.toLocaleString();
}

function formatRatio(value: number | undefined | null): string {
  if (value == null || isNaN(value)) return "0";
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

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

.summary-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-bar {
  flex: 1;
  line-height: 16px;
  font-size: 12px;
  border: 1px solid #bbc6d9;
  border-radius: 4px;
  padding: 6px 10px;
  background-color: #f8f9fd;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.summary-bar-empty {
  color: #8998b5;
}

.summary-placeholder {
  font-style: italic;
}

.summary-item {
  display: inline-flex;
  gap: 4px;
}

.summary-label {
  color: #6a7184;
  font-weight: 500;
}

.summary-value {
  color: #28364e;
}

.divider {
  color: #bbc6d9;
  padding: 0 4px;
}

.zoom-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid #bbc6d9;
  border-radius: 4px;
  background: #fff;
  font-size: 12px;
  color: #6a7184;
  flex-shrink: 0;

  &:hover {
    background-color: #4568e017;
    color: #4568e0;
  }
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
