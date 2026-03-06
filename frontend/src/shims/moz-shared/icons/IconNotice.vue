<template>
  <svg :width="d.width" :height="d.height" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      fill-rule="evenodd" clip-rule="evenodd"
      d="M15 30C23.2843 30 30 23.2843 30 15C30 6.71573 23.2843 0 15 0C6.71573 0 0 6.71573 0 15C0 23.2843 6.71573 30 15 30ZM14 7.6C14 7.26863 14.2686 7 14.6 7H16.4C16.7314 7 17 7.26863 17 7.6V17.4C17 17.7314 16.7314 18 16.4 18H14.6C14.2686 18 14 17.7314 14 17.4V7.6ZM14 20.6C14 20.2686 14.2686 20 14.6 20H16.4C16.7314 20 17 20.2686 17 20.6V22.4C17 22.7314 16.7314 23 16.4 23H14.6C14.2686 23 14 22.7314 14 22.4V20.6Z"
      :fill="color"
    />
  </svg>
</template>
<script setup lang="ts">
import { computed, toRefs } from 'vue';
interface Props { size?: '10'|'12'|'14'|'16'|'18'|'20'|'22'|'30'; color?: string; disabled?: boolean; }
const props = withDefaults(defineProps<Props>(), { size: '30', color: '#8998b5', disabled: false });
const { size, color } = toRefs(props);
const d = computed(() => {
  const preset: Record<string, {width:number;height:number}> = { '10':{width:10,height:10},'12':{width:12,height:12},'14':{width:14,height:14},'16':{width:16,height:16},'18':{width:18,height:18},'20':{width:20,height:20},'22':{width:22,height:22},'30':{width:30,height:30} };
  return preset[size.value] ?? { width: 12, height: 12 };
});
</script>
