<template>
  <div
    :class="[
      `extended-window__receiver`,
      `extended-window__receiver__${windowKey}${minorKey}`,
      `extended-window__receiver__${uuid}`,
    ]"
    :data-notAllowed="notAllowed"
    :data-fixedPosition="fixedPosition"
    ref="windowReceiverRef"
  />
  <!-- <Teleport :to="currentPosition === 'float' ? `.extended-window__container` : `.extended-window-edge__${currentPosition}`"> -->
  <div
    ref="instanceRef"
    @mousemove="emitDataHandler"
    @mouseleave="changeMouseOverPositionHandler('none')"
    :style="[
      currentPosition === 'float' ? styleWhenFloat : styleWhenFixed,
      currentWidth &&
        currentHeight &&
        currentPosition === 'float' && {
          width: typeof currentWidth === 'number' ? currentWidth + 'px' : currentWidth,
          height: typeof currentHeight === 'number' ? currentHeight + 'px' : currentHeight,
        },
      !modelValue && {
        visibility: 'hidden',
        overflow: 'hidden',
        flex: 'none',
      },
      !modelValue &&
        currentPosition !== 'float' && {
          width: '0 !important',
          height: '0 !important',
        },
      hidden && {
        visibility: 'hidden',
      },
    ]"
    :class="[
      'extended-window__instance',
      `extended-window__instance-from__${windowKey}${minorKey}`,
      `extended-window__instance-${currentPosition}`,
      `extended-window__instance-${currentPosition}${currentFloatHeaderPosition}`,
      isDragging ? `extended-window__instance-isDragging` : '',
      `extended-window__instance__${uuid}`,
      `extended-window__instance__${instanceKey}`,
      `extended-window__instance__hovering-${mouseOverPosition}`,
    ]"
    :data-currentPosition="currentPosition"
    :data-headerPositionWhenFixed="headerPositionWhenFixed"
    :data-teleportToBodyWhenFloat="teleportToBodyWhenFloat"
    :data-instanceKey="instanceKey"
    :data-isVisible="modelValue !== undefined ? modelValue : true"
    :data-width="currentWidth"
    :data-height="currentHeight"
    :data-instanceClass="`extended-window__instance-from__${windowKey}${minorKey}`"
  >
    <div
      @mousedown="startDrag"
      :class="[
        'extended-window__instance-header',
        `extended-window__instance-header-${computedHeaderPosition}${currentFloatHeaderPosition}`,
      ]"
      :data-closeButton="closeButtonWhenFloat"
      :style="[replaceHeaderWith && { height: 0, visibility: 'hidden' }]"
    >
      <div
        v-if="currentPosition === 'float' && closeButtonWhenFloat"
        :class="[
          'extended-window__instance-header-button-wrapper',
          `extended-window__instance-header-button-wrapper${currentFloatHeaderPosition}`,
        ]"
      >
        <IconClose
          style="margin-right: 1.5px"
          :width="10"
          :height="10"
          :color="'rgba(255, 255, 255, 0.8)'"
          @mousedown="(e: any) => e.stopPropagation()"
          @click="toggleInstanceHandler"
        />
      </div>
      <!--      <div v-else :class="[`extended-window__instance-header-indicator-${computedHeaderPosition}${currentFloatHeaderPosition}`]" />-->
    </div>
    <div
      @click="changeInstancePriorityHandler"
      :class="['extended-window__instance-body', `extended-window__instance-body-${currentPosition}`]"
    >
      <slot></slot>
    </div>
    <div class="extended-window__instance__resizer" v-if="resizeable" @mousedown="startResize" />
  </div>

  <Teleport :to="'body'" v-if="teleportToBodyWhenFloat" defer>
    <div
      ref="minSizeRef"
      class="extended-window__instance__size-calculator"
      :style="{ width: styleWhenFloat?.minWidth ?? '200px', height: styleWhenFloat?.minHeight ?? '200px' }"
    />
    <div
      ref="maxSizeRef"
      class="extended-window__instance__size-calculator"
      :style="{ width: styleWhenFloat?.maxWidth ?? '1024px', height: styleWhenFloat?.maxHeight ?? '720px' }"
    />
  </Teleport>
  <Teleport :to="windowRef" v-else-if="windowKey" defer>
    <div
      ref="minSizeRef"
      class="extended-window__instance__size-calculator"
      :style="{ width: styleWhenFloat?.minWidth ?? '200px', height: styleWhenFloat?.minHeight ?? '200px' }"
    />
    <div
      ref="maxSizeRef"
      class="extended-window__instance__size-calculator"
      :style="{ width: styleWhenFloat?.maxWidth ?? '1024px', height: styleWhenFloat?.maxHeight ?? '720px' }"
    />
  </Teleport>
</template>

<script setup lang="ts">
import { IconClose } from '@moz-shared/icons';
import { generateUUID } from '@moz-shared/utils';
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, toRefs, watch } from 'vue';
import { HEADER_LENGTH_THIN, HEADER_LENGTH_WIDE } from './ExtendedWindowConstants';

