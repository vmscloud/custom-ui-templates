<template>
  <div
    :style="$attrs.style as StyleValue"
    :class="['extended-window', `extended-window__${windowKey}${minorKey}`, dirPriority]"
    :data-windowKey="windowKey"
    :data-minorKey="minorKey"
    ref="outerWindowRef"
  >
    <div :class="['extended-window-indicator', `extended-window__${windowKey}${minorKey}`]" />
    <ExtendedWindowEdge
      :windowKey="windowKey"
      :minorKey="minorKey"
      :position="dirPriority === 'horizontal' ? 'top' : 'left'"
      :emitDataHandler="emitDataHandler"
      v-bind="dirPriority === 'horizontal' ? edgeStyleTop : edgeStyleLeft"
    />
    <div :class="['extended-windows-law', dirPriority]">
      <ExtendedWindowEdge
        :windowKey="windowKey"
        :minorKey="minorKey"
        :position="dirPriority === 'horizontal' ? 'left' : 'top'"
        :emitDataHandler="emitDataHandler"
        v-bind="dirPriority === 'horizontal' ? edgeStyleLeft : edgeStyleTop"
      />
      <!--      <div class="extended-window-container-dummy" v-if="float" />-->
      <div class="extended-window-container-wrapper">
        <div
          :class="['extended-window__container', `extended-window__${windowKey}${minorKey}`]"
          @mouseenter="(e) => emitDataHandler(e, 'float')"
        >
          <slot></slot>
        </div>
      </div>
      <ExtendedWindowEdge
        :windowKey="windowKey"
        :minorKey="minorKey"
        :position="dirPriority === 'horizontal' ? 'right' : 'bottom'"
        :emitDataHandler="emitDataHandler"
        v-bind="dirPriority === 'horizontal' ? edgeStyleRight : edgeStyleBottom"
      />
    </div>
    <ExtendedWindowEdge
      :windowKey="windowKey"
      :minorKey="minorKey"
      :position="dirPriority === 'horizontal' ? 'bottom' : 'right'"
      :emitDataHandler="emitDataHandler"
      v-bind="dirPriority === 'horizontal' ? edgeStyleBottom : edgeStyleRight"
    />
  </div>

  <div class="extended-window-slot-wrapper" :data-windowKey="windowKey" :data-minorKey="minorKey" ref="windowRef">
    <slot name="window"></slot>
  </div>
</template>

<script setup lang="ts">
import { dayjs } from '@moz-shared/utils';
import { debounce } from 'es-toolkit';
import { onBeforeUnmount, onMounted, provide, ref, StyleValue, toRefs, watch } from 'vue';
import ExtendedWindowEdge from './ExtendedWindowEdge.vue';

type edgeStyle = {
  resizable?: boolean; // Edge 리사이징 가능 여부
  width?: number | string;
  height?: number | string;
  minWidth?: number | string;
  minHeight?: number | string;
  maxWidth?: number | string;
  maxHeight?: number | string;
  stackDir?: 'horizontal' | 'vertical'; // 창(Instance)가 쌓이는 방향 선택, 상하/좌우에 따라 기본값이 자동으로 설정되나, 예외적으로 필요한 경우 사용
  priorityWeight?: number; // z-index 가중치
  float?: boolean; // Edge에 창(Instance)가 존재할 경우, Edge가 떠있는 상태인지, 아니면 Content를 밀어내는 상태인지 결정
};
type propsType = {
  windowKey: string; // 고유 키 지정. 한 페이지에 여러 ExtendedWindow가 사용되었을 경우를 고려함.
  minorKey?: string; // windowKey 다음으로 고유한 키 지정. DOM 클래스 명에만 영향을 미침.
  refreshKey?: string; // 레이아웃 저장/로드 갱신되는 키키
  dirPriority: 'horizontal' | 'vertical'; // 상하/좌우의 Edge의 배치 우선순위 (예: 'horizontal'일 경우, 모서리에서 상하의 Edge가 좌우의 Edge에 의해 밀려나게 됨.)
  edgeStyleLeft?: edgeStyle; // 왼쪽 Edge에 대한 스타일 지정
  edgeStyleRight?: edgeStyle; // 오른쪽 Edge에 대한 스타일 지정
  edgeStyleTop?: edgeStyle; // 위쪽 Edge에 대한 스타일 지정
  edgeStyleBottom?: edgeStyle; // 아래쪽 Edge에 대한 스타일 지정
  useSaveLayout?: boolean; // 레이아웃 상태를 로컬스토리지에 저장할지에 대한 여부
};
const props = withDefaults(defineProps<propsType>(), {
  minorKey: '',
});

