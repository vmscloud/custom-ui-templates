<template>
  <div
    ref="minSizeRef"
    :style="{
      position: 'fixed',
      width: minWidth ? (typeof minWidth === 'number' ? minWidth + 'px' : minWidth) : '100px',
      height: minHeight ? (typeof minHeight === 'number' ? minHeight + 'px' : minHeight) : '100px',
    }"
    class="drawer-size-calculator"
  />
  <div
    ref="maxSizeRef"
    :style="{
      position: 'fixed',
      width: maxWidth ? (typeof maxWidth === 'number' ? maxWidth + 'px' : maxWidth) : '100%',
      height: maxHeight ? (typeof maxHeight === 'number' ? maxHeight + 'px' : maxHeight) : '100%',
    }"
    class="drawer-size-calculator"
  />
  <div
    ref="edgeWrapperRef"
    :class="[
      'extended-window-edge-wrapper',
      `extended-window-edge-wrapper-from__${windowKey}${minorKey}`,
      `extended-window__${windowKey}${minorKey}`,
      `extended-window-edge-wrapper__${position}`,
    ]"
    :data-isFloat="float"
    :data-position="position"
  >
    <div
      v-if="resizable"
      @mousedown="startResize"
      :class="[`extended-window-edge-dragbar`, `extended-window-edge-dragbar__${position}`]"
    />
    <!--    <div v-if="position === 'right' || position === 'bottom'"></div>-->
    <div
      ref="edgeRef"
      :class="['extended-window-edge', `extended-window__${windowKey}${minorKey}`, `extended-window-edge__${position}`]"
      :style="[
        {
          display: 'flex',
          flexDirection: stackDirResult === 'horizontal' ? 'row' : 'column',
          pointerEvents: 'auto',
        },
      ]"
      @mouseleave="mouseLeaveHandler"
      @mouseover="
        (e) => {
          emitDataHandler(e, position);
        }
      "
      @mouseenter="
        (e) => {
          emitDataHandler(e, position);
        }
      "
      :data-isFloat="float"
      :data-stackDir="stackDirResult"
      :data-position="position"
    ></div>

    <!--    <div v-if="position === 'left' || position === 'top'"></div>-->
  </div>
</template>
<script setup lang="ts">
import { inject, nextTick, Ref, ref, toRefs, watch } from 'vue';

type propsType = {
  windowKey: string;
  minorKey?: string;
  position: 'left' | 'right' | 'top' | 'bottom';
  emitDataHandler: (e: any, position: any) => any;
  resizable?: boolean;
  width?: number | string;
  height?: number | string;
  minWidth?: number | string;
  minHeight?: number | string;
  maxWidth?: number | string;
  maxHeight?: number | string;
  float?: boolean;
  stackDir?: 'horizontal' | 'vertical';
  priorityWeight?: number;
};

const props = withDefaults(defineProps<propsType>(), {
  width: 'auto',
  height: 'auto',
  minWidth: '18px',
  minHeight: '18px',
  maxWidth: '20%',
  maxHeight: '48px',
  resizable: true,
  float: false,
  priorityWeight: 5,
});

const {
  windowKey,
  minorKey,
  position,
  emitDataHandler,
  resizable,
  minWidth,
  minHeight,
  maxWidth,
  maxHeight,
  width,
  height,
  float,
  stackDir,
  priorityWeight,
} = toRefs(props);

const { loadPosition, saveLayout } = inject('extended-window-provide') as any;

const edgeRef = ref();
const edgeWrapperRef = ref();
const isResizing = ref(false);
const startX = ref(0);
const startWidth = ref(0);
const startY = ref(0);
const startHeight = ref(0);
const minSizeRef = ref();
const maxSizeRef = ref();
const stackDirResult = ref(
  stackDir.value || (position.value === 'top' || position.value === 'bottom' ? 'horizontal' : 'vertical'),
);

const getSize = (dimension: Ref<number | string> | undefined) => {
  if (!dimension?.value) return 'auto';
  return typeof dimension.value === 'number' ? `${dimension.value}px` : dimension.value;
};

const initialWidth = getSize(width);
const initialHeight = getSize(height);

