<template>
  <div class="demand-distribution-page">
    <!-- Filter Section -->
    <Controller
      :navigations="navigations"
      showFilterButton
      :actions="[
        {
          action: 'Search',
          click: handleSearch,
          disabled: loading || !selectedDemandVer,
        },
      ]"
    >
      <template #filter>
        <Select
          v-model="selectedDemandVer"
          :items-source="demandVersions as any[]"
          key-prop="demand_ver"
          display-prop="display_text"
          placeholder="Select Demand Version"
          label="수요 정보 버전"
          :width="260"
        />
        <Select
          v-model="aggregateType"
          :items-source="aggregateOptions"
          key-prop="value"
          display-prop="label"
          label="집계 기준"
        />
        <Radio
          v-model="summary"
          :items-source="summaryOptions"
          display-expr="label"
          value-expr="value"
          label="요약"
          variant="boxed"
          :width="160"
        />
        <Select
          v-model="uomType"
          :items-source="qtyUOMSource"
          key-prop="value"
          display-prop="displayValue"
          label="수량 단위"
        />
        <MultiSelect
          v-model="selectedColumns"
          :items-source="columnsSource"
          key-prop="columnName"
          display-prop="displayText"
          :placeholder="columnsSource.length === 0 ? 'No columns' : ''"
          label="컬럼 선택"
          header-format="{count:n0} COLUMNS"
          @close="onColumnsClose"
        />
      </template>
    </Controller>
    <!-- Main Content Area -->
    <section class="content-section">
      <!-- Empty State -->
      <div v-if="visibleState === 'empty'" class="empty-state">
        <EmptyState :is-read-only="true" />
      </div>

      <!-- Content -->
      <div v-else class="demand-distribution-container">
        <div v-for="(col, idx) in propColumns" :key="col.columnName">
          <DemandDistributionSub
            v-show="selectedColumns.includes(col.columnName)"
            :is-loading="loading"
            :display-name="col.displayText"
            :column="col.columnName"
            :unit="col.category"
            :idx="idx"
            :data="getFilteredData(col.columnName)"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import {
  Select,
  MultiSelect,
  Radio,
  EmptyState,
  Controller,
} from "@vmscloud/moz-ui-components";
import { useHostNavigations } from "@/composables/useHostStores";
import { useDemandDistribution } from "./demandDistribution";
import type { DemandDistributionData } from "./demandDistribution";
import DemandDistributionSub from "./DemandDistributionSub.vue";

const navigations = useHostNavigations(() => ["수요 관리", "수요 분포 현황"]);

// Demand Distribution composable
const {
  data,
  headers,
  demandVersions,
  columnMetadata,
  loading,
  selectedDemandVer,
  aggregateType,
  summary,
  uomType,
  qtyUOMSource,
  selectedColumns,
  loadDemandVersions,
  loadColumnMetadata,
  loadData,
} = useDemandDistribution();

// Aggregate type options
const aggregateOptions = ref([
  { value: "WEEK", label: "WEEK" },
  { value: "MONTH", label: "MONTH" },
  { value: "YEAR", label: "YEAR" },
]);

// Summary type options
const summaryOptions = ref([
  { value: "sum", label: "Demand Qty" },
  { value: "count", label: "Item Count" },
]);

// Column options source
const columnsSource = ref<
  { columnName: string; displayText: string; category: string | null }[]
>([]);

// Prop columns (from API response headers)
const propColumns = ref<
  { columnName: string; displayText: string; category: string | null }[]
>([]);

// Visible state
const visibleState = computed(() => {
  if (loading.value) return "loading";
  if (data.value.length > 0) return "content";
  return "empty";
});

// Handle search
async function handleSearch() {
  if (!selectedDemandVer.value) return;

  // Pre-mount sub-components before loading so data flows reactively (fixes first search)
  if (propColumns.value.length === 0 && columnsSource.value.length > 0) {
    propColumns.value = columnsSource.value.map((c) => ({
      columnName: c.columnName,
      displayText: c.displayText,
      category: c.category ?? null,
    }));
  }

  await loadData();

  if (data.value.length > 0 && headers.value.length > 0) {
    // headers의 displayText를 columnsSource의 friendly name으로 매핑
    propColumns.value = headers.value.map((h) => {
      const source = columnsSource.value.find(
        (c) => c.columnName === h.columnName,
      );
      return {
        columnName: h.columnName,
        displayText: source?.displayText ?? h.displayText,
        category: h.category,
      };
    });
  }
}

// Handle columns close - ensure at least one column is selected
function onColumnsClose() {
  if (selectedColumns.value.length === 0 && columnsSource.value.length > 0) {
    selectedColumns.value = [columnsSource.value[0].columnName];
  }
}

// Filter data by column
function getFilteredData(columnName: string): DemandDistributionData[] {
  return data.value.filter((d) => d[columnName] != null);
}

// Initialize columns source from API
async function initColumnsSource() {
  await loadColumnMetadata();

  // API 응답이 있으면 사용, 없으면 기본값
  if (columnMetadata.value.length > 0) {
    columnsSource.value = columnMetadata.value.map((c) => ({
      columnName: c.columnName,
      displayText: c.displayText,
      category: c.category,
    }));
  } else {
    columnsSource.value = [
      { columnName: "cust_id", displayText: "Customer", category: null },
      { columnName: "item_group_id", displayText: "Item Group", category: null },
      { columnName: "prod_type", displayText: "Prod Type", category: null },
      { columnName: "item_size_type", displayText: "Item Size Type", category: null },
    ];
  }

  // Set default selected column
  if (selectedColumns.value.length === 0 && columnsSource.value.length > 0) {
    selectedColumns.value = [columnsSource.value[0].columnName];
  }
}

// Lifecycle
onMounted(async () => {
  await loadDemandVersions();
  await initColumnsSource();

  // Auto select first demand version if available
  if (demandVersions.value.length > 0 && !selectedDemandVer.value) {
    selectedDemandVer.value = demandVersions.value[0].demand_ver;
  }
});

// Removed auto-load on demand version selection to prevent EChart renderer issues
// User should click Search button to load data
</script>

<style scoped lang="scss">
.demand-distribution-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.content-section {
  padding: 0 11px 20px 20px;
  flex: 1;
  overflow-y: scroll;
  position: relative;
}

.demand-distribution-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: visible;
  //height: 100%;
}

.loading-state {
  position: relative;
  height: 100%;
  min-height: 300px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}
</style>