const {
  dirPriority,
  windowKey,
  minorKey,
  edgeStyleLeft,
  edgeStyleRight,
  edgeStyleTop,
  edgeStyleBottom,
  useSaveLayout,
  refreshKey,
} = toRefs(props);
const outerWindowRef = ref();
const windowRef = ref();
const loadPosition = ref([]);

// Instance를 옮길 때, 커서가 ExtendedWindow의 가장자리까지 이동해야 Instance의 Position이 변경되도록, 그리고 Edge의 Float 기능이 추가되었기 때문에, 아래의 코드는 검증이 필요함
const emitDataHandler = (e: any, position: 'left' | 'right' | 'top' | 'bottom' | 'float') => {
  const target = document.querySelector(
    `.extended-window__receiver__${windowKey.value}${minorKey.value}[data-isDragging='true']`,
  );
  if (e.target.classList.contains('extended-window-edge')) {
    target?.setAttribute('data-targetPosition', 'float');
  } else {
    target?.setAttribute('data-targetPosition', position);
  }
};

const popLeftLoadPosition = () => {
  loadPosition.value.splice(0, 1);
};

const onUnload = () => {
  saveLayout();
  ummountInstanceInBody();
};

const ummountInstanceInBody = () => {
  const instances = document.body.querySelectorAll(
    `.extended-window__instance-from__${windowKey.value}${minorKey.value}`,
  );
  instances.forEach((el) => {
    el.remove();
  });
};

const saveLayout = () => {
  if (!useSaveLayout.value) return;

  const layout: any = [];

  const instances = [
    ...Array.from(document.body.children).filter((el) =>
      el.classList.contains(`extended-window__instance-from__${windowKey.value}${minorKey.value}`),
    ),
    ...outerWindowRef.value.querySelectorAll(`.extended-window__instance-from__${windowKey.value}${minorKey.value}`),
  ];
  const keys: string[] = [];

  instances.forEach((ins) => {
    if ((ins as HTMLElement).tagName === 'DIV') {
      const key = (ins as HTMLElement).getAttribute('data-instanceKey');
      const position = (ins as HTMLElement).getAttribute('data-currentPosition');
      const floatParent =
        ins.getAttribute('data-teleportToBodyWhenFloat') === 'true'
          ? document.body
          : document.querySelector(`.extended-window__${windowKey.value}${minorKey.value}`)!;

      if (key && !keys.includes(key)) {
        keys.push(key);
        layout.push({
          type: 'instance',
          key,
          position,
          order: null,
          x: position === 'float' ? ((ins as HTMLElement).offsetLeft / floatParent.clientWidth) * 100 : null,
          y: position === 'float' ? ((ins as HTMLElement).offsetTop / floatParent.clientHeight) * 100 : null,
          width: Number(ins.getAttribute('data-width')),
          height: Number(ins.getAttribute('data-height')),
        });
      }
    }
  });

  const edges = outerWindowRef.value.querySelectorAll(
    `.extended-window-edge-wrapper-from__${windowKey.value}${minorKey.value}`,
  );

  edges.forEach((edge: HTMLDivElement) => {
    const key = (edge as HTMLElement).getAttribute('data-position');
    const position = (edge as HTMLElement).getAttribute('data-position');

    if (key && !keys.includes(key)) {
      keys.push(key);
      layout.push({
        type: 'edge',
        key,
        position,
        order: null,
        x: null,
        y: null,
        width: key === 'left' || key === 'right' ? edge.clientWidth : null,
        height: key === 'top' || key === 'bottom' ? edge.clientHeight : null,
      });
    }
  });

  window.localStorage.setItem(`extended-window-${windowKey.value}`, JSON.stringify(layout));
};

