<template>
  <svg :width="width" :height="height" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M7.91699 4.11084L4.96289 6.99988L2.08203 4.11084"
      :stroke="color"
      stroke-width="1.6"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
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
  width: 18,
  height: 18,
  color: '#8998B5',
});
const { width, height, color } = toRefs(props);
</script>
