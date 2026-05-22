<template>
  <div class="rtf-report-page">
    <!-- Filter Section -->
    <Controller
      :navigations="navigations"
      showFilterButton
      :actions="[
        {
          action: 'Search',
          click: handleSearch,
          disabled: loading || !planVer,
        },
      ]"
    >
      <template #filter>
        <Radio
          v-model="summaryType"
          label="요약 유형"
          :items-source="summaryOptions"
          display-expr="label"
          value-expr="value"
          variant="boxed"
        />
        <MultiSelect
          v-if="summaryType === 'cust'"
          v-model="selectedCustomers"
          :items-source="customerSource"
          key-prop="cust_id"
          display-prop="cust_name"
          label="고객"
          header-format="{count:n0} CUSTOMERS"
          :use-filter="true"
          :use-select-all="true"
          @close="onCustomersClose"
        />
        <MultiSelect
          v-if="summaryType === 'itemGroup'"
          v-model="selectedItemGroups"
          :items-source="itemGroupSource"
          key-prop="item_group"
          display-prop="item_group"
          label="제품 그룹"
          header-format="{count:n0} GROUPS"
          :use-filter="true"
          :use-select-all="true"
          @close="onItemGroupsClose"
        />
        <MultiSelect
          v-if="summaryType === 'region'"
          v-model="selectedRegions"
          :items-source="regionSource"
          key-prop="value"
          display-prop="value"
          label="지역"
          header-format="{count:n0} REGIONS"
          :use-filter="true"
          :use-select-all="true"
          @close="onRegionsClose"
        />
        <MultiSelect
          v-if="summaryType === 'demandType'"
          v-model="selectedDemandTypes"
          :items-source="demandTypeSource"
          key-prop="value"
          display-prop="value"
          label="수요 유형"
          header-format="{count:n0} DEMAND TYPES"
          :use-filter="true"
          :use-select-all="true"
          @close="onDemandTypesClose"
        />
        <Select
          v-model="aggType"
          :items-source="aggTypeOptions"
          key-prop="value"
          display-prop="label"
          label="집계 유형"
        />
        <Select
          v-model="uomType"
          :items-source="qtyUOMSource"
          key-prop="value"
          display-prop="displayValue"
          label="수량 단위"
        />
        <Radio
          v-model="prodStatus"
          label="생산 상태"
          :items-source="prodStatusOptions"
          display-expr="label"
          value-expr="value"
          variant="boxed"
        />
      </template>
    </Controller>

    <!-- Main Content -->
    <section class="content-section">
      <!-- Empty State -->
      <div v-if="summaryData.length === 0 && !loading" class="empty-state">
        <EmptyState :is-read-only="true" />
      </div>

      <!-- SplitPane Layout -->
      <SplitPane
        v-else
        horizontal
        style="max-width: 100%"
        :class="{ 'hide-splitter': isZoomedDetail }"
      >
        <!-- 상단: 요약 + 상세 -->
        <Pane
          :size="`${isZoomedDetail ? 0 : 60}%`"
          :max-size="`${isZoomedDetail ? 0 : 70}%`"
          :min-size="`${isZoomedDetail ? 0 : 30}%`"
          v-show="!isZoomedDetail"
        >
          <SplitPane>
            <Pane size="38%" min-size="30%">
              <RtfReportSummary
                :data="summaryData"
                :summary-type="committedSummaryType"
                :agg-type="committedAggType"
                :loading="loading"
                @row-selected="handleSummaryRowSelect"
              />
            </Pane>
            <Pane size="62%" min-size="30%">
              <RtfReportDetail
                :data="detailData"
                :loading="detailLoading"
                :plan-ver="planVer"
                :uom-type="committedUomType"
                :prop-columns="propColumns"
                :short-data="shortData"
                :item-props-data="itemPropsData"
                :demand-record-data="demandRecordData"
                @demand-selected="handleDemandSelect"
                @load-short="(id: string) => loadShort(planVer, id)"
                @load-item-props="(id: string) => loadItemProps(planVer, id)"
                @load-demand-record="(id: string) => loadDemandRecord(planVer, id)"
              />
            </Pane>
          </SplitPane>
        </Pane>

        <!-- 하단: 생산 상세 -->
        <Pane
          :size="`${isZoomedDetail ? 100 : 40}%`"
          :max-size="`${isZoomedDetail ? 100 : 70}%`"
          :min-size="`${isZoomedDetail ? 100 : 20}%`"
        >
          <RtfReportProdDetail
            :data="prodDetailData"
            :loading="prodDetailLoading"
            :demand-summary-data="demandSummaryData"
            :demand-info-data="demandInfoData"
            :peg-info-data="pegInfoData"
            :bom-map-data="bomMapData"
            :buffer-plan-target-data="bufferPlanTargetData"
            :plan-ver="planVer"
            :demand-id="selectedDemandID"
            :uom-type="committedUomType"
            :is-zoomed="isZoomedDetail"
            @toggle-zoom="isZoomedDetail = !isZoomedDetail"
            @load-demand-info="(id: string) => loadDemandInfo(planVer, id)"
            @load-peg-info="(id: string) => loadPegInfo(planVer, id)"
            @load-bom-map="(id: string) => loadBomMap(planVer, id)"
            @load-buffer-plan-target="(id: string) => loadBufferPlanTarget(planVer, id)"
          />
        </Pane>
      </SplitPane>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import {
  Controller,
  Select,
  MultiSelect,
  Radio,
  EmptyState,
} from "@vmscloud/moz-ui-components";
import { SplitPane, Pane } from "@vmscloud/moz-ui-components";
import { useHostPlanCycle, useHostNavigations } from "@/composables/useHostStores";
import { useRtfReport } from "./rtfReport";
import RtfReportSummary from "./RtfReportSummary.vue";
import RtfReportDetail from "./RtfReportDetail.vue";
import RtfReportProdDetail from "./RtfReportProdDetail.vue";
import type { RtfSummaryData } from "./rtfReport";

