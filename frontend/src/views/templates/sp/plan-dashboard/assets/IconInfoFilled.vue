<template>
  <svg :width="d.width" :height="d.height" viewBox="0 0 14 15" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M7 14.5C10.866 14.5 14 11.366 14 7.5C14 3.63401 10.866 0.5 7 0.5C3.13401 0.5 0 3.63401 0 7.5C0 11.366 3.13401 14.5 7 14.5ZM6.53369 4.36582C6.53369 4.03445 6.80232 3.76582 7.13369 3.76582H7.33369C7.66506 3.76582 7.93369 4.03445 7.93369 4.36582V8.29915C7.93369 8.63052 7.66506 8.89915 7.33369 8.89915H7.13369C6.80232 8.89915 6.53369 8.63053 6.53369 8.29915V4.36582ZM6.53369 10.4327C6.53369 10.1013 6.80232 9.83272 7.13369 9.83272H7.33369C7.66506 9.83272 7.93369 10.1013 7.93369 10.4327V10.6327C7.93369 10.9641 7.66506 11.2327 7.33369 11.2327H7.13369C6.80232 11.2327 6.53369 10.9641 6.53369 10.6327V10.4327Z"
      :fill="color"
    />
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
  size: '14',
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
