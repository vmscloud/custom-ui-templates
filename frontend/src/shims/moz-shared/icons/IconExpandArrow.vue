<template>
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
    <mask id="mask0_36823_12642" style="mask-type: alpha" maskUnits="userSpaceOnUse" x="0" y="0" width="16" height="16">
      <rect width="16" height="16" fill="#D9D9D9" />
    </mask>
    <g mask="url(#mask0_36823_12642)">
      <mask id="path-2-outside-1_36823_12642" maskUnits="userSpaceOnUse" x="0.99707" y="1" width="14" height="14" fill="black">
        <rect fill="white" x="0.99707" y="1" width="14" height="14" />
        <path d="M13.0957 2C13.5615 2 13.9454 2.35485 13.9912 2.80859L13.9961 2.90039V6.2334C13.9961 6.61975 13.6822 6.93359 13.2959 6.93359C12.9096 6.93355 12.5967 6.61972 12.5967 6.2334V4.38867L4.38477 12.6006H6.22949C6.61575 12.6006 6.92951 12.9136 6.92969 13.2998C6.92957 13.686 6.61575 14 6.22949 14H2.89648L2.80469 13.9951C2.38108 13.9523 2.04477 13.615 2.00195 13.1914L1.99707 13.0996V9.7666C1.99723 9.3805 2.3102 9.06757 2.69629 9.06738C3.08255 9.06741 3.39637 9.38037 3.39648 9.7666V11.6104L11.6064 3.40039H9.7627C9.37638 3.40036 9.06349 3.08651 9.06348 2.7002C9.06348 2.31387 9.37637 2.00003 9.7627 2H13.0957Z" />
      </mask>
      <path d="M13.0957 2C13.5615 2 13.9454 2.35485 13.9912 2.80859L13.9961 2.90039V6.2334C13.9961 6.61975 13.6822 6.93359 13.2959 6.93359C12.9096 6.93355 12.5967 6.61972 12.5967 6.2334V4.38867L4.38477 12.6006H6.22949C6.61575 12.6006 6.92951 12.9136 6.92969 13.2998C6.92957 13.686 6.61575 14 6.22949 14H2.89648L2.80469 13.9951C2.38108 13.9523 2.04477 13.615 2.00195 13.1914L1.99707 13.0996V9.7666C1.99723 9.3805 2.3102 9.06757 2.69629 9.06738C3.08255 9.06741 3.39637 9.38037 3.39648 9.7666V11.6104L11.6064 3.40039H9.7627C9.37638 3.40036 9.06349 3.08651 9.06348 2.7002C9.06348 2.31387 9.37637 2.00003 9.7627 2H13.0957Z" fill="#8998B5" />
    </g>
  </svg>
</template>
<script setup lang="ts">
import { computed, toRefs } from 'vue';
interface Props { size?: '10'|'12'|'14'|'16'|'18'|'20'|'22'|'30'; color?: string; disabled?: boolean; }
const props = withDefaults(defineProps<Props>(), { size: '16', color: '#D9D9D9', disabled: false });
const { size, color } = toRefs(props);
const d = computed(() => {
  const preset: Record<string, {width:number;height:number}> = { '10':{width:10,height:10},'12':{width:12,height:12},'14':{width:14,height:14},'16':{width:16,height:16},'18':{width:18,height:18},'20':{width:20,height:20},'22':{width:22,height:22},'30':{width:30,height:30} };
  return preset[size.value] ?? { width: 12, height: 12 };
});
</script>
