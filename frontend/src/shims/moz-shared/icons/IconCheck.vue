<template>
  <svg xmlns="http://www.w3.org/2000/svg" :width="d.width" :height="d.height" viewBox="0 0 16 16">
    <g data-name="check-icon" :style="{ fill: disabled ? '#a7b1bc' : color }">
      <path
        d="M836.533 699.734h-.022a.928.928 0 0 1-.716-.336l-3.779-4.535a.926.926 0 0 1-.212-.68.93.93 0 0 1 1.643-.512l3.026 3.63 6.096-8.128a.922.922 0 0 1 .745-.373c.202 0 .396.064.559.186.199.15.328.367.363.614a.925.925 0 0 1-.177.69l-6.803 9.071a.928.928 0 0 1-.721.373h-.002z"
        style="stroke: none"
        transform="translate(-829.971 -686.318)"
      />
      <path
        d="M836.532 699.634a.833.833 0 0 0 .644-.333l6.803-9.07a.831.831 0 1 0-1.33-.998l-6.172 8.23-3.107-3.728a.83.83 0 1 0-1.277 1.064l3.78 4.535c.157.19.391.3.638.3h.021m.003.2h-.024c-.307 0-.596-.136-.793-.372l-3.779-4.535a1.025 1.025 0 0 1-.235-.754 1.03 1.03 0 0 1 1.82-.567l2.945 3.534 6.02-8.027a1.034 1.034 0 0 1 1.444-.207c.22.165.363.407.402.68.04.273-.03.544-.196.765l-6.803 9.07c-.19.254-.481.404-.799.412h-.002z"
        :style="{ fill: disabled ? '#a7b1bc' : color, stroke: 'none' }"
        transform="translate(-829.971 -686.318)"
      />
    </g>
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
  size: '12',
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
