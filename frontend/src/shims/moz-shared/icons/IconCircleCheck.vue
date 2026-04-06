<template>
  <svg xmlns="http://www.w3.org/2000/svg" :width="d.width" :height="d.height" viewBox="0 0 12 12">
    <g id="icon_확정" transform="translate(-1432.899 -749.899)">
      <rect
        id="사각형_4934"
        data-name="사각형 4934"
        width="12"
        height="12"
        transform="translate(1432.899 749.899)"
        fill="none"
      />
      <path
        id="패스_4568"
        data-name="패스 4568"
        d="M12.332,4.085,6.976,9.441a.533.533,0,0,1-.755,0L4.706,7.925a.533.533,0,0,1,0-.755h0a.533.533,0,0,1,.755,0L6.6,8.305,11.571,3.33a.533.533,0,0,1,.755,0h0A.529.529,0,0,1,12.332,4.085ZM9.376,2.4A5.354,5.354,0,1,0,12.53,8.75a5.18,5.18,0,0,0,.112-2.26.539.539,0,0,0-.91-.289h0a.539.539,0,0,0-.145.477,4.027,4.027,0,0,1-.278,2.281,4.354,4.354,0,0,1-3.54,2.662A4.286,4.286,0,1,1,9.311,3.544a.536.536,0,0,0,.627-.1h0a.537.537,0,0,0-.129-.857C9.665,2.527,9.52,2.457,9.376,2.4Z"
        transform="translate(1431.54 748.542)"
        :fill="color"
        :stroke="color"
        stroke-width="0.28"
      />
    </g>
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
