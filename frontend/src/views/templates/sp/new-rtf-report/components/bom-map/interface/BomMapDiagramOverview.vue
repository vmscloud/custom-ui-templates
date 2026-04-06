<template>
  <div :class="['bom-map-overview-wrapper']" :style="{ opacity: `${interfaceConfigs.window.overview.opacity}%` }">
    <div class="bom-map-window-title-wrapper">
      {{ t('text-upper-bom_map_overview') }}
      <div class="bom-map-window-title-right">
        <input
          @mousedown="(e) => e.stopPropagation()"
          type="range"
          min="30"
          max="100"
          value="50"
          class="bom-map-window-slider"
          v-model="interfaceConfigs.window.overview.opacity"
        />
        <IconClose style="cursor: pointer" @mousedown="closeHandler" />
      </div>
    </div>

    <div :class="['bom-map-overview-middle-wrapper']">
      <div class="bom-map-overview-floating-btn" @click="scrollToDirection('upLeft')">↖</div>
      <div class="bom-map-overview-floating-btn" @click="scrollToDirection('upRight')" style="right: 0">↗</div>
      <div class="bom-map-overview-floating-btn" @click="scrollToDirection('downLeft')" style="bottom: 0">↙</div>
      <div class="bom-map-overview-floating-btn" @click="scrollToDirection('downRight')" style="bottom: 0; right: 0">
        ↘
      </div>

      <div class="bom-map-overview-floating-btn" @click="scrollToDirection('up')" style="left: calc(50% - 28px)">↑</div>
      <div class="bom-map-overview-floating-btn" @click="scrollToDirection('left')" style="top: calc(50% - 28px)">
        ←
      </div>
      <div
        class="bom-map-overview-floating-btn"
        @click="scrollToDirection('right')"
        style="right: 0; top: calc(50% - 28px)"
      >
        →
      </div>
      <div
        class="bom-map-overview-floating-btn"
        @click="scrollToDirection('down')"
        style="bottom: 0; left: calc(50% - 28px)"
      >
        ↓
      </div>
      <div :class="['bom-map-overview-scroll-wrapper']" ref="overviewScrollWrapperRef">
        <div
          :class="['bom-map-overview-inner-wrapper']"
          :style="{ width: computedWidth + 'px', height: computedHeight + 'px' }"
        >
          <div :id="`bom-map-overview`" :class="['bom-map-overview']" />
        </div>
      </div>
    </div>

    <div class="bom-map-overview-zoom-wrapper">
      <IconSearch />
      <label>{{ t('text-bom_map-zoom_overview') }}</label>
      <input
        @mousedown="(e) => e.stopPropagation()"
        type="range"
        min="0.1"
        max="25.1"
        value="1"
        class="bom-map-overview-slider"
        v-model="zoom"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { IconClose, IconSearch } from '@moz-shared/icons';
import { Diagram, Overview } from 'gojs';
import { useTranslation } from 'i18next-vue';
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, toRefs, watch } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';

type propsType = {
  getDiagram?: () => Diagram;
  initOverview?: () => Overview;
};

const props = defineProps<propsType>();
const { getDiagram, initOverview } = toRefs(props);

const { interfaceConfigs } = inject('useBomMapInterface') as IBomMapIntefaceQuery;
const { t } = useTranslation(); // 다국어

const width = ref(0);
const height = ref(0);
const zoom = ref(0.1);
const overviewScrollWrapperRef = ref();

const computedWidth = computed(() => width.value * (zoom.value / 100));

const computedHeight = computed(() => height.value * (zoom.value / 100));

let myDiagram: any;
let myOverview: any;

watch(
  [getDiagram],
  () => {
    if (getDiagram.value) {
      myDiagram = getDiagram.value();

      nextTick(() => {
        updateDiagramSize();
        myDiagram.addDiagramListener('ViewportBoundsChanged', updateDiagramSize);
      });
      nextTick(() => {
        if (!initOverview.value) return;
        myOverview = initOverview.value() as Overview;
        myOverview.div.querySelector('canvas')?.addEventListener('wheel', onWheelHandler);
        // myOverview.div.addEventListener('wheel', onWheelHandler)
      });
    }
  },
  { flush: 'post' },
);

onMounted(() => {});
watch(
  [zoom],
  () => {
    myOverview.redraw();
  },
  { flush: 'post' },
);

onBeforeUnmount(() => {
  myDiagram?.removeDiagramListener('ViewportBoundsChanged', updateDiagramSize);
  myOverview?.div?.querySelector('canvas')?.removeEventListener('wheel', onWheelHandler);
});

function updateDiagramSize() {
  if (!myDiagram) return;
  const bounds = myDiagram.documentBounds;
  width.value = bounds.width;
  height.value = bounds.height;
}