const startResize = (e: any) => {
  if (!resizable.value) return;
  e.preventDefault();
  isResizing.value = true;
  startX.value = e.clientX;
  startY.value = e.clientY;
  startWidth.value = edgeWrapperRef.value.clientWidth;
  startHeight.value = edgeWrapperRef.value.clientHeight;
  const window = document.querySelector(`.extended-window__${windowKey.value}${minorKey.value}`)!;
  window.addEventListener('mousemove', resize);
  window.addEventListener('mouseup', stopResize);
};

const resize = (e: any) => {
  if (isResizing.value) {
    const calculated = {
      newWidth:
        position.value === 'right'
          ? startWidth.value - (e.clientX - startX.value)
          : startWidth.value + (e.clientX - startX.value),
      newHeight:
        position.value === 'bottom'
          ? startHeight.value - (e.clientY - startY.value)
          : startHeight.value + (e.clientY - startY.value),
      minWidth: minSizeRef.value.clientWidth,
      maxWidth: maxSizeRef.value.clientWidth,
      minHeight: minSizeRef.value.clientHeight,
      maxHeight: maxSizeRef.value.clientHeight,
    };

    if (position.value === 'left' || position.value === 'right') {
      let targetWidth = calculated.newWidth;
      if (calculated.newWidth > calculated.minWidth && calculated.newWidth < calculated.maxWidth) {
        targetWidth = calculated.newWidth;
      } else if (calculated.newWidth < calculated.minWidth) {
        targetWidth = calculated.minWidth;
      } else if (calculated.newWidth > calculated.maxWidth) {
        targetWidth = calculated.maxWidth;
      }
      edgeWrapperRef.value.style.width = `${targetWidth}px`;
      // edgeWrapperRef.value.style.width = 'fit-content';
      // edgeWrapperRef.value.querySelectorAll('.extended-window__instance')!.forEach((el: HTMLDivElement) => {
      //   el.style.width = `${targetWidth}px`;
      // });
    }

    if (position.value === 'top' || position.value === 'bottom') {
      let targetHeight = calculated.newHeight;
      if (calculated.newHeight > calculated.minHeight && calculated.newHeight < calculated.maxHeight) {
        targetHeight = calculated.newHeight;
      } else if (calculated.newHeight < calculated.minHeight) {
        targetHeight = calculated.minHeight;
      } else if (calculated.newHeight > calculated.maxHeight) {
        targetHeight = calculated.maxHeight;
      }
      edgeWrapperRef.value.style.height = `${targetHeight}px`;
      // edgeWrapperRef.value.style.height = 'fit-content';
      // edgeWrapperRef.value.querySelectorAll('.extended-window__instance')!.forEach((el: HTMLDivElement) => {
      //   el.style.height = `${targetHeight}px`;
      // });
    }
  }
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', resize);
  document.removeEventListener('mouseup', stopResize);
  nextTick(() => {
    saveLayout();
  });
};

const mouseLeaveHandler = () => {
  if (edgeRef.value.childNodes.length < 1) {
    edgeWrapperRef.value.style.width = 'auto';
    edgeWrapperRef.value.style.height = 'auto';
  }
};

watch(
  [loadPosition],
  async () => {
    if (!edgeWrapperRef.value) return;
    // alert(`${JSON.stringify(loadPosition.value)}`)
    const posInfoIndex = loadPosition.value.findIndex((p: any) => p.key === position.value);
    const posInfo = loadPosition.value[posInfoIndex];

    if (!posInfo) return;
    if (posInfo.applied) return;
    if (posInfoIndex > 0 && !loadPosition.value[posInfoIndex - 1].applied) {
      return;
    }

    if (position.value === 'left' || position.value === 'right') {
      edgeWrapperRef.value.style.width = `${posInfo.width || width.value}px`;
    }
    if (position.value === 'top' || position.value === 'bottom') {
      edgeWrapperRef.value.style.height = `${posInfo.height || height.value}px`;
    }

    posInfo.applied = true;
    // applyLayoutWatch();
    // popLeftLoadPosition();
  },
  { deep: true, flush: 'post', immediate: true },
);
</script>
<style lang="less" scoped>
@use 'ExtendedWindow.scss';

.extended-window-edge-wrapper {
  position: relative;
  z-index: v-bind(priorityWeight);
  max-width: 100%;
  max-height: 100%;

  &[data-isFloat='true'] {
    background-color: unset;
    pointer-events: none;
    position: absolute;

    &[data-position='right'] {
      right: 0;
    }
    &[data-position='bottom'] {
      bottom: 0;
    }
  }

  &[data-isFloat='false'] {
    pointer-events: auto;
    position: relative;
  }
}

