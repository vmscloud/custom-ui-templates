<template>
  <div class="moz-controller-root popup-controller">
    <div
      class="moz-horizontal-filter moz-controller-filter"
      :style="{
        width: `${typeof width === 'number' ? width + 'px' : width}`,
        height: `${typeof height === 'number' ? height + 'px' : height}`,
      }"
    >
      <slot name="filter"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from 'vue';

interface Props {
  width?: string | number;
  height?: string | number;
}

/**
 * props
 */
const props = defineProps<Props>();
const { width, height } = toRefs(props);
</script>
<style lang="scss" scoped>
.moz-controller-root {
  .moz-horizontal-filter {
    border-radius: 0px;
    padding: 10px 10px;
    background-color: #f5f7fc;
    border: 1px solid #cad4e5;
    gap: 6px;
    position: relative;

    &.moz-horizontal-filter {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
    }
  }
}
</style>
