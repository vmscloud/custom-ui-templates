<template>
  <div class="demand-distribution-page">
    <!-- Filter Section -->
    <Controller :navigations="['수요 관리', '수요 분포 현황']" showFilterButton :actions="[{
      'action': 'Search',
      'click': handleSearch,
      'disabled': loading || !selectedDemandVer
    }]" >
      <template #filter>
        <Select
            v-model="selectedDemandVer"
            :items-source="demandVersions as any[]"
            key-prop="demand_ver"
            display-prop="display_text"
            placeholder="Select Demand Version"
            label="Demand Version"
            :width="260"
          />
          <Select
            v-model="aggregateType"
            :items-source="aggregateOptions"
            key-prop="value"
            display-prop="label"
            label="Aggregate Type"
          />
          <Radio
            v-model="summary"
            :items-source="summaryOptions"
            display-expr="label"
            value-expr="value"
            label="Summary Type"
            variant="boxed"
            :width="160"
            :style="{ marginTop: '-4px'}"
          />
          <Select
            v-model="uomType"
            :items-source="uomOptions"
            key-prop="value"
            display-prop="label"
            label="Qty UOM"
          />
          <MultiSelect
            v-model="selectedColumns"
            :items-source="columnsSource"
            key-prop="columnName"
            display-prop="displayText"
            :placeholder="columnsSource.length === 0 ? 'No columns' : ''"
            label="Columns"
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
import { ref, computed, onMounted, watch } from "vue";
import {
  Select,
  MultiSelect,
  Radio,
  EmptyState,
  Controller,
} from "@vmscloud/moz-ui-components";
import { useDemandDistribution } from "./demandDistribution";
import type { DemandDistributionData } from "./demandDistribution";
import { useHostStores } from "@/composables/useHostStores";
import DemandDistributionSub from "./DemandDistributionSub.vue";

// Host stores for project info
const hostStores = useHostStores();
const projectId = computed(
  () => hostStores.projectInfo.currentProjectID.value || ""
);

// Demand Distribution composable
const {
  data,
  headers,
  demandVersions,
  loading,
  selectedDemandVer,
  aggregateType,
  summary,
  uomType,
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

// UOM type options
const uomOptions = ref([
  { value: "DEFAULT", label: "DEFAULT" },
  { value: "CONVERSION", label: "CONVERSION" },
]);

// Column options source
const columnsSource = ref<{ columnName: string; displayText: string; category: string | null }[]>([]);

// Prop columns (from API response headers)
const propColumns = ref<{ columnName: string; displayText: string; category: string | null }[]>([]);

// Visible state
const visibleState = computed(() => {
  if (loading.value) return "loading";
  if (data.value.length > 0) return "content";
  return "empty";
});

// Handle search
async function handleSearch() {
  if (!projectId.value || !selectedDemandVer.value) return;

  await loadData(projectId.value);

  if (data.value.length > 0 && headers.value.length > 0) {
    // Update prop columns from response headers
    propColumns.value = headers.value.map((h) => ({
      columnName: h.columnName,
      displayText: h.displayText,
      category: h.category,
    }));
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

// Initialize columns source
async function initColumnsSource() {
  // Load column metadata from API
  await loadColumnMetadata(projectId.value);

  // Set default columns
  columnsSource.value = [
    { columnName: "cust_id", displayText: "Customer", category: "fixed" },
    { columnName: "item_group_id", displayText: "Item Group", category: "fixed" },
    { columnName: "prod_type", displayText: "Prod Type", category: "fixed" },
    { columnName: "item_size_type", displayText: "Item Size Type", category: "fixed" },
  ];

  // Set default selected column
  if (selectedColumns.value.length === 0 && columnsSource.value.length > 0) {
    selectedColumns.value = [columnsSource.value[0].columnName];
  }
}

// Lifecycle
onMounted(async () => {
  if (projectId.value) {
    await loadDemandVersions(projectId.value);
    await initColumnsSource();

    // Auto select first demand version if available
    if (demandVersions.value.length > 0 && !selectedDemandVer.value) {
      selectedDemandVer.value = demandVersions.value[0].demand_ver;
    }
  }
});

// Watch for project changes
watch(projectId, async (newVal) => {
  if (newVal) {
    await loadDemandVersions(newVal);
    await initColumnsSource();
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
  padding: 0 6px 20px 20px;
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