type propsType = {
  modelValue?: boolean; // 창(Instance)의 visibility와 바인딩됨
  initPosition: 'top' | 'bottom' | 'left' | 'right' | 'float'; // 초기 포지션
  headerPositionWhenFloat?: 'top' | 'left'; // 포지션이 float일 때, 기본 헤더의 위치 결정
  headerPositionWhenFixed?: 'left' | 'top'; // 포지션이 float이 아닐 때, 기본 헤더의 위치 결정
  notAllowed?: ('top' | 'bottom' | 'left' | 'right' | 'float')[]; // 창(Instance)가 위치할 수 없는 포지션을 결정함
  fixedPosition?: boolean; // 위치 고정
  closeButtonWhenFloat?: boolean; // 포지션이 float일 때, 기본 헤더의 닫기 버튼의 유무. modelValue props가 있을 때만 작동함
  replaceHeaderWith?: string; // 기본 헤더가 아닌, 개발자가 임의로 헤더를 지정하고자 할 때, 요소 선택자를 해당 prop으로 넘겨줄 수 있음
  instanceKey: string; // 고유 키값
  styleWhenFixed?: Record<string, any>; // 포지션이 float일 때, 창(Instance)의 스타일 결정. slot에 들어가는 콘텐츠와는 별개로 창(Instance) 그 자체의 스타일을 지정
  styleWhenFloat?: Record<string, any>; // 포지션이 float이 아닐 때, 창(Instance)의 스타일 결정. slot에 들어가는 콘텐츠와는 별개로 창(Instance) 그 자체의 스타일을 지정
  teleportToBodyWhenFloat?: boolean;
  resizeable?: boolean;
  hidden?: boolean;
};

const props = withDefaults(defineProps<propsType>(), {
  modelValue: true,
  headerPositionWhenFloat: 'top',
  fixedPosition: false,
  closeButtonWhenFloat: false,
});

const {
  initPosition,
  headerPositionWhenFloat,
  notAllowed,
  fixedPosition,
  closeButtonWhenFloat,
  modelValue,
  headerPositionWhenFixed,
  replaceHeaderWith,
  instanceKey,
  styleWhenFixed,
  styleWhenFloat,
  teleportToBodyWhenFloat,
  resizeable,
  hidden,
} = toRefs(props);

const emits = defineEmits(['update:modelValue']);
const currentPosition = ref<'top' | 'bottom' | 'left' | 'right' | 'float'>(initPosition.value);
const computedHeaderPosition = computed(() => {
  if (currentPosition.value === 'float') {
    return currentPosition.value;
  } else if (headerPositionWhenFixed.value) {
    return headerPositionWhenFixed.value === 'left' ? 'top' : 'left';
  }
  return currentPosition.value;
});
const currentFloatHeaderPosition = computed(() =>
  currentPosition.value === 'float' ? `-${headerPositionWhenFloat.value}` : '',
);
const isDragging = ref(false);
const instanceRef = ref();
const windowReceiverRef = ref();
const startCursorX = ref(0);
const startCursorY = ref(0);
const startInstanceX = ref(0);
const startInstanceY = ref(0);
const targetPosition = ref<'top' | 'bottom' | 'left' | 'right' | 'float'>('float');
const isValidToTeleport = ref(true);
const prevPosition = ref<'top' | 'bottom' | 'left' | 'right' | 'float'>(initPosition.value);
const windowKey = ref('');
const minorKey = ref('');
const windowRef = ref();
const windowIndicatorRef = ref();
const mouseOverPosition = ref<'before' | 'after' | 'none'>('none');
const uuid = ref(generateUUID());
const headerLengthWide = ref(`${HEADER_LENGTH_WIDE}px`);
const headerLengthThin = ref(`${HEADER_LENGTH_THIN}px`);
const currentHeaderLength = ref(closeButtonWhenFloat.value ? HEADER_LENGTH_WIDE : HEADER_LENGTH_THIN);
const computedHeaderLength = computed(() => {
  if (replaceHeaderWith.value) {
    return 0;
  } else if (currentPosition.value === 'float') {
    return `${currentHeaderLength.value}px`;
  }
  return headerLengthThin.value;
});
const altHeader = ref<any>();
const floatParent = computed(() => (teleportToBodyWhenFloat.value ? document.body : windowRef.value));

const { loadPosition, saveLayout } = inject('extended-window-provide') as any;

const instanceProps = ref({
  width: 0,
  height: 0,
});
const windowProps = ref({
  width: 0,
  height: 0,
  left: 0,
  top: 0,
});
const rangeProps = ref({
  minX: 0,
  minY: 0,
  maxX: 0,
  maxY: 0,
});

const edgeProps = ref<any>({
  leftEdge: {
    width: 0,
    height: 0,
    left: 0,
    top: 0,
  },
  rightEdge: {
    width: 0,
    height: 0,
    left: 0,
    top: 0,
  },
  topEdge: {
    width: 0,
    height: 0,
    left: 0,
    top: 0,
  },
  bottomEdge: {
    width: 0,
    height: 0,
    left: 0,
    top: 0,
  },
});

