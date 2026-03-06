<template>
  <teleport to="body">
    <div
      v-if="useInfoModal.open.value"
      :class="['simple-floating-modal', 'is-open', `modal-${props.storeKey}`]"
      :style="[dialogStyle, { opacity: useInfoModal.opacity.value }]"
      ref="dialog"
    >
      <InfoPanel :storeKey="props.storeKey">
        <template #title>
          <div class="title-container" @mousedown="onMouseDown">
            <slot name="title">Simple Modal</slot>
          </div>
        </template>
        <template #content>
          <slot name="content"></slot>
        </template>
      </InfoPanel>

      <div v-if="USE_RESIZE" class="resize-handler-bottom" @mousedown="onResizeMouseDownBottom"></div>
      <div v-if="USE_RESIZE" class="resize-handler-right" @mousedown="onResizeMouseDownRight"></div>
      <div v-if="USE_RESIZE" class="resize-handler-bottom-right" @mousedown="onResizeMouseDown"></div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { bindDropDownEvents, pxToRem, unbindDropDownEvents } from '@moz-shared/utils';
import { computed, inject, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import InfoPanel from './InfoPanel.vue';

// Props 정의
interface Props {
  storeKey?: string;
}

const props = withDefaults(defineProps<Props>(), {
  storeKey: 'useInfoModal', // 기본값
});

const MODAL_MIN_WIDTH = 400;
const MODAL_MIN_HEIGHT = 300;
const MODAL_MAX_WIDTH = 1400;
const MODAL_MAX_HEIGHT = 600;
const dialog = ref<HTMLElement>();
const USE_DRAG = true;
const USE_RESIZE = true;

const useInfoModal = inject(props.storeKey) as any;
const { open: _open, left: _left, top: _top, width: _width, height: _height, opacity: _opacity } = useInfoModal;

const dialogStyle = computed(() => ({
  position: 'fixed' as const,
  top: `${useInfoModal.top.value}px`,
  left: `${useInfoModal.left.value}px`,
  width: useInfoModal.width.value ? `${pxToRem(useInfoModal.width.value)}rem` : undefined,
  height: useInfoModal.height.value ? `${pxToRem(useInfoModal.height.value)}rem` : undefined,
  zIndex: '99999',
}));

const overEvent = ref<any | null>(null);

// touch 객체를 reactive로 만들어서 각 인스턴스마다 독립적으로 생성
const touch = reactive({
  mouseDown: false,
  dragging: false,
  offset: { x: 0, y: 0 },
});

// 드래그 시작
const startMove = (event: MouseEvent) => {
  touch.mouseDown = true;
  touch.offset.x = event.clientX - useInfoModal.left.value;
  touch.offset.y = event.clientY - useInfoModal.top.value;
};

function adjustPositionToBounds(targetLeft: number, targetTop: number) {
  const modalWidth = useInfoModal.width.value || MODAL_MIN_WIDTH;
  const modalHeight = useInfoModal.height.value || MODAL_MIN_HEIGHT;
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;

  // 최소값: 0, 최대값: 브라우저 크기 - 모달 크기
  const adjustedLeft = Math.max(0, Math.min(targetLeft, viewportWidth - modalWidth));
  const adjustedTop = Math.max(0, Math.min(targetTop, viewportHeight - modalHeight));

  return { left: adjustedLeft, top: adjustedTop };
}

// open이 true로 바뀌는 순간 위치 보정
watch(useInfoModal.open, (val) => {
  if (val) {
    nextTick(() => {
      const { left: newLeft, top: newTop } = adjustPositionToBounds(useInfoModal.left.value, useInfoModal.top.value);
      useInfoModal.left.value = newLeft;
      useInfoModal.top.value = newTop;
    });
  }
});

// 드래그 이동 시에도 보정
const move = (event: MouseEvent) => {
  if (touch.mouseDown) {
    const modalWidth = useInfoModal.width.value || MODAL_MIN_WIDTH;
    const modalHeight = useInfoModal.height.value || MODAL_MIN_HEIGHT;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let newLeft = event.clientX - touch.offset.x;
    let newTop = event.clientY - touch.offset.y;

    // 최소값: 0, 최대값: 브라우저 크기 - 모달 크기
    newLeft = Math.max(0, Math.min(newLeft, viewportWidth - modalWidth));
    newTop = Math.max(0, Math.min(newTop, viewportHeight - modalHeight));

    useInfoModal.left.value = newLeft;
    useInfoModal.top.value = newTop;
  }
};

const onMouseMove = (event: MouseEvent) => {
  if (event.clientX !== 0 && event.clientY !== 0) {
    overEvent.value = event;
  }
  if (touch.mouseDown && USE_DRAG) {
    touch.dragging = true;
    move(event);
  }
};

const onMouseUp = () => {
  touch.mouseDown = false;

  // 드래그 종료 시 모달이 뷰포트 밖에 있으면 위치 보정
  const { left: newLeft, top: newTop } = adjustPositionToBounds(useInfoModal.left.value, useInfoModal.top.value);
  useInfoModal.left.value = newLeft;
  useInfoModal.top.value = newTop;

  setTimeout(() => {
    touch.dragging = false;
    unbindDropDownEvents(onMouseUp, onMouseMove);
  }, 100);
};

const onMouseDown = (event: any) => {
  if (USE_DRAG) {
    event.preventDefault();
    startMove(event);
    bindDropDownEvents(onMouseUp, onMouseMove);
  }
};

// 리사이즈 핸들러 함수 복원
const onResizeMouseDown = (event: MouseEvent): void => {
  event.preventDefault();
  const initialWidth: number | undefined = useInfoModal.width.value;
  const initialHeight: number | undefined = useInfoModal.height.value;
  if (!initialWidth || !initialHeight) return;

  const startMousePosition = { x: event.clientX, y: event.clientY };

  const onResizeMouseMove = (moveEvent: MouseEvent): void => {
    const dx: number = moveEvent.clientX - startMousePosition.x;
    const dy: number = moveEvent.clientY - startMousePosition.y;

    let newWidthPx: number = Math.max(MODAL_MIN_WIDTH, Math.min(initialWidth + dx, MODAL_MAX_WIDTH));
    let newHeightPx: number = Math.max(MODAL_MIN_HEIGHT, Math.min(initialHeight + dy, MODAL_MAX_HEIGHT));

    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    if (useInfoModal.left.value + newWidthPx > viewportWidth) {
      newWidthPx = viewportWidth - useInfoModal.left.value;
    }
    if (useInfoModal.top.value + newHeightPx > viewportHeight) {
      newHeightPx = viewportHeight - useInfoModal.top.value;
    }

    useInfoModal.width.value = newWidthPx;
    useInfoModal.height.value = newHeightPx;
  };

  const onResizeMouseUp = (): void => {
    document.removeEventListener('mousemove', onResizeMouseMove);
    document.removeEventListener('mouseup', onResizeMouseUp);
  };

  document.addEventListener('mousemove', onResizeMouseMove);
  document.addEventListener('mouseup', onResizeMouseUp);
};

const onResizeMouseDownBottom = (event: MouseEvent): void => {
  event.preventDefault();
  const initialHeight: number | undefined = useInfoModal.height.value;
  if (!initialHeight) return;

  const startMousePosition = { y: event.clientY };

  const onResizeMouseMoveBottom = (moveEvent: MouseEvent): void => {
    const dy: number = moveEvent.clientY - startMousePosition.y;
    let newHeightPx: number = Math.max(MODAL_MIN_HEIGHT, Math.min(initialHeight + dy, MODAL_MAX_HEIGHT));

    const viewportHeight = window.innerHeight;
    if (useInfoModal.top.value + newHeightPx > viewportHeight) {
      newHeightPx = viewportHeight - useInfoModal.top.value;
    }

    useInfoModal.height.value = newHeightPx;
  };

  const onResizeMouseUpBottom = (): void => {
    document.removeEventListener('mousemove', onResizeMouseMoveBottom);
    document.removeEventListener('mouseup', onResizeMouseUpBottom);
  };

  document.addEventListener('mousemove', onResizeMouseMoveBottom);
  document.addEventListener('mouseup', onResizeMouseUpBottom);
};

const onResizeMouseDownRight = (event: MouseEvent): void => {
  event.preventDefault();
  const initialWidth: number | undefined = useInfoModal.width.value;
  if (!initialWidth) return;

  const startMousePosition = { x: event.clientX };

  const onResizeMouseMoveRight = (moveEvent: MouseEvent): void => {
    const dx: number = moveEvent.clientX - startMousePosition.x;
    let newWidthPx: number = Math.max(MODAL_MIN_WIDTH, Math.min(initialWidth + dx, MODAL_MAX_WIDTH));

    const viewportWidth = window.innerWidth;
    if (useInfoModal.left.value + newWidthPx > viewportWidth) {
      newWidthPx = viewportWidth - useInfoModal.left.value;
    }

    useInfoModal.width.value = newWidthPx;
  };

  const onResizeMouseUpRight = (): void => {
    document.removeEventListener('mousemove', onResizeMouseMoveRight);
    document.removeEventListener('mouseup', onResizeMouseUpRight);
  };

  document.addEventListener('mousemove', onResizeMouseMoveRight);
  document.addEventListener('mouseup', onResizeMouseUpRight);
};

onMounted(() => {
  if (useInfoModal.open.value) {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const modalW = useInfoModal.width.value ? useInfoModal.width.value : MODAL_MIN_WIDTH;
    const modalH = useInfoModal.height.value ? useInfoModal.height.value : MODAL_MIN_HEIGHT;
    useInfoModal.left.value = (vw - modalW) / 2;
    useInfoModal.top.value = (vh - modalH) / 2;
  }
});

onBeforeUnmount(() => {
  unbindDropDownEvents(onMouseUp, onMouseMove);
});
</script>

<style lang="scss" scoped>
.title-container {
  width: 100%;
}

.simple-floating-modal {
  position: fixed;
  z-index: 9999 !important;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-radius: 0.5rem;
  background-color: #ffffff;

  &.is-open {
    opacity: 1;
    transform: scale(1);
  }

  .resize-handler-bottom {
    position: absolute;
    bottom: -3px;
    left: 0;
    right: 10px;
    height: 6px;
    cursor: ns-resize;
    z-index: 10;
  }

  .resize-handler-right {
    position: absolute;
    top: 0;
    right: -3px;
    bottom: 10px;
    width: 6px;
    cursor: ew-resize;
    z-index: 10;
  }

  .resize-handler-bottom-right {
    position: absolute;
    bottom: -3px;
    right: -3px;
    width: 10px;
    height: 10px;
    cursor: nwse-resize;
    z-index: 11;
  }
}
</style>
