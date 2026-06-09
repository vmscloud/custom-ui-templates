<template>
  <div class="production-chart-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="page-header-top">
        <h1 class="page-title">공정별 생산량</h1>
        <span v-if="planVer" class="plan-ver-badge">계획 버전 · {{ planVer }}</span>
      </div>
      <p class="page-description">선택한 계획 버전 기준, 공정별 계획 대비 실적 생산량을 비교합니다.</p>
    </div>

    <!-- 차트 영역 -->
    <section class="chart-section">
      <div v-if="loading" class="loading-state">로딩 중...</div>
      <div v-else-if="error" class="error-state">{{ error }}</div>
      <div v-else style="width: 100%; height: 100%;">
        <EChart
          id="production-by-process-chart"
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
import { ref, onMounted, watch } from "vue";
import { useProductionByProcess } from "./productionByProcess";
import { useHostPlanCycle } from "@/composables/useHostStores";
import {
  EChart,
  DataType,
  Aggregate,
  type MozEChart,
  type ViewDef,
  type FilterDef,
  type ChartField,
} from "@vmscloud/moz-ui-chart";

// 공정별 생산량 차트 컴포저블
const { data, loading, error, loadData } = useProductionByProcess();

// Host(APS)가 주입한 현재 계획 버전
const { planVer } = useHostPlanCycle();

// ViewDef 설정
const viewDef = ref<ViewDef>({
  fields: [
    { binding: "process", header: "공정", dataType: DataType.String },
    { binding: "planQty", header: "계획수량", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "actualQty", header: "실적수량", dataType: DataType.Number, aggregate: Aggregate.Sum },
  ] as ChartField[],
  rowFields: [],
  columnFields: [{ binding: "process", header: "공정", dataType: DataType.String }],
  valueFields: [
    { binding: "planQty", header: "계획수량", dataType: DataType.Number, aggregate: Aggregate.Sum },
    { binding: "actualQty", header: "실적수량", dataType: DataType.Number, aggregate: Aggregate.Sum },
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

// 계획 버전이 바뀌면 해당 버전 기준으로 데이터 갱신
watch(planVer, () => {
  loadData();
});
</script>

<style scoped lang="scss">
.production-chart-page {
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 1.5rem;

  .page-header-top {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .page-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--color-text-primary, #1f2937);
    margin: 0;
  }

  .plan-ver-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    background: var(--color-badge-100, #eef1fc);
    color: var(--color-badge-800, #4568e0);
    font-size: 0.8125rem;
    font-weight: 500;
    white-space: nowrap;
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
