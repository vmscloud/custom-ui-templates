<template>
  <div class="custom-menu-2">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">Custom Menu 2</h1>
      <p class="page-description">moz-component를 활용한 샘플 폼 페이지입니다.</p>
    </div>

    <!-- 폼 섹션 -->
    <section class="form-section">
      <h2>데이터 입력 폼</h2>

      <form @submit.prevent="handleSubmit" class="sample-form">
        <div class="form-row">
          <div class="form-group">
            <label for="itemName">아이템 이름</label>
            <input id="itemName" v-model="formData.name" type="text" placeholder="이름을 입력하세요" />
          </div>

          <div class="form-group">
            <label for="itemCode">아이템 코드</label>
            <input id="itemCode" v-model="formData.code" type="text" placeholder="코드를 입력하세요" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="category">카테고리</label>
            <select id="category" v-model="formData.category">
              <option value="">선택하세요</option>
              <option value="A">카테고리 A</option>
              <option value="B">카테고리 B</option>
              <option value="C">카테고리 C</option>
            </select>
          </div>

          <div class="form-group">
            <label for="quantity">수량</label>
            <input id="quantity" v-model.number="formData.quantity" type="number" min="0" />
          </div>
        </div>

        <div class="form-group">
          <label for="description">설명</label>
          <textarea id="description" v-model="formData.description" rows="4" placeholder="설명을 입력하세요"></textarea>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="handleReset">초기화</button>
          <button type="submit" class="btn btn-primary">저장</button>
        </div>
      </form>
    </section>

    <!-- 제출된 데이터 표시 -->
    <section v-if="submittedData.length > 0" class="submitted-section">
      <h2>제출된 데이터</h2>
      <div class="submitted-list">
        <div v-for="(item, index) in submittedData" :key="index" class="submitted-item">
          <div class="item-header">
            <strong>{{ item.name }}</strong>
            <span class="item-code">{{ item.code }}</span>
          </div>
          <div class="item-details">
            <span>카테고리: {{ item.category || '-' }}</span>
            <span>수량: {{ item.quantity }}</span>
          </div>
          <p class="item-description">{{ item.description || '설명 없음' }}</p>
          <div class="item-meta">
            <span>프로젝트: {{ currentProject?.projectNM }}</span>
            <span>Plan Ver: {{ planVer }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useHostStores } from '@/composables/useHostStores';

// Host 스토어에서 정보 가져오기
const hostStores = useHostStores();
const { planVer } = hostStores.planCycle;
const { currentProject } = hostStores.projectInfo;

// 폼 데이터
const initialFormData = {
  name: '',
  code: '',
  category: '',
  quantity: 0,
  description: '',
};

const formData = reactive({ ...initialFormData });
const submittedData = ref<typeof initialFormData[]>([]);

// 폼 제출
const handleSubmit = () => {
  if (!formData.name || !formData.code) {
    alert('이름과 코드는 필수 입력 항목입니다.');
    return;
  }

  submittedData.value.unshift({ ...formData });
  handleReset();
};

// 폼 초기화
const handleReset = () => {
  Object.assign(formData, initialFormData);
};
</script>

<style scoped lang="scss">
.custom-menu-2 {
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

.form-section,
.submitted-section {
  margin-bottom: 2rem;

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border, #e5e7eb);
  }
}

.sample-form {
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  label {
    font-weight: 500;
    color: var(--color-text-secondary, #6b7280);
    font-size: 0.875rem;
  }

  input,
  select,
  textarea {
    padding: 0.625rem 0.75rem;
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: 0.375rem;
    font-size: 0.875rem;
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }

  textarea {
    resize: vertical;
    min-height: 100px;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.btn {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;

  &.btn-primary {
    background: #3b82f6;
    color: white;
    border: none;

    &:hover {
      background: #2563eb;
    }
  }

  &.btn-secondary {
    background: white;
    color: var(--color-text-secondary, #6b7280);
    border: 1px solid var(--color-border, #e5e7eb);

    &:hover {
      background: var(--color-bg-secondary, #f9fafb);
    }
  }
}

.submitted-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submitted-item {
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1rem;

  .item-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;

    strong {
      font-size: 1rem;
    }

    .item-code {
      background: var(--color-bg-secondary, #f3f4f6);
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      color: var(--color-text-secondary, #6b7280);
    }
  }

  .item-details {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--color-text-secondary, #6b7280);
    margin-bottom: 0.5rem;
  }

  .item-description {
    margin: 0.5rem 0;
    font-size: 0.875rem;
    color: var(--color-text-primary, #1f2937);
  }

  .item-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.75rem;
    color: var(--color-text-muted, #9ca3af);
    padding-top: 0.5rem;
    border-top: 1px solid var(--color-border, #e5e7eb);
  }
}
</style>