.extended-window-edge-wrapper__left,
.extended-window-edge-wrapper__right {
  width: auto;
  &:has(.extended-window__instance[data-isVisible='true']) {
    width: v-bind(initialWidth);
  }

  display: flex;

  &[data-isFloat='false']:has(.extended-window__instance[data-isVisible='true']) {
    // box-shadow: 0px 0px 10px 1px rgba(0, 0, 0, 0.15);
  }
}

.extended-window-edge-wrapper__top,
.extended-window-edge-wrapper__bottom {
  height: auto;

  &:has(.extended-window__instance[data-isVisible='true']) {
    height: v-bind(initialHeight);
  }

  display: flex;
  flex-direction: column;

  &[data-isFloat='false']:has(.extended-window__instance[data-isVisible='true']) {
    // box-shadow: 0px 0px 10px 1px rgba(0, 0, 0, 0.15);
  }
}

.extended-window-edge-wrapper__right[data-stackDir='vertical'],
.extended-window-edge-wrapper__bottom[data-stackDir='horizontal'] {
  align-items: flex-end;
}

.extended-window-edge-wrapper__right[data-stackDir='horizontal'],
.extended-window-edge-wrapper__bottom[data-stackDir='vertical'] {
  justify-content: flex-end;
}

.extended-window-edge {
  &[data-isFloat='false'] {
    outline: 1px solid #c1c1d8;
    // box-shadow: 0px 0px 0px 1px #c1c1d8;
  }
  &[data-isFloat='true'] {
    padding: 1px;
  }
  position: relative;

  //z-index: 9;
}

.extended-window-edge__left,
.extended-window-edge__right {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

.extended-window-edge__top,
.extended-window-edge__bottom {
  width: 100%;
  height: 100%;
  overflow-y: hidden;
  overflow-x: auto;
}

.extended-window-edge-dragbar {
  position: absolute;
  z-index: 2000;
  pointer-events: auto;
  // transition-property: width height left top;
  // transition-duration: 0.1s;
}

.extended-window-edge-dragbar__top,
.extended-window-edge-dragbar__bottom {
  &:hover {
    height: 8px;
    background-color: #e1e7fa;
  }
}
.extended-window-edge-dragbar__left,
.extended-window-edge-dragbar__right {
  &:hover {
    width: 8px;
    background-color: #e1e7fa;
    //box-shadow: 0px 0px 0px 1px #c1c1d8;
  }
}

.extended-window-edge-dragbar__top {
  width: 100%;
  height: 2px;
  cursor: row-resize;
  bottom: 0px;
  &:hover {
    bottom: -4px;
  }
}

.extended-window-edge-dragbar__bottom {
  width: 100%;
  height: 2px;
  cursor: row-resize;
  &:hover {
    top: -4px;
  }
}

.extended-window-edge-dragbar__left {
  width: 2px;
  height: 100%;
  cursor: col-resize;
  right: 0px;
  &:hover {
    right: -4px;
  }
}

.extended-window-edge-dragbar__right {
  width: 2px;
  height: 100%;
  cursor: col-resize;
  left: 0;

  &:hover {
    left: -4px;
  }
}

.drawer-size-calculator {
  position: absolute;
  pointer-events: none;
  visibility: hidden;
}

.extended-window-edge-wrapper:not(:has(.extended-window__instance[data-isvisible='true'])) {
  // visible 상태인 instance가 없을때도 width, height를 유지해야만 레이아웃 저장시 width, height를 저장하므로, width: 100%; height: 100%;가 아닌 아래와 같이 처리
  position: absolute;

  // absolute 상태에서는 다시 left, top값을 지정해줘야 함. 그 이유는 instance가 드래그중 어느 edge에 있는지 파악하는데 if ~ else if를 사용하기 때문에, 실제와 다른 edge에 존재한다는 조건이 우선적으로 부합하면 안되기 때문.
  &[data-position='left'] {
    height: 100%;
    left: 0;
  }
  &[data-position='right'] {
    height: 100%;
    left: 100%;
  }
  &[data-position='top'] {
    width: 100%;
    top: 0;
  }
  &[data-position='bottom'] {
    width: 100%;
    top: 100%;
  }
}
</style>