const teleportTo = async () => {
  // const floatParent = teleportToBodyWhenFloat.value
  //   ? 'body'
  //   : `.extended-window.extended-window__${windowKey.value}${minorKey.value}`;
  // const from = document.querySelector(
  //   prevPosition.value === 'float'
  //     ? floatParent
  //     : `.extended-window.extended-window__${windowKey.value}${minorKey.value} .extended-window-edge__${prevPosition.value}`,
  // );
  // const to = document.querySelector(
  //   currentPosition.value === 'float'
  //     ? floatParent
  //     : `.extended-window.extended-window__${windowKey.value}${minorKey.value} .extended-window-edge__${currentPosition.value}`,
  // );
  const from =
    prevPosition.value === 'float'
      ? floatParent.value
      : document.querySelector(
          `.extended-window.extended-window__${windowKey.value}${minorKey.value} .extended-window-edge__${prevPosition.value}`,
        );
  const to =
    currentPosition.value === 'float'
      ? floatParent.value
      : document.querySelector(
          `.extended-window.extended-window__${windowKey.value}${minorKey.value} .extended-window-edge__${currentPosition.value}`,
        );

  const isReversedDir =
    currentPosition.value === 'left' || currentPosition.value === 'right'
      ? to?.getAttribute('data-stackDir') === 'horizontal'
      : to?.getAttribute('data-stackDir') === 'vertical';

  const existBefore = windowReceiverRef.value.getAttribute('data-before');
  const existAfter = windowReceiverRef.value.getAttribute('data-after');
  const beforeReferenceItem =
    existBefore &&
    document.querySelector(
      `.extended-window.extended-window__${windowKey.value}${minorKey.value} .extended-window-edge__${currentPosition.value} > .${existBefore}`,
    );
  const afterReferenceItem =
    existAfter &&
    document.querySelector(
      `.extended-window.extended-window__${windowKey.value}${minorKey.value} .extended-window-edge__${currentPosition.value} > .${existAfter}`,
    );

  const fromElement = from as HTMLElement;
  if (!fromElement) return;
  const fromPosition = fromElement.getAttribute('data-position');
  const fromStackDir = fromElement.getAttribute('data-stackDir');
  const toElement = to as HTMLElement;
  const toPosition = toElement.getAttribute('data-position');
  const toStackDir = toElement.getAttribute('data-stackDir');

  if (prevPosition.value !== 'float' && instanceRef.value.clientWidth) {
    if (fromStackDir === 'horizontal' && (fromPosition === 'left' || fromPosition === 'right')) {
      fromElement.style.width = 'auto';
      // fromElement.style.width = fromElement.clientWidth - instanceRef.value.clientWidth + 'px';
    } else if (fromStackDir === 'vertical' && (fromPosition === 'top' || fromPosition === 'bottom')) {
      fromElement.style.height = 'auto';
      // fromElement.style.height = fromElement.clientHeight - instanceRef.value.clientHeight + 'px';
    }
  }

  if (currentPosition.value !== 'float' && instanceRef.value.clientWidth) {
    if (toStackDir === 'horizontal' && (toPosition === 'left' || toPosition === 'right')) {
      toElement.style.width = 'auto';
      // toElement.style.width = toElement.clientWidth + instanceRef.value.clientWidth + 'px';
    } else if (toStackDir === 'vertical' && (toPosition === 'top' || toPosition === 'bottom')) {
      toElement.style.height = 'auto';
      // toElement.style.height = toElement.clientHeight + instanceRef.value.clientHeight + 'px';
    }
  }

  if (prevPosition.value !== 'float' && prevPosition.value !== currentPosition.value) {
    if (fromElement.childNodes?.length === 0) {
      if (fromPosition === 'left' || fromPosition === 'right') {
        fromElement.style.width = 'auto';
      }
      if (fromPosition === 'top' || fromPosition === 'bottom') {
        fromElement.style.height = 'auto';
      }
    }
  }

  if (beforeReferenceItem) {
    await to?.insertBefore(instanceRef.value, beforeReferenceItem);
  } else if (afterReferenceItem) {
    await to?.insertBefore(instanceRef.value, afterReferenceItem.nextSibling);
  } else if (isReversedDir && to?.childNodes?.length && isValidToTeleport.value) {
    if (currentPosition.value === 'left' || currentPosition.value === 'top') {
      await to?.insertBefore(instanceRef.value, to.firstChild);
    } else {
      await to?.insertBefore(instanceRef.value, to.lastChild);
    }
  } else {
    if (isValidToTeleport.value) {
      await to?.appendChild(instanceRef.value);
    } else {
      currentPosition.value = prevPosition.value;
    }
  }

  changeInstancePriorityHandler();
  deleteEmitDataHandler();

  // nextTick(() => {
  //   saveLayout();
  // });
};

const isResizing = ref(false);
const startX = ref(0);
const startY = ref(0);
const startWidth = ref(0);
const startHeight = ref(0);
const minSizeRef = ref();
const maxSizeRef = ref();
const currentWidth = ref();
const currentHeight = ref();

const startResize = (e: any) => {
  if (!resizeable.value) return;
  e.preventDefault();
  isResizing.value = true;
  startX.value = e.clientX;
  startY.value = e.clientY;
  startWidth.value = instanceRef.value.clientWidth;
  startHeight.value = instanceRef.value.clientHeight;
  document.addEventListener('mousemove', resizing);
  document.addEventListener('mouseup', stopResize);
};

