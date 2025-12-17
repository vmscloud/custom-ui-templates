<template>
  <div class="item-master-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">Item Master</h1>
      <p class="page-description">Item Master 데이터를 조회합니다.</p>
    </div>

    <!-- 검색 조건 -->
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

    <!-- 그리드 -->
    <section class="grid-section">
      <div v-if="loading" class="loading-state">로딩 중...</div>
      <div v-else-if="data.length > 0" class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Item ID</th>
              <th>Item Name</th>
              <th>Item Type</th>
              <th>Item Group</th>
              <th>Description</th>
              <th>Procurement Type</th>
              <th>Prod Type</th>
              <th>Item Spec</th>
              <th>Priority</th>
              <th>Create User</th>
              <th>Update Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data" :key="item.item_id">
              <td>{{ item.item_id }}</td>
              <td>{{ item.item_name }}</td>
              <td>{{ item.item_type }}</td>
              <td>{{ item.item_group_id }}</td>
              <td>{{ item.description }}</td>
              <td>{{ item.procurement_type }}</td>
              <td>{{ item.prod_type }}</td>
              <td>{{ item.item_spec }}</td>
              <td>{{ item.item_priority }}</td>
              <td>{{ item.create_user_id }}</td>
              <td>{{ formatDate(item.update_datetime) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-state">조회된 데이터가 없습니다.</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from "vue";
import { useItemMaster, type ItemMasterParams } from "./itemMaster";

// Item Master 컴포저블
const { data, loading, error, count, loadData } = useItemMaster();

// 검색 파라미터
const searchParams = reactive<ItemMasterParams>({
  projectId: "31C13202-5860-4123-8ACD-81C2373F1E73",
  planVer: "20251103-P-TEST",
});

// 날짜 포맷
function formatDate(dateStr: string | null): string {
  if (!dateStr) return "-";
  try {
    return new Date(dateStr).toLocaleString("ko-KR");
  } catch {
    return dateStr;
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
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.search-section {
  margin-bottom: 1rem;

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
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  background: white;
}

.table-wrapper {
  height: 100%;
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;

  th,
  td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--color-border, #e5e7eb);
    white-space: nowrap;
  }

  th {
    background: var(--color-bg-secondary, #f9fafb);
    font-weight: 600;
    color: var(--color-text-secondary, #6b7280);
    position: sticky;
    top: 0;
    z-index: 1;
  }

  tbody tr:hover {
    background: var(--color-bg-hover, #f3f4f6);
  }

  tbody tr:last-child td {
    border-bottom: none;
  }
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-text-secondary, #9ca3af);
  font-size: 0.875rem;
}
</style>
