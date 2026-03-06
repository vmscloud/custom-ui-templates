<template>
  <div class="simple-modal-panel" :style="{ opacity: opacity }">
    <div class="simple-modal-panel-title">
      <div class="title" @mousedown="onMouseDown" @touchstart="onMouseDown">
        <slot name="title">{{ '' }}</slot>
      </div>
      <div class="actions">
        <input
          @mousedown="(e) => e.stopPropagation()"
          type="range"
          min="50"
          max="100"
          v-model="sliderValue"
          class="info-modal-window-slider"
        />
        <button
          @click="
            () => {
              useInfoModal.modalClose();
            }
          "
        >
          <IconClose size="12" />
        </button>
      </div>
    </div>
    <div class="simple-modal-panel-content">
      <slot name="content">
        <div class="default-content">
          <p>{{ '' }}</p>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { IconClose } from '@moz-shared/icons';
import { bindDropDownEvents, unbindDropDownEvents } from '@moz-shared/utils';
import { inject, onBeforeUnmount, ref, watch } from 'vue';

// Props 정의
interface Props {
  storeKey?: string;
}

const props = withDefaults(defineProps<Props>(), {
  storeKey: 'useInfoModal', // 기본값
});

const useInfoModal = inject(props.storeKey) as any;
const { opacity } = useInfoModal;

// 슬라이더 값 (50-100)
const sliderValue = ref(100);

// 드래그 관련 상태
const touch: {
  mouseDown: boolean;
  dragging: boolean;
  offset: { x: number; y: number };
} = {
  mouseDown: false,
  dragging: false,
  offset: { x: 0, y: 0 },
};

const overEvent = ref<any | null>(null);

// 드래그 시작
const startMove = (event: MouseEvent) => {
  touch.mouseDown = true;
  touch.offset.x = useInfoModal.left.value - event.clientX;
  touch.offset.y = useInfoModal.top.value - event.clientY;
};

// 드래그 이동
const move = (event: MouseEvent) => {
  if (event.clientX === 0 && overEvent.value) event = overEvent.value;
  if (event && event.clientX && event.clientY) {
    const newLeft = event.clientX + touch.offset.x;
    const newTop = event.clientY + touch.offset.y;
    useInfoModal.left.value = newLeft;
    useInfoModal.top.value = newTop;
  }
};

// 마우스 이동 이벤트
const onMouseMove = (event: MouseEvent) => {
  if (event.clientX !== 0 && event.clientY !== 0) {
    overEvent.value = event;
  }

  if (touch.mouseDown) {
    touch.dragging = true;
    move(event);
  }
};

// 마우스 업 이벤트
const onMouseUp = () => {
  touch.mouseDown = false;

  setTimeout(() => {
    touch.dragging = false;
    unbindDropDownEvents(onMouseUp, onMouseMove);
  }, 100);
};

// 마우스 다운 이벤트
const onMouseDown = (event: any) => {
  event.preventDefault();
  startMove(event);
  bindDropDownEvents(onMouseUp, onMouseMove);
};

watch(sliderValue, () => {
  opacity.value = sliderValue.value / 100;
});

// 컴포넌트 언마운트 시 이벤트 리스너 정리
onBeforeUnmount(() => {
  unbindDropDownEvents(onMouseUp, onMouseMove);
});
</script>

<style lang="scss" scoped>
.simple-modal-panel {
  height: 100%;
  border: #bbc6d9 solid 1px;
  border-radius: 0.5rem;
  background-color: #ffffff;
  display: grid;
  grid-template-rows: auto 1fr;
  color: #28364e;

  .simple-modal-panel-title {
    width: 100%;
    padding: 10px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: #e1e3f0 solid 1px;
    position: relative; // 드래그 핸들러 역할을 위한 position 설정

    .title {
      color: #28364e;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1; // 남은 공간을 모두 차지하도록 설정
      cursor: move; // 드래그 가능함을 표시
    }

    .actions {
      display: flex;
      align-items: center;
      gap: 8px;
      z-index: 20; // 드래그 핸들러의 z-index: 10보다 높게 설정
      pointer-events: auto; // 명시적으로 포인터 이벤트 활성화

      button {
        width: 24px;
        height: 24px;
        border-radius: 0.25rem;
        display: inline-flex;
        padding: 6px;
        justify-content: center;
        align-items: center;
        border: none;
        background: transparent;
        cursor: pointer;
        position: relative; // z-index가 올바르게 적용되도록 position 추가
        pointer-events: auto; // 버튼에도 명시적으로 포인터 이벤트 활성화

        &:hover {
          background-color: #8998b529;
        }
      }
    }
  }

  .simple-modal-panel-content {
    width: 100%;
    height: 100%;
    overflow: auto;
    padding: 25px 17px;

    .default-content {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #6a7184;
    }
  }
}

:deep(.info-modal-window-slider) {
  outline: 0;
  outline: 1px solid #bac6d4;
  border-radius: 500px;
  width: 50px;
  max-width: 100%;
  transition: box-shadow 0.2s ease-in-out;
  cursor: ew-resize;
  pointer-events: auto; // 명시적으로 포인터 이벤트 활성화
  position: relative; // z-index가 올바르게 적용되도록 position 추가
  z-index: 20; // 드래그 핸들러보다 높은 z-index
}

:deep(.info-modal-window-slider[type='range']) {
  overflow: hidden;
  height: 8px;
  -webkit-appearance: none;
  background-color: rgba(129, 146, 215, 0.5);

  &:hover::-webkit-slider-thumb {
    background: #4568e0;
    box-shadow:
      -70px 0 0 65px #4568e0,
      inset 0 0 0 40px #ffffff;
  }
}

:deep(.info-modal-window-slider[type='range']::-webkit-slider-runnable-track) {
  height: 8px;
  -webkit-appearance: none;
  color: #444;
  -webkit-transition: box-shadow 0.5s ease-in-out;
  transition: box-shadow 0.5s ease-in-out;
}

:deep(.info-modal-window-slider[type='range']::-webkit-slider-thumb) {
  width: 8px;
  -webkit-appearance: none;
  height: 8px;
  background: #4568e0;
  box-shadow: -70px 0 0 65px #4568e0;
  border-radius: 50%;
  -webkit-transition: box-shadow 0.2s ease-in-out;
  transition: box-shadow 0.2s ease-in-out;
  position: relative;
}

:deep(.info-modal-window-slider[type='range']:active::-webkit-slider-thumb) {
  background: #4568e0;
  box-shadow:
    -70px 0 0 65px #4568e0,
    inset 0 0 0 40px #ffffff;
}
</style>
