<template>
  <div class="external-app">
    <!-- 개발용 헤더 (Host에서는 Main.vue 레이아웃 사용) -->
    <header class="dev-header" v-if="isDev">
      <h1>External Dev App (개발 모드)</h1>
    </header>
    <!-- APS Main.vue의 .moz-contents 영역과 동일한 구조 -->
    <main class="moz-contents">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

// Host에서 로드되었는지 확인 (개발 모드 구분)
const isDev = computed(() => {
  // Module Federation으로 로드된 경우 __remotes__가 정의되어 있지 않음
  return typeof window !== "undefined" && !window.__POWERED_BY_APS_HOST__;
});
</script>

<style scoped>
.external-app {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dev-header {
  height: 45px; /* TopAppBar와 동일 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 1rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.dev-header h1 {
  margin: 0;
  font-size: 1rem;
}

.dev-header p {
  margin: 0;
  font-size: 0.875rem;
  opacity: 0.9;
}

/* APS Main.vue의 .moz-contents와 동일한 스타일 */
.moz-contents {
  flex: 1;
  display: grid;
  grid-template-rows: auto 1fr;
  height: 100%;
  overflow: hidden;
}
</style>
