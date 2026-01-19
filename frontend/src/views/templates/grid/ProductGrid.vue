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
      <ExtendFlexGrid
        name="productGrid"
        :dataKey="['id']"
        :itemsSource="data"
        :width="'100%'"
        :height="550"
        :useToolBox="true"
        :useToolBoxSetting="true"
        :useExtendFooter="true"
        :useSummaryFooter="true"
        :useSort="true"
        :isReadOnly="false"
        :loading="loading"
        :initialized="onGridInitialized"
      >
        <WjFlexGridColumn binding="id" header="ID" :width="60" :isReadOnly="true" />
        <WjFlexGridColumn binding="name" header="상품명" :width="150" />
        <WjFlexGridColumn binding="category" header="카테고리" :width="100" />
        <WjFlexGridColumn binding="price" header="가격" :width="120" format="n0" />
        <WjFlexGridColumn binding="stock" header="재고" :width="80" />
        <WjFlexGridColumn
          binding="manufacturer"
          header="제조사"
          :width="120"
        />
        <WjFlexGridColumn
          binding="releaseDate"
          header="출시일"
          :width="120"
          format="yyyy-MM-dd"
        />
        <WjFlexGridColumn binding="isActive" header="판매중" :width="70" />
      </ExtendFlexGrid>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useProductGrid } from "./productGrid";
import {
  ExtendFlexGrid,
  type ExtendGrid,
} from "@vmscloud/moz-ui-components";
import { WjFlexGridColumn } from "@grapecity/wijmo.vue2.grid";
import type { FlexGrid } from "@grapecity/wijmo.grid";

// 상품 그리드 컴포저블
const { data, loading, error, count, loadData } = useProductGrid();

// 그리드 초기화 핸들러
const onGridInitialized = (flexGrid: FlexGrid, extendGrid: ExtendGrid) => {
  console.log("그리드 초기화 완료", flexGrid, extendGrid);
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
