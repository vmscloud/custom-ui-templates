<template>
  <svg xmlns="http://www.w3.org/2000/svg" :width="d.width" :height="d.height" viewBox="0 0 12.005 12.015">
    <path data-name="패스 3250" d="M0 0h12v12H0z" style="fill: none" />
    <g data-name="사각형 3366" transform="translate(3.944)" :stroke="color" style="stroke-width: 1.75px; fill: none">
      <rect width="7.546" height="8.77" rx="1.6" style="stroke: none" />
      <rect x=".875" y=".875" width="5.796" height="7.02" rx=".725" style="fill: none" />
    </g>
    <path data-name="패스 3268" d="M0 4.663V12.5h6.835" transform="translate(1.499 -1.363)" :stroke="color" style="stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.75px; fill: none" />
  </svg>
</template>
<script setup lang="ts">
import { computed, toRefs } from 'vue';
interface Props { size?: '10'|'12'|'14'|'16'|'18'|'20'|'22'|'30'; color?: string; disabled?: boolean; }
const props = withDefaults(defineProps<Props>(), { size: '12', color: '#8998b5', disabled: false });
const { size, color } = toRefs(props);
const d = computed(() => {
  const preset: Record<string, {width:number;height:number}> = { '10':{width:10,height:10},'12':{width:12,height:12},'14':{width:14,height:14},'16':{width:16,height:16},'18':{width:18,height:18},'20':{width:20,height:20},'22':{width:22,height:22},'30':{width:30,height:30} };
  return preset[size.value] ?? { width: 12, height: 12 };
});
</script>