// Host 데이터
const navigations = useHostNavigations(() => ["생산 계획", "RTF 현황 (이수페타시스)"]);
const { planVer } = useHostPlanCycle();

// Composable
const {
  // 필터 상태 (UI 바인딩)
  summaryType,
  aggType,
  uomType,
  qtyUOMSource,
  prodStatus,
  selectedCustomers,
  selectedItemGroups,
  selectedRegions,
  selectedDemandTypes,
  // 확정 조회조건 스냅샷
  committedSummaryType,
  committedAggType,
  committedUomType,
  // 필터 소스
  customerSource,
  itemGroupSource,
  regionSource,
  demandTypeSource,
  propColumns,
  // 데이터
  summaryData,
  detailData,
  shortData,
  prodDetailData,
  demandSummaryData,
  demandInfoData,
  pegInfoData,
  bomMapData,
  itemPropsData,
  demandRecordData,
  bufferPlanTargetData,
  // 선택
  selectedDemandID,
  // UI
  loading,
  detailLoading,
  prodDetailLoading,
  // 메서드
  commitFilters,
  loadFilters,
  loadSummary,
  loadDetail,
  loadShort,
  loadProdDetail,
  loadDemandSummary,
  loadDemandInfo,
  loadPegInfo,
  loadBomMap,
  loadItemProps,
  loadDemandRecord,
  loadBufferPlanTarget,
  reset,
} = useRtfReport();

// === 로컬 상태 ===
const isZoomedDetail = ref(false);

// === 정적 옵션 ===
const summaryOptions = [
  { value: "itemGroup", label: "제품 그룹" },
  { value: "cust", label: "고객" },
  { value: "region", label: "지역" },
  { value: "demandType", label: "수요 유형" },
];

const aggTypeOptions = [
  { value: "WEEK", label: "WEEK" },
  { value: "MONTH", label: "MONTH" },
];

const prodStatusOptions = [
  { value: "default", label: "전체" },
  { value: "on_time", label: "On-Time" },
  { value: "late", label: "Late" },
  { value: "short", label: "Short" },
];

// === 이벤트 핸들러 ===

async function handleSearch() {
  if (!planVer.value) return;
  commitFilters();
  reset();
  await loadSummary(planVer.value);
}

function handleSummaryRowSelect(item: RtfSummaryData) {
  if (!planVer.value) return;
  loadDetail(planVer.value, item);
}

function handleDemandSelect(demandID: string) {
  if (!planVer.value || !demandID) return;
  selectedDemandID.value = demandID;
  // 수요 선택 시 생산 상세 + 수요 요약 로드
  loadProdDetail(planVer.value, demandID);
  loadDemandSummary(planVer.value, [demandID]);
}

// MultiSelect close 핸들러 — 빈 상태면 전체 선택
function onCustomersClose() {
  if (selectedCustomers.value.length === 0) {
    selectedCustomers.value = customerSource.value.map((c) => c.cust_id);
  }
}
function onItemGroupsClose() {
  if (selectedItemGroups.value.length === 0) {
    selectedItemGroups.value = itemGroupSource.value.map((g) => g.item_group);
  }
}
function onRegionsClose() {
  if (selectedRegions.value.length === 0) {
    selectedRegions.value = regionSource.value.map((r) => r.value);
  }
}
function onDemandTypesClose() {
  if (selectedDemandTypes.value.length === 0) {
    selectedDemandTypes.value = demandTypeSource.value.map((d) => d.value);
  }
}

// === Lifecycle ===

onMounted(async () => {
  if (planVer.value) {
    await loadFilters(planVer.value);
    handleSearch();
  }
});

// planVer 변경 시 필터 재로드 + 자동 조회
watch(planVer, async (newVer) => {
  if (newVer) {
    reset();
    await loadFilters(newVer);
    handleSearch();
  }
});
</script>

<style scoped lang="scss">
.rtf-report-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.content-section {
  padding: 0 20px 20px 20px;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.hide-splitter :deep(.splitpanes__splitter) {
  display: none;
}
</style>
