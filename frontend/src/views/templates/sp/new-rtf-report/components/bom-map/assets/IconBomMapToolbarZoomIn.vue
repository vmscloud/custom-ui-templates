<template>
  <svg :width="width" :height="height" viewBox="0 0 19 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g clip-path="url(#clip0_10840_10529)">
      <g clip-path="url(#clip1_10840_10529)">
        <path d="M9.5 2.57141V15.4286" :stroke="color" stroke-width="1.8" stroke-linecap="round" />
        <path d="M3.07141 9H15.9286" :stroke="color" stroke-width="1.8" stroke-linecap="round" />
      </g>
    </g>
    <defs>
      <clipPath id="clip0_10840_10529">
        <rect width="18" height="18" fill="white" transform="translate(0.5)" />
      </clipPath>
      <clipPath id="clip1_10840_10529">
        <rect width="18" height="18" fill="white" transform="translate(0.5)" />
      </clipPath>
    </defs>
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
  width: 19,
  height: 18,
  color: '#8998B5',
});
const { width, height, color } = toRefs(props);
</script>
