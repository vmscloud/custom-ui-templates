<template>
  <MozComponentLocaleProvider :locale="koKR">
    <DeveloperTool>
      <main class="moz-contents">
        <router-view />
      </main>
    </DeveloperTool>
  </MozComponentLocaleProvider>
</template>

<script setup lang="ts">
import DeveloperTool from "@/components/DeveloperTool/DeveloperTool.vue";
import { MozComponentLocaleProvider, koKR } from "@vmscloud/moz-ui-components-vue";
</script>

<style scoped>
/* APS Main.vue의 .moz-contents와 동일한 스타일 */
.moz-contents {
  flex: 1;
  height: 100%;
  overflow: hidden;
}
</style>
