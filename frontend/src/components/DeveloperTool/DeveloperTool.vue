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
import './styles/index.scss'

const isDev = computed(() => {
  // Module Federation으로 로드된 경우 __remotes__가 정의되어 있지 않음
  return typeof window !== "undefined" && !window.__POWERED_BY_APS_HOST__;
});
</script>