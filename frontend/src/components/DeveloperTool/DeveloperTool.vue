<template>
  <DeveloperToolCore v-if="isDev">
    <slot>
    </slot>
  </DeveloperToolCore>
  <slot v-else>
  </slot>
</template>
<script setup lang="ts">
import DeveloperToolCore from "@/components/DeveloperTool/DeveloperToolCore.vue";
import {computed} from "vue";
import { setProjectIdResolver } from "@/api/client";
import { useHostData } from "@/composables/useHostStores";
import './styles/index.scss'

const isDev = computed(() => {
  // Module Federation으로 로드된 경우 __remotes__가 정의되어 있지 않음
  return typeof window !== "undefined" && !window.__POWERED_BY_APS_HOST__;
});

// Host(APS) 환경: DeveloperToolCore를 거치지 않으므로 여기서 resolver 설정
if (!isDev.value) {
  const hostData = useHostData();
  setProjectIdResolver(() => hostData.value?.projectInfo?.currentProjectID ?? "");
}
</script>