const resizing = (e: any) => {
  if (isResizing.value) {
    const newWidth = startWidth.value + (e.clientX - startX.value);
    const newHeight = startHeight.value + (e.clientY - startY.value);
    // const targetWidth = newWidth > minWidth.value ? newWidth : minWidth.value;

    const minWidth = minSizeRef.value.clientWidth;
    const maxWidth = maxSizeRef.value.clientWidth;
    const minHeight = minSizeRef.value.clientHeight;
    const maxHeight = maxSizeRef.value.clientHeight;

    let targetWidth = newWidth;
    let targetHeight = newHeight;

    if (newWidth > minWidth && newWidth < maxWidth) {
      targetWidth = newWidth;
    } else if (newWidth < minWidth) {
      targetWidth = minWidth;
    } else if (newWidth > maxWidth) {
      targetWidth = maxWidth;
    }

    if (newHeight > minHeight && newHeight < maxHeight) {
      targetHeight = newHeight;
    } else if (newHeight < minHeight) {
      targetHeight = minHeight;
    } else if (newHeight > maxHeight) {
      targetHeight = maxHeight;
    }

    currentWidth.value = targetWidth;
    currentHeight.value = targetHeight;

    // instanceRef.value.style.width = `${targetWidth}px !important`;
    // instanceRef.value.style.height = `${targetHeight}px !important`;
  }
};
const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', resizing);
  document.removeEventListener('mouseup', stopResize);
  nextTick(() => {
    saveLayout();
  });
};

const startDrag = async (e: any) => {
  e.preventDefault();
  // instanceRef.value.style.left = instanceRef.value.offsetLeft + 'px';
  // instanceRef.value.style.top = instanceRef.value.offsetTop + 'px';
  // instanceRef.value.style.right = 'auto';
  // instanceRef.value.style.bottom = 'auto';
  changeInstancePriorityHandler();
  initProps();
  isDragging.value = true;
  startCursorX.value = e.clientX;
  startCursorY.value = e.clientY;
  windowReceiverRef.value.setAttribute('data-isDragging', true);

  if (currentPosition.value !== 'float' && !fixedPosition.value) {
    prevPosition.value = currentPosition.value;
    currentPosition.value = 'float';
    await teleportTo();
    // const containerRect = document
    //   .querySelector(`.extended-window.extended-window__${windowKey.value}${minorKey.value}`)!
    //   .getBoundingClientRect();
    const containerRect = floatParent.value.getBoundingClientRect();

    let targetLeft = '0';
    let targetTop = '0';
    if (altHeader.value) {
      const instanceRect = instanceRef.value.getBoundingClientRect();
      const altHeaderRect = altHeader.value.getBoundingClientRect();
      targetLeft = `${e.clientX - (altHeaderRect.left - instanceRect.left + altHeader.value.clientWidth / 2) - containerRect.left}px`;
      targetTop = `${e.clientY - (altHeaderRect.top - instanceRect.top + altHeader.value.clientHeight / 2) - containerRect.top}px`;
    } else {
      switch (headerPositionWhenFloat.value) {
        case 'top':
          targetLeft = `${e.clientX - instanceRef.value.clientWidth / 2 - containerRect.left}px`;
          targetTop = `${e.clientY - currentHeaderLength.value / 2 - containerRect.top}px`;
          break;
        default:
        case 'left':
          targetLeft = `${e.clientX - currentHeaderLength.value / 2 - containerRect.left}px`;
          targetTop = `${e.clientY - instanceRef.value.clientHeight / 2 - containerRect.top}px`;
          break;
      }
    }

    instanceRef.value.style.left = targetLeft;
    instanceRef.value.style.top = targetTop;
    startInstanceX.value = instanceRef.value.offsetLeft;
    startInstanceY.value = instanceRef.value.offsetTop;
  } else {
    changeInstancePriorityHandler();
    startInstanceX.value = instanceRef.value.offsetLeft;
    startInstanceY.value = instanceRef.value.offsetTop;
  }

  document.addEventListener('mousemove', dragging);
  document.addEventListener('mouseup', stopDrag);
};

