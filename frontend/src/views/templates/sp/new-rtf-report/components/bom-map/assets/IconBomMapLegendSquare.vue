<template>
  <svg :width="width" :height="height" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="0.5" y="0.5" width="19" height="15" rx="3.5" :fill="fill" :stroke="stroke" />
  </svg>
</template>
<script setup lang="ts">
import { toRefs } from 'vue';

interface Props {
  width?: number;
  height?: number;
  fill?: string;
  stroke?: string;
}
const props = withDefaults(defineProps<Props>(), {
  width: 20,
  height: 16,
});
const { width, height, fill, stroke } = toRefs(props);
</script>
