<template>
  <svg :width="width" :height="height" viewBox="0 0 27 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M27 5.73913L19 12V0L27 5.73913Z" :fill="color" />
    <line y1="5.5" x2="19" y2="5.5" :stroke="color" />
  </svg>
</template>
<script setup lang="ts">
import { toRefs } from 'vue';

interface Props {
  width?: number;
  height?: number;
  color?: string;
}
const props = withDefaults(defineProps<Props>(), {
  width: 27,
  height: 12,
});
const { width, height, color } = toRefs(props);
</script>
