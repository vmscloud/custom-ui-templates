<template>
  <DeveloperTool>
    <main class="moz-contents">
      <router-view />
    </main>
  </DeveloperTool>
</template>

<script setup lang="ts">
import { computed } from "vue";
import DeveloperTool from "@/components/DeveloperTool/DeveloperTool.vue";

// Host에서 로드되었는지 확인 (개발 모드 구분)
const isDev = computed(() => {
  // Module Federation으로 로드된 경우 __remotes__가 정의되어 있지 않음
  return typeof window !== "undefined" && !window.__POWERED_BY_APS_HOST__;
});
</script>

<style scoped>
/* APS Main.vue의 .moz-contents와 동일한 스타일 */
.moz-contents {
  flex: 1;
  display: grid;
  grid-template-rows: auto 1fr;
  height: 100%;
  overflow: hidden;
}
</style>