function scrollToDirection(
  direction: 'up' | 'down' | 'left' | 'right' | 'upLeft' | 'upRight' | 'downLeft' | 'downRight' | 'center',
) {
  if (!myDiagram) return;
  const viewBounds = myDiagram.documentBounds;
  const viewportSize = myDiagram.viewportBounds.size;

  const targetPosition = myDiagram.position.copy();

  if (direction.includes('down')) {
    overviewScrollWrapperRef.value.scrollTop =
      overviewScrollWrapperRef.value.scrollHeight - overviewScrollWrapperRef.value.clientHeight;
  }
  if (direction.includes('up')) {
    overviewScrollWrapperRef.value.scrollTop = 0;
  }
  if (direction.includes('left')) {
    overviewScrollWrapperRef.value.scrollLeft = 0;
  }
  if (direction.includes('right')) {
    overviewScrollWrapperRef.value.scrollLeft =
      overviewScrollWrapperRef.value.scrollWidth - overviewScrollWrapperRef.value.clientWidth;
  }

  switch (direction) {
    case 'up':
      targetPosition.y = viewBounds.top;
      break;
    case 'down':
      targetPosition.y = viewBounds.bottom - viewportSize.height;
      break;
    case 'left':
      targetPosition.x = viewBounds.left;
      break;
    case 'right':
      targetPosition.x = viewBounds.right - viewportSize.width;
      break;
    case 'upLeft':
      targetPosition.x = viewBounds.left;
      targetPosition.y = viewBounds.top;
      break;
    case 'upRight':
      targetPosition.x = viewBounds.right - viewportSize.width;
      targetPosition.y = viewBounds.top;
      break;
    case 'downLeft':
      targetPosition.x = viewBounds.left;
      targetPosition.y = viewBounds.bottom - viewportSize.height;
      break;
    case 'downRight':
      targetPosition.x = viewBounds.right - viewportSize.width;
      targetPosition.y = viewBounds.bottom - viewportSize.height;
      break;
    case 'center':
      targetPosition.x = (viewBounds.width - viewportSize.width) / 2 + viewBounds.x;
      targetPosition.y = (viewBounds.height - viewportSize.height) / 2 + viewBounds.y;
      break;
    default:
      console.warn(`Unknown direction: ${direction}`);
      return;
  }

  myDiagram.position = targetPosition;
}

const closeHandler = () => {
  interfaceConfigs.value.window.overview.isShown = false;
};

const onWheelHandler = (e: any) => {
  if (!e.ctrlKey) return;
  if (e.deltaY > 0 && zoom.value > 0.1) {
    zoom.value = zoom.value - 1;
  }
  if (e.deltaY < 0 && zoom.value < 25.1) {
    zoom.value = zoom.value + 1;
  }
};
</script>
<style lang="scss" scoped>
.bom-map-overview-wrapper {
  z-index: 10;
  position: absolute;
  right: 0px;
  top: 0px;
  background-color: white;
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
}

.extended-window-edge__right[data-isfloat='true'] {
  .extended-window__instance-right[data-isvisible='true'] {
    .extended-window__instance-body-right {
      .bom-map-overview-wrapper {
        height: 400px;
      }
    }
  }
}

.extended-window-edge__right[data-isfloat='false'] {
  .extended-window__instance-right[data-isvisible='true'] {
    .extended-window__instance-body-right {
      .bom-map-overview-wrapper {
        height: 100%;
        min-height: 240px;
        max-height: 600px;
      }
    }
  }
}

.extended-window__instance-body-float {
  .bom-map-overview-wrapper {
    width: 500px;
    height: 400px;
  }
}

.bom-map-overview-middle-wrapper {
  position: relative;
  flex: 1;
  overflow: hidden;
}
.bom-map-overview-scroll-wrapper {
  width: 100%;
  height: 100%;
  overflow: auto;

  display: grid;
  grid-template-columns: 100%;
  grid-template-rows: 100%;
}

.bom-map-overview-inner-wrapper {
  min-width: 100% !important;
  min-height: 100% !important;
}

:deep(.extended-window-edge) {
  .bom-map-overview-wrapper {
    width: 100%;
    // min-width: 220px;
  }
}

.bom-map-overview {
  width: 100% !important;
  height: 100% !important;

  & > * {
    //filter: saturate(500%) invert(10%);
  }

  & * {
    overflow: hidden !important;
  }
}

.bom-map-overview-zoom-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;

  & label {
    color: #6a7184;
    font-size: 12px;
  }
}
.bom-map-overview-slider {
  outline: 0;
  outline: 1px solid #bac6d4;
  border-radius: 500px;
  flex: 1;
  transition: box-shadow 0.2s ease-in-out;
  cursor: ew-resize;
}

.bom-map-overview-slider[type='range'] {
  overflow: hidden;
  height: 8px;
  -webkit-appearance: none;
  background-color: rgba(129, 146, 215, 0.5);

  &:hover::-webkit-slider-thumb {
    background: #4568e0;
    box-shadow:
      -305px 0 0 300px #4568e0,
      inset 0 0 0 40px #ffffff;
  }
}

.bom-map-overview-slider[type='range']::-webkit-slider-runnable-track {
  height: 8px;
  -webkit-appearance: none;
  color: #444;
  -webkit-transition: box-shadow 0.5s ease-in-out;
  transition: box-shadow 0.5s ease-in-out;
}

.bom-map-overview-slider[type='range']::-webkit-slider-thumb {
  width: 8px;
  -webkit-appearance: none;
  height: 8px;
  background: #4568e0;
  box-shadow: -305px 0 0 300px #4568e0;
  border-radius: 50%;
  -webkit-transition: box-shadow 0.2s ease-in-out;
  transition: box-shadow 0.2s ease-in-out;
  position: relative;
}

.bom-map-overview-slider[type='range']:active::-webkit-slider-thumb {
  background: #4568e0;
  box-shadow:
    -305px 0 0 300px #4568e0,
    inset 0 0 0 40px #ffffff;
}

.bom-map-overview-floating-btn {
  position: absolute;
  opacity: 50%;
  border: 1px solid #c1c1d8;
  background-color: white;
  border-radius: 100%;
  width: 28px;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  line-height: 100%;
  user-select: none;
  cursor: pointer;
  color: #434c60;
  margin: 12px;
  z-index: 10000;

  &:hover {
    opacity: 100%;
  }
}
</style>