const dragging = (e: any) => {
  if (isDragging.value) {
    const newX = startInstanceX.value + (e.clientX - startCursorX.value);
    const newY = startInstanceY.value + (e.clientY - startCursorY.value);
    const targetX = teleportToBodyWhenFloat.value
      ? newX
      : Math.min(Math.max(newX, rangeProps.value.minX), rangeProps.value.maxX);
    const targetY = teleportToBodyWhenFloat.value
      ? newY
      : Math.min(Math.max(newY, rangeProps.value.minY), rangeProps.value.maxY);
    instanceRef.value.style.left = `${targetX}px`;
    instanceRef.value.style.top = `${targetY}px`;

    if (fixedPosition.value) return;

    const toPosition = windowReceiverRef.value.getAttribute('data-targetPosition');
    if (toPosition && toPosition !== 'float' && !notAllowed?.value?.includes(toPosition)) {
      windowIndicatorRef.value.setAttribute('data-position', 'none');
      targetPosition.value = toPosition;
      return;
    }

    if (e.clientX < edgeProps.value.leftEdge.left + edgeProps.value.leftEdge.width + 10) {
      if (notAllowed?.value?.includes('left')) return;
      if (e.clientX < windowProps.value.left + 10) {
        windowIndicatorRef.value.setAttribute('data-position', 'left');
        isValidToTeleport.value = true;
      } else {
        if (e.clientX > windowProps.value.left) {
          windowIndicatorRef.value.setAttribute('data-position', 'none');
          isValidToTeleport.value = false;
        }
      }
      targetPosition.value = 'left';
    } else if (e.clientX > edgeProps.value.rightEdge.left - 10) {
      if (notAllowed?.value?.includes('right')) return;
      if (e.clientX > windowProps.value.left + windowProps.value.width - 10) {
        windowIndicatorRef.value.setAttribute('data-position', 'right');
        isValidToTeleport.value = true;
      } else {
        if (e.clientX < windowProps.value.left + windowProps.value.width) {
          windowIndicatorRef.value.setAttribute('data-position', 'none');
          isValidToTeleport.value = false;
        }
      }
      targetPosition.value = 'right';
    } else if (e.clientY < edgeProps.value.topEdge.top + edgeProps.value.topEdge.height + 10) {
      if (notAllowed?.value?.includes('top')) return;
      if (e.clientY < windowProps.value.top + 10) {
        windowIndicatorRef.value.setAttribute('data-position', 'top');
        isValidToTeleport.value = true;
      } else {
        if (e.clientY > windowProps.value.top) {
          windowIndicatorRef.value.setAttribute('data-position', 'none');
          isValidToTeleport.value = false;
        }
      }
      targetPosition.value = 'top';
    } else if (e.clientY > edgeProps.value.bottomEdge.top - 10) {
      if (notAllowed?.value?.includes('bottom')) return;
      if (e.clientY > windowProps.value.top + windowProps.value.height - 10) {
        windowIndicatorRef.value.setAttribute('data-position', 'bottom');
        isValidToTeleport.value = true;
      } else {
        if (e.clientY < windowProps.value.height + windowProps.value.top) {
          windowIndicatorRef.value.setAttribute('data-position', 'none');
          isValidToTeleport.value = false;
        }
      }
      targetPosition.value = 'bottom';
    } else {
      windowIndicatorRef.value.setAttribute('data-position', 'none');
      deleteEmitDataHandler();
      targetPosition.value = 'float';
    }
  }
};

const stopDrag = () => {
  isDragging.value = false;

  if (targetPosition.value === 'float') {
    if (instanceRef.value.offsetLeft < 0) {
      instanceRef.value.style.left = '0%';
    } else if (instanceRef.value.offsetLeft > floatParent.value.clientWidth - instanceRef.value.clientWidth) {
      instanceRef.value.style.left = `calc(100% - ${instanceRef.value.clientWidth}px)`;
    } else {
      instanceRef.value.style.left = `${(instanceRef.value.offsetLeft / floatParent.value.clientWidth) * 100}%`;
    }

    if (instanceRef.value.offsetTop < 0) {
      instanceRef.value.style.top = '0%';
    } else if (instanceRef.value.offsetTop > floatParent.value.clientHeight - instanceRef.value.clientHeight) {
      instanceRef.value.style.top = `calc(100% - ${instanceRef.value.clientHeight}px)`;
    } else {
      instanceRef.value.style.top = `${(instanceRef.value.offsetTop / floatParent.value.clientHeight) * 100}%`;
    }
  }

  if (!fixedPosition.value && currentPosition.value !== targetPosition.value) {
    prevPosition.value = currentPosition.value;
    currentPosition.value = targetPosition.value;
    teleportTo();
  }

  windowIndicatorRef.value.setAttribute('data-position', 'none');
  windowReceiverRef.value.setAttribute('data-isDragging', false);
  document.removeEventListener('mousemove', dragging);
  document.removeEventListener('mouseup', stopDrag);
  nextTick(() => {
    saveLayout();
  });
};

const emitDataHandler = (e: any) => {
  if (currentPosition.value !== 'float') {
    const rect = instanceRef.value.getBoundingClientRect();
    const horizontalJudge = e.clientY > rect.top + instanceRef.value.clientHeight / 2;
    const verticalJudge = e.clientX > rect.left + instanceRef.value.clientWidth / 2;
    const stackDir = instanceRef.value.parentNode.getAttribute('data-stackDir');
    const position = stackDir === 'horizontal' ? verticalJudge : horizontalJudge;
    const target = document.querySelector(
      `.extended-window__receiver__${windowKey.value}${minorKey.value}[data-isDragging='true']`,
    );

    if (target?.getAttribute('data-notAllowed')?.includes(currentPosition.value)) return;
    if (target?.getAttribute('data-fixedPosition') && JSON.parse(target?.getAttribute('data-fixedPosition') || '')) {
      return;
    }

    target?.setAttribute(position ? 'data-after' : 'data-before', `extended-window__instance__${uuid.value}`);
    target?.setAttribute(!position ? 'data-after' : 'data-before', ``);

    if (target) {
      changeMouseOverPositionHandler(position ? 'after' : 'before');
    }
  }
};

const deleteEmitDataHandler = () => {
  const target = document.querySelector(
    `.extended-window__receiver__${windowKey.value}${minorKey.value}[data-isDragging='true']`,
  );
  target?.setAttribute('data-after', ``);
  target?.setAttribute('data-before', ``);
  target?.setAttribute('data-targetPosition', ``);
  isValidToTeleport.value = true;
  changeMouseOverPositionHandler('none');
};

