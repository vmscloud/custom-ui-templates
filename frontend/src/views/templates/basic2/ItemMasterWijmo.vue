<template>
  <div class="item-master-page">
    <!-- 검색 조건 (APS 컨트롤러 스타일) -->
    <section class="search-section">
      <div class="search-form">
        <div class="form-group">
          <label for="projectId">Project ID</label>
          <input
            id="projectId"
            v-model="searchParams.projectId"
            type="text"
            placeholder="Project ID"
          />
        </div>
        <div class="form-group">
          <label for="planVer">Plan Version</label>
          <input
            id="planVer"
            v-model="searchParams.planVer"
            type="text"
            placeholder="Plan Version"
          />
        </div>
        <button class="search-button" :disabled="loading" @click="handleSearch">
          {{ loading ? "조회중..." : "조회" }}
        </button>
      </div>
    </section>

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
import { reactive, onMounted, ref } from "vue";
import { ExtendFlexGrid } from "@vmscloud/moz-component";
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
  padding: var(--spacing-9, 1rem);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: var(--spacing-6, 0.5rem);
}

.search-section {
  .search-form {
    display: flex;
    gap: 1rem;
    align-items: flex-end;
    flex-wrap: wrap;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;

    label {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--color-text-secondary, #6b7280);
    }

    input {
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--color-border, #d1d5db);
      border-radius: 0.375rem;
      font-size: 0.875rem;
      min-width: 280px;

      &:focus {
        outline: none;
        border-color: var(--color-primary, #3b82f6);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
      }
    }
  }

  .search-button {
    padding: 0.5rem 1.5rem;
    background-color: var(--color-primary, #3b82f6);
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover:not(:disabled) {
      background-color: var(--color-primary-hover, #2563eb);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.result-info {
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
  border-radius: 0.5rem;
  background: white;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-text-secondary, #9ca3af);
  font-size: 0.875rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
}
</style>