const loadLayout = () => {
  const load = window.localStorage.getItem(`extended-window-${windowKey.value}`);
  if (load) {
    loadPosition.value = JSON.parse(load);
  }

  window.addEventListener('unload', () => {
    onUnload();
  });
};

const onResizeHandler = debounce(() => {
  const extendedWindow = document.querySelector(`.extended-window__${windowKey.value}${minorKey.value}`);
  if (extendedWindow) {
    Array.from(extendedWindow.childNodes).forEach((ins) => {
      if ((ins as HTMLElement).tagName === 'DIV') {
        const instance = ins as HTMLElement;
        const key = instance.getAttribute('data-instanceKey');
        if (key) {
          if (instance.offsetLeft < 0) {
            instance.style.left = '0%';
          } else if (instance.offsetLeft > outerWindowRef.value.clientWidth - instance.clientWidth) {
            instance.style.left = `calc(100% - ${instance.clientWidth}px)`;
          }

          if (instance.offsetTop < 0) {
            instance.style.top = '0%';
          } else if (instance.offsetTop > outerWindowRef.value.clientHeight - instance.clientHeight) {
            instance.style.top = `calc(100% - ${instance.clientHeight}px)`;
          }
        }
      }
    });
  }
}, 100);

const observer = new ResizeObserver(() => {
  onResizeHandler();
});

const onLoad = () => {
  setTimeout(() => {
    const instances = document.querySelectorAll('.extended-window__instance');
    instances.forEach((el) => {
      if (el.getAttribute('data-currentPosition') === 'float') {
        const now = dayjs();
        const today = dayjs().format('DD');
        const midnight = dayjs().startOf('day');
        const duration = now.diff(midnight, 'second'); // 시간 단위로 계산
        (el as HTMLElement).style.zIndex = String(today) + String(duration);
      }
    });
  });
};

// 크기변화를 관찰할 요소지정

onMounted(() => {
  observer.observe(outerWindowRef.value);
  onLoad();
});

// onMounted(() => {
//   loadLayout();
// });

onBeforeUnmount(() => {
  onUnload();
});

watch(
  [refreshKey],
  () => {
    loadLayout();
  },
  { immediate: true, flush: 'post' },
);

provide(`extended-window-provide`, { loadPosition, popLeftLoadPosition, saveLayout });

defineExpose({
  saveLayout,
});
</script>

<style lang="less" scoped>
@use 'ExtendedWindow.scss';

.extended-window {
  display: flex;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 100%;
  z-index: 10;
}

.extended-window.horizontal {
  flex-direction: column;
}

.extended-window-slot-wrapper {
  position: absolute;
  pointer-events: none;
  visibility: hidden;
}

.extended-windows-law {
  flex: 1;
  display: flex;
  //height: 100%;
  overflow: hidden;
}

.extended-windows-law.vertical {
  flex-direction: column;
}

.extended-window-container-wrapper {
  flex: 1;
  display: grid;

  //&[data-isFloat='true'] {
  //  position: absolute;
  //  left: 0;
  //  top: 0;
  //  width: 100%;
  //  height: 100%;
  //}
}

.extended-window-container-dummy {
  flex: 1;
}

.extended-window__container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.extended-window-indicator {
  position: absolute;
  z-index: 1000;
  &[data-position='left'] {
    left: 0;
    top: 0;
    width: 10px;
    height: 100%;
    background-color: rgba(50, 100, 255, 0.6);
  }
  &[data-position='right'] {
    right: 0;
    top: 0;
    width: 10px;
    height: 100%;
    background-color: rgba(50, 100, 255, 0.6);
  }
  &[data-position='top'] {
    left: 0;
    top: 0;
    width: 100%;
    height: 10px;
    background-color: rgba(50, 100, 255, 0.6);
  }
  &[data-position='bottom'] {
    left: 0;
    bottom: 0;
    width: 100%;
    height: 10px;
    background-color: rgba(50, 100, 255, 0.6);
  }
}
</style>