const changeInstancePriorityHandler = () => {
  if (currentPosition.value !== 'float') return;
  const baseZIndex = 900; // 진짜 Popup(1000)보다는 zIndex가 작아야 하고, 다른 요소들에 비해서는 커야하므로 900 책정

  const instances = Array.from((floatParent.value as HTMLDivElement).children).filter((el) =>
    el.classList.contains(`extended-window__instance-${currentPosition.value}${currentFloatHeaderPosition.value}`),
  )!;

  instances.sort((a, b) => {
    const zA = parseInt(getComputedStyle(a).zIndex, 10);
    const zB = parseInt(getComputedStyle(b).zIndex, 10);

    const safeZA = isNaN(zA) ? -Infinity : zA;
    const safeZB = isNaN(zB) ? -Infinity : zB;

    return safeZA - safeZB;
  });

  instances.forEach((el, index) => {
    if (el === instanceRef.value) {
      (el as HTMLDivElement).style.zIndex = String(baseZIndex + instances.length);
    } else {
      (el as HTMLDivElement).style.zIndex = String(baseZIndex + index);
    }
  });
};

// const changeInstancePriorityHandler = () => {
//   if (currentPosition.value === 'float') {
//     const now = dayjs();
//     const today = dayjs().format('DD');
//     const midnight = dayjs().startOf('day');
//     const duration = now.diff(midnight, 'second'); // 시간 단위로 계산
//     instanceRef.value.style.zIndex = String(today) + String(duration);
//   } else {
//     instanceRef.value.style.zIndex = (styleWhenFixed.value as any)?.zIndex || 0;
//   }
// };

const changeMouseOverPositionHandler = (value: 'before' | 'after' | 'none') => {
  mouseOverPosition.value = value;
};

const toggleInstanceHandler = () => {
  emits('update:modelValue', !modelValue.value);
};

const initProps = () => {
  if (currentPosition.value === 'float' && windowRef.value && instanceRef.value) {
    instanceProps.value.width = instanceRef.value.clientWidth;
    instanceProps.value.height = instanceRef.value.clientHeight;
    windowProps.value.width = windowRef.value.clientWidth;
    windowProps.value.height = windowRef.value.clientHeight;
    const windowRect = windowRef.value.getBoundingClientRect();
    windowProps.value.left = windowRect.left;
    windowProps.value.top = windowRect.top;
    rangeProps.value.minX =
      headerPositionWhenFloat.value === 'left' ? 0 : -(instanceRef.value.clientWidth - currentHeaderLength.value);
    rangeProps.value.minY =
      headerPositionWhenFloat.value === 'top' ? 0 : -(instanceRef.value.clientHeight - currentHeaderLength.value);
    rangeProps.value.maxX = windowRef.value.clientWidth - currentHeaderLength.value;
    rangeProps.value.maxY = windowRef.value.clientHeight - currentHeaderLength.value;

    const edgeLeft = document.querySelector(
      `.extended-window-edge__left.extended-window__${windowKey.value}${minorKey.value}`,
    );
    const edgeRight = document.querySelector(
      `.extended-window-edge__right.extended-window__${windowKey.value}${minorKey.value}`,
    );
    const edgeTop = document.querySelector(
      `.extended-window-edge__top.extended-window__${windowKey.value}${minorKey.value}`,
    );
    const edgeBottom = document.querySelector(
      `.extended-window-edge__bottom.extended-window__${windowKey.value}${minorKey.value}`,
    );
    const edgeLeftRect = edgeLeft?.getBoundingClientRect();
    const edgeRightRect = edgeRight?.getBoundingClientRect();
    const edgeTopRect = edgeTop?.getBoundingClientRect();
    const edgeBottomRect = edgeBottom?.getBoundingClientRect();

    edgeProps.value.leftEdge.width = edgeLeft?.clientWidth;
    edgeProps.value.leftEdge.height = edgeLeft?.clientHeight;
    edgeProps.value.leftEdge.left = edgeLeftRect?.left;
    edgeProps.value.leftEdge.top = edgeLeftRect?.top;

    edgeProps.value.rightEdge.width = edgeRight?.clientWidth;
    edgeProps.value.rightEdge.height = edgeRight?.clientHeight;
    edgeProps.value.rightEdge.left = edgeRightRect?.left;
    edgeProps.value.rightEdge.top = edgeRightRect?.top;

    edgeProps.value.topEdge.width = edgeTop?.clientWidth;
    edgeProps.value.topEdge.height = edgeTop?.clientHeight;
    edgeProps.value.topEdge.left = edgeTopRect?.left;
    edgeProps.value.topEdge.top = edgeTopRect?.top;

    edgeProps.value.bottomEdge.width = edgeBottom?.clientWidth;
    edgeProps.value.bottomEdge.height = edgeBottom?.clientHeight;
    edgeProps.value.bottomEdge.left = edgeBottomRect?.left;
    edgeProps.value.bottomEdge.top = edgeBottomRect?.top;
  }
};

watch(
  [currentPosition, instanceRef, windowRef],
  () => {
    setTimeout(() => {
      initProps();
    });
  },
  { immediate: true, flush: 'post' },
);

