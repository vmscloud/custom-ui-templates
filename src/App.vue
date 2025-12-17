<template>
  <div class="external-app">
    <!-- 개발용 헤더 (Host에서는 Main.vue 레이아웃 사용) -->
    <header class="dev-header" v-if="isDev">
      <h1>External Dev App (개발 모드)</h1>
      <p>이 헤더는 개발 모드에서만 표시됩니다. Host(APS)에서 로드 시에는 표시되지 않습니다.</p>
    </header>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// Host에서 로드되었는지 확인 (개발 모드 구분)
const isDev = computed(() => {
  // Module Federation으로 로드된 경우 __remotes__가 정의되어 있지 않음
  return typeof window !== 'undefined' && !window.__POWERED_BY_APS_HOST__;
});
</script>

<style scoped>
.external-app {
  min-height: 100vh;
}

.dev-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  margin-bottom: 1rem;
}

.dev-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.dev-header p {
  margin: 0;
  font-size: 0.875rem;
  opacity: 0.9;
}
</style>

