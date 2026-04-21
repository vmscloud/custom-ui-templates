<template>
  <svg :width="d.width" :height="d.height" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g clip-path="url(#clip0_770_3837)">
      <g clip-path="url(#clip1_770_3837)">
        <path d="M1 2.00101H9.7" :stroke="color" stroke-width="1.8" stroke-linecap="round" />
        <path d="M1 6.00101H7.6" :stroke="color" stroke-width="1.8" stroke-linecap="round" />
        <path d="M1 9.50101H4.767" :stroke="color" stroke-width="1.8" stroke-linecap="round" />
        <path
          d="M8.00795 11.793H7.99895C7.84279 11.792 7.69305 11.7307 7.58095 11.622C7.50878 11.5519 7.45539 11.4648 7.42568 11.3687C7.39598 11.2726 7.39091 11.1706 7.41095 11.072L7.71095 9.51401C7.73371 9.39701 7.79081 9.28943 7.87495 9.20501L10.488 6.54301L12.624 8.60601L10.005 11.272C9.9222 11.3566 9.81595 11.4145 9.69995 11.438L8.13395 11.779C8.09257 11.7881 8.05033 11.7928 8.00795 11.793ZM13.181 8.04001L11.044 5.97201L11.657 5.35201C11.7695 5.23916 11.9217 5.17474 12.081 5.1725C12.2404 5.17026 12.3943 5.23037 12.51 5.34001L13.777 6.56001C13.8345 6.61586 13.8805 6.68256 13.9122 6.75626C13.9439 6.82996 13.9607 6.90921 13.9616 6.98943C13.9626 7.06965 13.9476 7.14926 13.9176 7.22368C13.8876 7.29809 13.8432 7.36584 13.787 7.42301L13.181 8.04001Z"
          :fill="color"
        />
      </g>
    </g>
    <defs>
      <clipPath id="clip0_770_3837">
        <rect :width="d.width" :height="d.height" :fill="color" />
      </clipPath>
      <clipPath id="clip1_770_3837">
        <rect :width="d.width" :height="d.height" :fill="color" />
      </clipPath>
    </defs>
  </svg>
</template>

<script setup lang="ts">
import { computed, toRefs } from "vue";

interface Props {
  size?: "10" | "12" | "14" | "16" | "18" | "20" | "22" | "30";
  color?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: "14",
  color: "#8998b5",
  disabled: false,
});
const { size, color } = toRefs(props);

const d = computed(() => {
  const preset = {
    "10": { width: 10, height: 10 },
    "12": { width: 12, height: 12 },
    "14": { width: 14, height: 14 },
    "16": { width: 16, height: 16 },
    "18": { width: 18, height: 18 },
    "20": { width: 20, height: 20 },
    "22": { width: 22, height: 22 },
    "30": { width: 30, height: 30 },
  } as const;
  return preset[size.value] ?? { width: 12, height: 12 };
});
</script>