onBeforeUnmount(() => {
  document.removeEventListener('mouseup', stopDrag);
  document.removeEventListener('mousemove', dragging);
});

onMounted(() => {
  windowKey.value = windowReceiverRef.value.parentNode.getAttribute('data-windowKey');
  minorKey.value = windowReceiverRef.value.parentNode.getAttribute('data-minorKey');
  windowRef.value = document.querySelector(`.extended-window.extended-window__${windowKey.value}${minorKey.value}`);
  windowIndicatorRef.value = document.querySelector(
    `.extended-window-indicator.extended-window__${windowKey.value}${minorKey.value}`,
  );
  teleportTo();
});

onMounted(() => {
  nextTick(() => {
    if (replaceHeaderWith.value) {
      altHeader.value = document.querySelector(`.extended-window__instance__${uuid.value} ${replaceHeaderWith.value}`);
      if (altHeader.value) {
        altHeader.value.style.cursor = 'move';
        altHeader.value.addEventListener('mousedown', startDrag);
      }
    }
  });
});

onBeforeUnmount(() => {
  altHeader?.value?.removeEventListener('mousedown', startDrag);
});

watch(
  [loadPosition, modelValue, instanceRef],
  async () => {
    if (!instanceRef.value) return;
    // alert(`${JSON.stringify(loadPosition.value)}`)
    const posInfoIndex = loadPosition.value.findIndex((p: any) => p.key === instanceKey.value);
    const posInfo = loadPosition.value[posInfoIndex];

    if (!posInfo) {
      return;
    }

    if (posInfo.applied) return;
    if (posInfoIndex > 0 && !loadPosition.value[posInfoIndex - 1].applied) {
      return;
    }

    currentPosition.value = posInfo.position;
    await teleportTo();
    if (posInfo.position === 'float') {
      const stanX =
        ((floatParent.value.clientWidth - instanceRef.value.clientWidth) / floatParent.value.clientWidth) * 100;
      const stanY =
        ((floatParent.value.clientHeight - instanceRef.value.clientHeight) / floatParent.value.clientHeight) * 100;
      const newX = stanX < posInfo.x ? stanX : posInfo.x;
      const newY = stanY < posInfo.y ? stanY : posInfo.y;
      instanceRef.value.style.left = `${newX}%`;
      instanceRef.value.style.top = `${newY}%`;
      currentWidth.value = posInfo.width ?? styleWhenFloat.value?.width;
      currentHeight.value = posInfo.height ?? styleWhenFloat.value?.height;
    }
    posInfo.applied = true;
    // applyLayoutWatch();
    // popLeftLoadPosition();
  },
  { deep: true, flush: 'post', immediate: true },
);

onMounted(() => {
  if (initPosition.value === 'float') {
    instanceRef.value.style.left = `${floatParent.value.clientWidth / 2 - instanceRef.value.clientWidth / 2}px`;
    instanceRef.value.style.top = `${floatParent.value.clientHeight / 2 - instanceRef.value.clientHeight / 2}px`;
  }
});

watch([modelValue], () => {
  if (!modelValue.value) {
    instanceRef.value.style.width = '0 !important';
    instanceRef.value.style.height = '0 !important';
  }
});
</script>

<style lang="less" scoped>
@use 'ExtendedWindow.scss';
.extended-window-edge[data-isFloat='true'] {
  .extended-window__instance-top,
  .extended-window__instance-bottom {
    // border-right: 1px solid #e8ebf0;
    //display: grid;
    height: fit-content;
    //grid-template-columns: v-bind(computedHeaderLength) auto;
  }

  .extended-window__instance-left,
  .extended-window__instance-right {
    // border-bottom: 1px solid #e8ebf0;
    width: fit-content;
    //flex-direction: column;
    //grid-template-rows: v-bind(computedHeaderLength) auto;
  }
}

.extended-window-edge[data-isFloat='false'] {
  & .extended-window__instance {
    background-color: #e8ebf0;
  }
  & .extended-window__instance-body {
    background-color: #c4cedc;
  }
}

.extended-window__instance {
  color: #233253;
  display: grid;
  overflow: visible;
  white-space: nowrap;
  pointer-events: auto;
}

.extended-window__instance-body {
  //background-color: #c4cedc;
}

.extended-window__instance-body-float {
  border-radius: 2.5px;
}

.extended-window__instance-float-top {
  //border-radius: 4px;
  //border: 1px solid #e8ebf0;
  position: absolute;
  grid-template-rows: v-bind(computedHeaderLength) auto;
  box-shadow: 0px 0px 5px 1px rgba(0, 0, 0, 0.1);
}

.extended-window__instance-float-left {
  //border-radius: 4px;
  //border: 1px solid #e8ebf0;
  position: absolute;
  grid-template-columns: auto auto;
  box-shadow: 0px 0px 5px 1px rgba(0, 0, 0, 0.1);
}

.extended-window__instance-top,
.extended-window__instance-bottom {
  width: fit-content;
}

.extended-window__instance-left,
.extended-window__instance-right {
  // border-bottom: 1px solid #e8ebf0;
  height: fit-content;
}

