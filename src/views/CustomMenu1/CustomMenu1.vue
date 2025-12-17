<template>
  <div class="custom-menu-1">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">Custom Menu 1</h1>
      <p class="page-description">외주 개발자가 만든 샘플 메뉴입니다.</p>
    </div>

    <!-- Host 정보 표시 -->
    <section class="info-section">
      <h2>Host(APS) 연동 정보</h2>
      <div class="info-grid">
        <div class="info-card">
          <h3>사용자 정보</h3>
          <dl>
            <dt>이름</dt>
            <dd>{{ userInfo?.name || "-" }}</dd>
            <dt>이메일</dt>
            <dd>{{ userInfo?.email || "-" }}</dd>
            <dt>관리자 여부</dt>
            <dd>{{ isAdmin ? "예" : "아니오" }}</dd>
          </dl>
        </div>

        <div class="info-card">
          <h3>프로젝트 정보</h3>
          <dl>
            <dt>프로젝트 ID</dt>
            <dd>{{ currentProjectID || "-" }}</dd>
            <dt>프로젝트 이름</dt>
            <dd>{{ currentProject?.projectNM || "-" }}</dd>
          </dl>
        </div>

        <div class="info-card">
          <h3>Plan Cycle 정보</h3>
          <dl>
            <dt>Plan Version</dt>
            <dd>{{ planVer || "-" }}</dd>
            <dt>From Date</dt>
            <dd>{{ fromDate?.format?.("YYYY-MM-DD") || "-" }}</dd>
            <dt>To Date</dt>
            <dd>{{ toDate?.format?.("YYYY-MM-DD") || "-" }}</dd>
          </dl>
        </div>
      </div>
    </section>

    <!-- 샘플 데이터 그리드 -->
    <section class="data-section">
      <h2>샘플 데이터</h2>
      <div class="sample-grid">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sampleData" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.name }}</td>
              <td>
                <span :class="['status-badge', `status-${item.status}`]">
                  {{ item.status }}
                </span>
              </td>
              <td>{{ item.created }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useHostStores } from "@/composables/useHostStores";

// Host 스토어에서 정보 가져오기
const hostStores = useHostStores();

// PlanCycle 정보
const { planVer, fromDate, toDate } = hostStores.planCycle;

// 프로젝트 정보
const { currentProjectID, currentProject, userInfo, isAdmin } =
  hostStores.projectInfo;

// 샘플 데이터
const sampleData = ref([
  { id: 1, name: "Item A", status: "active", created: "2024-01-15" },
  { id: 2, name: "Item B", status: "pending", created: "2024-01-16" },
  { id: 3, name: "Item C", status: "completed", created: "2024-01-17" },
  { id: 4, name: "Item D", status: "active", created: "2024-01-18" },
  { id: 5, name: "Item E", status: "inactive", created: "2024-01-19" },
]);
</script>

<style scoped lang="scss">
.custom-menu-1 {
  padding: 1.5rem;
  height: 100%;
  overflow: auto;
}

.page-header {
  margin-bottom: 2rem;

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

.info-section,
.data-section {
  margin-bottom: 2rem;

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border, #e5e7eb);
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.info-card {
  background: var(--color-bg-secondary, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1rem;

  h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.75rem 0;
    color: var(--color-text-primary, #1f2937);
  }

  dl {
    margin: 0;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 1rem;
  }

  dt {
    font-weight: 500;
    color: var(--color-text-secondary, #6b7280);
  }

  dd {
    margin: 0;
    color: var(--color-text-primary, #1f2937);
  }
}

.sample-grid {
  overflow-x: auto;

  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: 0.5rem;
    overflow: hidden;
  }

  th,
  td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--color-border, #e5e7eb);
  }

  th {
    background: var(--color-bg-secondary, #f9fafb);
    font-weight: 600;
    color: var(--color-text-secondary, #6b7280);
  }

  tr:last-child td {
    border-bottom: none;
  }

  tr:hover {
    background: var(--color-bg-hover, #f3f4f6);
  }
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;

  &.status-active {
    background: #dcfce7;
    color: #166534;
  }

  &.status-pending {
    background: #fef3c7;
    color: #92400e;
  }

  &.status-completed {
    background: #dbeafe;
    color: #1e40af;
  }

  &.status-inactive {
    background: #f3f4f6;
    color: #6b7280;
  }
}
</style>
