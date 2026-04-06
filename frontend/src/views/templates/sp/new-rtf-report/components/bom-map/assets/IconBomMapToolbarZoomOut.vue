<template>
  <svg :width="d.width" :height="d.height" viewBox="0 0 19 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3.07141 9H15.9286" :stroke="color" stroke-width="1.8" stroke-linecap="round" />
  </svg>
</template>
<script setup lang="ts">
import { computed, toRefs } from 'vue';

interface Props {
  size?: '10' | '12' | '14' | '16' | '18' | '20' | '22' | '30';
  color?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: '18',
  color: '#8998b5',
  disabled: false,
});
const { size, color } = toRefs(props);

const d = computed(() => {
  const preset = {
    '10': { width: 10, height: 10 },
    '12': { width: 12, height: 12 },
    '14': { width: 14, height: 14 },
    '16': { width: 16, height: 16 },
    '18': { width: 18, height: 18 },
    '20': { width: 20, height: 20 },
    '22': { width: 22, height: 22 },
    '30': { width: 30, height: 30 },
  };
  return preset[size.value] ?? { width: 12, height: 12 };
});
</script>
