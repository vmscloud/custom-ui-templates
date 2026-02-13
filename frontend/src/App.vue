<template>
  <MozConfigProvider :locale="koKR">
    <DeveloperTool>
      <main class="moz-contents">
        <router-view />
      </main>
    </DeveloperTool>
  </MozConfigProvider>
</template>

<script setup lang="ts">
import DeveloperTool from "@/components/DeveloperTool/DeveloperTool.vue";
import { MozConfigProvider, koKR } from "@vmscloud/moz-ui-components";
import { setProjectIdResolver } from "@/api/client";
import { useHostStores } from "@/composables/useHostStores";

const { projectInfo } = useHostStores();
setProjectIdResolver(() => projectInfo.currentProjectID.value);
</script>

<style scoped>
/* APS Main.vue의 .moz-contents와 동일한 스타일 */
.moz-contents {
  flex: 1;
  display: grid;
  /* grid-template-rows: auto 1fr; */
  height: 100%;
  overflow: hidden;
}
</style>
