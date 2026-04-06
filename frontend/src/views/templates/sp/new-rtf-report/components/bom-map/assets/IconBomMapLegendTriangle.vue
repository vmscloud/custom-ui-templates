<template>
  <svg :width="width" :height="height" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 1.02956L19.1502 17.5H0.849757L10 1.02956Z" :fill="fill" :stroke="stroke" />
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
  height: 18,
});
const { width, height, fill, stroke } = toRefs(props);
</script>
