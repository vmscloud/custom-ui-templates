<template>
  <div class="sales-chart-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">월별 매출 차트</h1>
      <p class="page-description">월별 매출, 수익, 비용을 차트로 확인합니다.</p>
    </div>

    <!-- 차트 영역 -->
    <section class="chart-section">
      <div v-if="loading" class="loading-state">로딩 중...</div>
      <div v-else-if="error" class="error-state">{{ error }}</div>
      <div v-else style="width: 100%; height: 100%;">
        <EChart
          id="sales-chart"
          :items-source="data"
          v-model:view-def="viewDef"
          v-model:filter-def="filterDef"
          v-model:chart-def="chartDef"
          :on-initialized="handleInitialized"
          :use-tool-box="true"
          :use-chart-setting="true"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSalesChart } from "./salesChart";
import {
  EChart,
  DataType,
  Aggregate,
  type MozEChart,
  type ViewDef,
  type FilterDef,
  type ChartField,
} from "@vmscloud/moz-ui-components";

// 매출 차트 컴포저블
const { data, loading, error, loadData } = useSalesChart();

// ViewDef 설정
const viewDef = ref<ViewDef>({
  fields: [
    { binding: "month", header: "월", dataType: DataType.String },
    { binding: "sales", header: "매출", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "profit", header: "수익", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "cost", header: "비용", dataType: DataType.Number, aggregate: Aggregate.Sum },
  ] as ChartField[],
  rowFields: [],
  columnFields: [{ binding: "month", header: "월", dataType: DataType.String }],
  valueFields: [
    { binding: "sales", header: "매출", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "profit", header: "수익", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "cost", header: "비용", dataType: DataType.Number, aggregate: Aggregate.Sum },
  ],
});

// FilterDef 설정
const filterDef = ref<FilterDef[]>([]);

// ChartDef 설정
const chartDef = ref({});

// 차트 초기화 핸들러
const handleInitialized = (mozEChart: MozEChart) => {
  mozEChart.category = "series";
  mozEChart.type = "bar";
  console.log("차트 초기화 완료");
};

// 초기 로드
onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.sales-chart-page {
  padding: 1.5rem;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 1.5rem;

  .page-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--color-text-primary, #1f2937);
    margin: 0 0 0.5rem 0;
  }

  .page-description {
    color: var(--color-text-secondary, #6b7280);
    margin: 0;
  }
}

.chart-section {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background: white;
  display: flex;
}

.loading-state,
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--color-text-secondary, #9ca3af);
  font-size: 0.875rem;
}

.error-state {
  color: var(--color-error, #ef4444);
}
</style>