.extended-window__instance:not([data-headerPositionWhenFixed='top']).extended-window__instance-top,
.extended-window__instance:not([data-headerPositionWhenFixed='top']).extended-window__instance-bottom {
  grid-template-columns: v-bind(computedHeaderLength) auto;
}

.extended-window__instance:not([data-headerPositionWhenFixed='left']).extended-window__instance-left,
.extended-window__instance:not([data-headerPositionWhenFixed='left']).extended-window__instance-right {
  grid-template-rows: v-bind(computedHeaderLength) auto;
}

.extended-window__instance.extended-window__instance-top[data-headerPositionWhenFixed='left'],
.extended-window__instance.extended-window__instance-bottom[data-headerPositionWhenFixed='left'],
.extended-window__instance.extended-window__instance-left[data-headerPositionWhenFixed='left'],
.extended-window__instance.extended-window__instance-right[data-headerPositionWhenFixed='left'] {
  grid-template-columns: v-bind(computedHeaderLength) auto;
}

.extended-window__instance.extended-window__instance-top[data-headerPositionWhenFixed='top'],
.extended-window__instance.extended-window__instance-bottom[data-headerPositionWhenFixed='top'],
.extended-window__instance.extended-window__instance-left[data-headerPositionWhenFixed='top'],
.extended-window__instance.extended-window__instance-right[data-headerPositionWhenFixed='top'] {
  grid-template-rows: v-bind(computedHeaderLength) auto;
}

.extended-window__instance-header {
  background-color: #e8ebf0;
  // border-bottom: 1px solid rgba(60, 60, 60, 1);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: move;
}

.extended-window__instance-header-float-left {
  &[data-closeButton='true'] {
    width: v-bind(headerLengthWide);
  }
  &[data-closeButton='false'] {
    width: v-bind(headerLengthThin);
  }
  height: 100%;
}

.extended-window__instance-header-float-top {
  &[data-closeButton='true'] {
    height: v-bind(headerLengthWide);
  }
  &[data-closeButton='false'] {
    height: v-bind(headerLengthThin);
  }
  width: 100%;
}

.extended-window__instance-header-top,
.extended-window__instance-header-bottom {
  width: v-bind(headerLengthThin);
  height: 100%;
}

.extended-window__instance-header-left,
.extended-window__instance-header-right {
  width: 100%;
  height: v-bind(headerLengthThin);
}

.extended-window__instance-header-indicator-left,
.extended-window__instance-header-indicator-right,
.extended-window__instance-header-indicator-float-top {
  position: absolute;
  width: 16px;
  height: 2px;
  border-radius: 4px;
  background-color: #c4cedc;
}

.extended-window__instance-header-indicator-top,
.extended-window__instance-header-indicator-bottom,
.extended-window__instance-header-indicator-float-left {
  position: absolute;
  width: 2px;
  height: 16px;
  border-radius: 4px;
  background-color: #c4cedc;
}

.extended-window__instance-isDragging {
  pointer-events: none;
}

//.extended-window__instance-top.extended-window__instance__hovering-before,
//.extended-window__instance-bottom.extended-window__instance__hovering-before {
//  border-left: 6px solid rgba(50, 100, 255, 0.6);
//}
//
//.extended-window__instance-top.extended-window__instance__hovering-after,
//.extended-window__instance-bottom.extended-window__instance__hovering-after {
//  border-right: 6px solid rgba(50, 100, 255, 0.6);
//}
//
//.extended-window__instance-left.extended-window__instance__hovering-before,
//.extended-window__instance-right.extended-window__instance__hovering-before {
//  border-top: 6px solid rgba(50, 100, 255, 0.6);
//}
//
//.extended-window__instance-left.extended-window__instance__hovering-after,
//.extended-window__instance-right.extended-window__instance__hovering-after {
//  border-bottom: 6px solid rgba(50, 100, 255, 0.6);
//}

.extended-window-edge[data-stackDir='vertical'] {
  & .extended-window__instance__hovering-before {
    border-top: 6px solid rgba(50, 100, 255, 0.6);
  }
  & .extended-window__instance__hovering-after {
    border-bottom: 6px solid rgba(50, 100, 255, 0.6);
  }
}

.extended-window-edge[data-stackDir='horizontal'] {
  & .extended-window__instance__hovering-before {
    border-left: 6px solid rgba(50, 100, 255, 0.6);
  }
  & .extended-window__instance__hovering-after {
    border-right: 6px solid rgba(50, 100, 255, 0.6);
  }
}

.extended-window__instance-header-button-wrapper {
  width: 100%;
  height: 100%;
  display: flex;

  & svg {
    cursor: pointer;
  }
}

.extended-window__instance-header-button-wrapper-top {
  justify-content: flex-end;
  align-items: center;
}
.extended-window__instance-header-button-wrapper-left {
  justify-content: center;
  //align-items: center;
}

.extended-window__instance__size-calculator {
  position: absolute;
  pointer-events: none;
  left: 0;
  top: 0;
}

.extended-window__instance__resizer {
  width: 10px;
  height: 10px;
  // background-color: red;
  cursor: nwse-resize;
  position: absolute;
  bottom: 0;
  right: 0;
}

.extended-window__instance[data-isvisible='false'] {
  position: absolute;
}
</style>
