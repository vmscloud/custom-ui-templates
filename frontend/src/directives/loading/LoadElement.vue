<template>
  <div class="load-element-outer-wrapper" v-show="shouldShow">
    <div class="load-element-inner-wrapper" ref="wrapperRef">
      <div class="load-element-panel" style="width: 64px; height: 64px">
        <svg class="svg-container" viewBox="0 0 100 100">
          <circle class="loader-svg bg" cx="50" cy="50" r="45"></circle>
          <circle class="loader-svg animate" cx="50" cy="50" r="45"></circle>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, Ref, ref, toRefs, watch } from 'vue';

type propsType = {
  isLoading: Ref<boolean>;
  parentEl: HTMLElement;
  delay?: number;
};
const props = withDefaults(defineProps<propsType>(), {
  delay: 300,
});
const { isLoading, parentEl, delay } = toRefs(props);
const wrapperRef = ref();

const domObserver = new ResizeObserver((entries) => {
  if (!wrapperRef.value) return;
  for (const entry of entries) {
    const cr = entry.contentRect;
    wrapperRef.value.style.width = `${cr.width}px`;
    wrapperRef.value.style.height = `${cr.height}px`;
  }
});

onMounted(() => {
  if (parentEl.value) {
    domObserver.observe(parentEl.value);
  }
});

onBeforeUnmount(() => {
  domObserver.disconnect();
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
});

const shouldShow = ref(isLoading.value);
let timer: ReturnType<typeof setTimeout> | null = null;

watch(props.isLoading, (newVal) => {
  if (newVal) {
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      shouldShow.value = true;
    }, delay.value);
  } else {
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
    shouldShow.value = false;
  }
});
</script>

<style lang="scss" scoped>
.load-element-outer-wrapper {
  width: 0;
  height: 0;
  position: relative;
  overflow: visible;

  .load-element-inner-wrapper {
    background-color: rgba(255, 255, 255, 1);
    position: absolute;
    z-index: 10;
    top: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.loader-svg {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  fill: none;
  stroke-width: 10px;
  stroke-linecap: round;
  stroke: #4568e0;

  &.bg {
    stroke-width: 10px;
    stroke: #e9edf4;
  }

  &.animate {
    stroke-dasharray: 242.6;
    animation: fill-animation 1s cubic-bezier(1, 1, 1, 1) 0s infinite;
  }
}

@keyframes fill-animation {
  0% {
    stroke-dasharray: 40 242.6;
    stroke-dashoffset: 282.6;
  }
  50% {
    stroke-dasharray: 141.3;
    stroke-dashoffset: 141.3;
  }
  100% {
    stroke-dashoffset: 0;
    stroke-dasharray: 40 242.6;
  }
}
</style>
