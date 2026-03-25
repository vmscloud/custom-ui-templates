<template>
  <svg xmlns="http://www.w3.org/2000/svg" :width="d.width" :height="d.height" viewBox="0 0 14 14">
    <g id="icon_open_14" transform="translate(-878.001 -433)">
      <path id="패스_3250" data-name="패스 3250" d="M0,0H14V14H0Z" transform="translate(878.001 433)" fill="none" />
      <path
        id="합치기_204"
        data-name="합치기 204"
        d="M1.513,11.724A1.515,1.515,0,0,1,0,10.21v-8.7A1.516,1.516,0,0,1,1.513,0H4.535v0A.881.881,0,0,1,4.637,0a.855.855,0,0,1,0,1.71h0a.815.815,0,0,1-.1-.006H1.7v8.316h8.322V6.949s0,0,0,0,0-.029,0-.043,0-.032,0-.048V6.79h.006a.831.831,0,0,1,.034-.149.016.016,0,0,0,0,0l0-.012,0-.01,0-.007a.851.851,0,0,1,1.59-.02l0,.01a.028.028,0,0,1,0,.007.833.833,0,0,1,.046.186h.007v3.42a1.514,1.514,0,0,1-1.512,1.514Zm3.748-5.19a.85.85,0,0,1,0-1.2C5.291,5.3,7.3,3.307,8.9,1.7h-1.8a.852.852,0,0,1,0-1.7h3.783a.853.853,0,0,1,.843.736.861.861,0,0,1,.017.2V4.485a.853.853,0,1,1-1.7,0V2.974c-1.59,1.594-3.542,3.537-3.57,3.562a.851.851,0,0,1-1.2,0Z"
        transform="translate(879.133 434.138)"
        :fill="color"
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
