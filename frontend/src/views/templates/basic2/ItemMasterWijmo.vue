<template>
  <div class="item-master-page">
    <!-- APS Controller 스타일 헤더 -->
    <Controller
      :showFilterButton="true"
      :showPreset="false"
      :customNavis="['Item Master', 'Wijmo Grid']"
      :actions="controllerActions"
    >
      <!-- 검색 조건 필터 -->
      <template #filter>
        <div class="filter-form">
          <div class="filter-item">
            <label for="projectId">Project ID</label>
            <input
              id="projectId"
              v-model="searchParams.projectId"
              type="text"
              placeholder="Project ID"
              class="filter-input"
            />
          </div>
          <div class="filter-item">
            <label for="planVer">Plan Version</label>
            <input
              id="planVer"
              v-model="searchParams.planVer"
              type="text"
              placeholder="Plan Version"
              class="filter-input"
            />
          </div>
        </div>
      </template>
    </Controller>

    <!-- 결과 정보 -->
    <section class="result-info">
      <span v-if="count > 0">총 {{ count }}건</span>
      <span v-if="error" class="error-text">{{ error }}</span>
    </section>

    <!-- Wijmo 그리드 -->
    <section class="grid-section">
      <ExtendFlexGrid
        v-if="data.length > 0"
        name="itemMasterGrid"
        :itemsSource="data"
        :isReadOnly="true"
        :loading="loading"
        :initialized="onGridInitialized"
        height="100%"
        :useToolBox="true"
        :useExtendFooter="true"
      />
      <div v-else-if="loading" class="loading-state">로딩 중...</div>
      <div v-else class="empty-state">조회된 데이터가 없습니다.</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, ref, computed } from "vue";
import { ExtendFlexGrid } from "@vmscloud/moz-component";
import Controller from "@/components/layout/Controller.vue";
import { useItemMaster, type ItemMasterParams } from "./itemMaster";

// Item Master 컴포저블
const { data, loading, error, count, loadData } = useItemMaster();

// 검색 파라미터
const searchParams = reactive<ItemMasterParams>({
  projectId: "31C13202-5860-4123-8ACD-81C2373F1E73",
  planVer: "20251103-P-TEST",
});

// 그리드 참조
const flexGrid = ref<any>(null);

// Controller Action 버튼 정의
const controllerActions = computed(() => [
  {
    action: "Search" as const,
    loading: loading.value,
    click: handleSearch,
  },
]);

// 그리드 초기화 핸들러
function onGridInitialized(grid: any) {
  flexGrid.value = grid;

  // 컬럼 설정 (선택사항 - 자동 생성되지만 커스터마이징 가능)
  if (grid.columns) {
    // 불필요한 컬럼 숨기기
    const hiddenColumns = [
      "partition_key",
      "project_id",
      "plan_ver",
      "prop01",
      "prop02",
      "prop03",
      "prop04",
      "prop05",
      "prop06",
      "prop07",
      "prop08",
      "prop09",
      "prop10",
    ];
    grid.columns.forEach((col: any) => {
      if (hiddenColumns.includes(col.binding)) {
        col.visible = false;
      }
    });
  }
}

// 검색 실행
async function handleSearch() {
  await loadData(searchParams);
}

// 초기 로드
onMounted(() => {
  handleSearch();
});
</script>

<style scoped lang="scss">
.item-master-page {
  // APS Main.vue의 페이지 구조와 동일
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-form {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-text-400, #6b7280);
    white-space: nowrap;
  }
}

.filter-input {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--color-border-750, #d1d5db);
  border-radius: 0.25rem;
  font-size: 0.875rem;
  min-width: 220px;
  background-color: var(--color-bg-100, #fff);
  color: var(--color-text-900, #1f2937);

  &:focus {
    outline: none;
    border-color: var(--color-accent-400, #3b82f6);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }

  &::placeholder {
    color: var(--color-text-300, #9ca3af);
  }
}

.result-info {
  font-size: 0.875rem;
  color: var(--color-text-400, #6b7280);
  padding: 0 var(--size-content-padding, 20px);

  .error-text {
    color: var(--color-error, #ef4444);
    margin-left: 1rem;
  }
}

.grid-section {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  margin: 0 var(--size-content-padding, 20px);
  margin-bottom: var(--spacing-6, 10px);
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-text-300, #9ca3af);
  font-size: 0.875rem;
  border: 1px solid var(--color-border-750, #e5e7eb);
  border-radius: 0.5rem;
}
</style>
