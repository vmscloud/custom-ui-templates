<template>
  <div class="product-grid-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">상품 관리</h1>
      <p class="page-description">상품 목록을 조회하고 관리합니다.</p>
    </div>

    <!-- 결과 정보 -->
    <section class="result-info">
      <span v-if="count > 0">총 {{ count }}건</span>
      <span v-if="error" class="error-text">{{ error }}</span>
    </section>

    <!-- 그리드 영역 -->
    <section class="grid-section">
      <MozGrid
        name="productGrid"
        :coreConfig="coreConfig"
        :height="550"
        :useSummaryFooter="true"
        :loading="loading"
        @ready="onGridReady"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useProductGrid } from "./productGrid";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { GridChrome, MozGridCoreProps, PureSheet } from "@vmscloud/moz-ui-grid-vue";

// 상품 그리드 컴포저블
const { data, loading, error, count, loadData } = useProductGrid();

// 그리드 설정 — 컬럼은 fields, 행 식별자는 keyFields 로 선언한다.
const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["id"],
  editable: true,
  data: data.value,
  fields: [
    { id: "id", header: "ID", dataType: "number", width: 60, readonly: true },
    { id: "name", header: "상품명", dataType: "string", width: 150 },
    { id: "category", header: "카테고리", dataType: "string", width: 100 },
    { id: "price", header: "가격", dataType: "number", width: 120, mask: { type: "numeric", pattern: "#,##0" } },
    { id: "stock", header: "재고", dataType: "number", width: 80 },
    { id: "manufacturer", header: "제조사", dataType: "string", width: 120 },
    { id: "releaseDate", header: "출시일", dataType: "date", width: 120, mask: { type: "date", pattern: "YYYY-MM-DD" } },
    { id: "isActive", header: "판매중", dataType: "boolean", width: 70 },
  ],
}));

// 그리드 준비 완료 핸들러 — 코어 그리드(PureSheet)와 래퍼(GridChrome)를 받는다.
const onGridReady = (grid: PureSheet, chrome: GridChrome) => {
  console.log("그리드 초기화 완료", grid, chrome);
};

// 초기 로드
onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.product-grid-page {
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  margin-bottom: 1rem;

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

.result-info {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);

  .error-text {
    color: var(--color-error, #ef4444);
    margin-left: 1rem;
  }
}

.grid-section {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
</style>
