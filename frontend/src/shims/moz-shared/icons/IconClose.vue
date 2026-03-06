<template>
  <svg v-if="d.width <= 10" :width="d.width" :height="d.height" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8.5 1.5L1.49999 8.50001" :stroke="color" stroke-width="1.75" stroke-linecap="round" />
    <path d="M1.5 1.5L8.50001 8.50001" :stroke="color" stroke-width="1.75" stroke-linecap="round" />
  </svg>
  <svg v-else-if="d.width <= 13 && d.width >= 11 && !thin" :width="d.width" :height="d.height" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M1.71436 1.71428L10.8069 10.7926" :stroke="color" stroke-width="2" stroke-linecap="round" />
    <path d="M10.8069 1.71428L1.71436 10.7926" :stroke="color" stroke-width="2" stroke-linecap="round" />
  </svg>
  <svg v-else-if="d.width <= 13 && d.width >= 11 && thin" :width="d.width" :height="d.height" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10.2 1.7998L1.79994 10.1998" :stroke="color" stroke-width="1.6" stroke-linecap="round" />
    <path d="M1.79993 1.7998L10.1999 10.1998" :stroke="color" stroke-width="1.6" stroke-linecap="round" />
  </svg>
  <svg v-else-if="d.width >= 14" :width="d.width" :height="d.height" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g id="icon_close"><g id="그룹 3939">
      <path fill-rule="evenodd" clip-rule="evenodd" d="M1.29234 1.29345C1.68256 0.902618 2.31572 0.902121 2.70655 1.29234L13.3146 11.8837C13.7054 12.2739 13.7059 12.9071 13.3157 13.2979C12.9254 13.6887 12.2923 13.6892 11.9014 13.299L1.29345 2.70766C0.902618 2.31744 0.902121 1.68428 1.29234 1.29345Z" :fill="disabled ? '#a7b1bc' : color" />
      <path fill-rule="evenodd" clip-rule="evenodd" d="M13.3157 1.29345C13.7059 1.68428 13.7054 2.31744 13.3146 2.70766L2.70655 13.299C2.31572 13.6892 1.68256 13.6887 1.29234 13.2979C0.902121 12.9071 0.902618 12.2739 1.29345 11.8837L11.9014 1.29234C12.2923 0.902121 12.9254 0.902618 13.3157 1.29345Z" :fill="disabled ? '#a7b1bc' : color" />
    </g></g>
  </svg>
</template>
<script setup lang="ts">
import { computed, toRefs } from 'vue';
interface Props { size?: '10'|'12'|'14'|'16'|'18'|'20'|'22'|'30'; color?: string; disabled?: boolean; thin?: boolean; }
const props = withDefaults(defineProps<Props>(), { size: '10', color: '#8998b5', disabled: false, thin: false });
const { size, color, thin } = toRefs(props);
const d = computed(() => {
  const preset: Record<string, {width:number;height:number}> = { '10':{width:10,height:10},'12':{width:12,height:12},'14':{width:14,height:14},'16':{width:16,height:16},'18':{width:18,height:18},'20':{width:20,height:20},'22':{width:22,height:22},'30':{width:30,height:30} };
  return preset[size.value] ?? { width: 12, height: 12 };
});
</script>
