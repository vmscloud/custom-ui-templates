<template>
  <ContextMenu
    ref="contextRef"
    :minWidth="'0px'"
    :noPadding="true"
    :fix-position="nodeCalcFloatingPosition"
    :to-bottom-center="floatingPosition === 'bottom'"
    :to-top-center="floatingPosition === 'top'"
    @open="
      (e: any) => {
        if (adjustViewportOnEdge && e.target) {
          adjustViewport(e.target.clientWidth, e.target.clientHeight, floatingPosition);
        }
        onOpenHandler();
      }
    "
    class="bom-map-floating"
    @wheel="onWheelHandler"
  >
    <template v-slot:[slotName]="{ props }" v-for="(_, slotName) in $slots" :key="slotName">
      <slot :name="slotName" :props="{ ...props }"></slot>
    </template>
  </ContextMenu>
</template>
<script setup lang="ts">
import { ContextMenu } from '@vmscloud/moz-ui-components';
import { ContextPosition } from '@moz-shared/types';
import { debounce, throttle } from 'es-toolkit';
import * as go from 'gojs';
import { Diagram } from 'gojs';
// import ContextMenu from '../../ContextMenu/ContextMenu.vue';
import { computed, onBeforeUnmount, onMounted, ref, toRefs, watch } from 'vue';

type propsType = {
  getDiagram: () => Diagram;
  floatingPosition: 'top' | 'bottom';
  correction?: (
    nodeWidth: number,
    nodeHeight: number,
  ) => {
    x: number;
    y: number;
  };
  node: go.Node;
  initialized: Function;
  closeOnMove?: boolean;
  adjustViewportOnEdge?: boolean;
};

const props = withDefaults(defineProps<propsType>(), {
  correction: () => ({
    x: 0,
    y: 0,
  }),
  adjustViewportOnEdge: true,
});

const { getDiagram, floatingPosition, initialized, node, closeOnMove, correction } = toRefs(props);
const myDiagram = getDiagram.value();
// const { data, setData } = inject('globalVariables') as any;
// const { currentScale } = data;
const contextRef = ref();
const willClose = ref(false);

const nodeViewPoint = ref({
  x: 0,
  y: 0,
});

const nodeCalcFloatingPosition = computed<ContextPosition>(() => {
  const { widthOnScreen, heightOnScreen } = getSelectedNodeSize();
  const calc = correction.value(widthOnScreen, heightOnScreen);
  return {
    left: `${nodeViewPoint.value.x + calc.x}px`,
    top: `${nodeViewPoint.value.y + calc.y}px`,
  };
});

/**
 * Floating Window를 켤 때 실행하는 함수
 */
const onOpenHandler = () => {
  if (node.value) {
    getPositionNode();
  }

  willClose.value = false;
};

/**
 * 노드의 실제 화면상 위치를 구하는 함수
 */
const getPositionNode = () => {
  const loc = myDiagram.transformDocToView(node.value?.location);
  if (loc) {
    nodeViewPoint.value = loc;
  }
};

/**
 * 노드의 실제 화면상 크기를 구하는 함수
 */
const getSelectedNodeSize = () => {
  if (!node.value) return { widthOnScreen: 0, heightOnScreen: 0 };
  const actualSize = node.value?.actualBounds;
  // 다이어그램의 현재 scale 값을 가져옴
  const scale = myDiagram.scale + 0.125;

  // 실제 화면에서 보여지는 크기를 계산
  const widthOnScreen = actualSize?.width * scale;
  const heightOnScreen = actualSize?.height * scale;

  return { widthOnScreen, heightOnScreen };
};

/**
 * Floating Window 위에 커서가 위치해 있어도, Diagram의 스크롤이나 확대/축소 조작을 하게끔 하는 코드
 */
const onWheelHandler = (e: any) => {
  e.preventDefault();

  const step = 100;
  let scrollPosX = myDiagram.position.x;
  let scrollPosY = myDiagram.position.y;

  if (e.ctrlKey) {
    if (e.deltaY < 0) {
      myDiagram.commandHandler.increaseZoom();
    } else {
      myDiagram.commandHandler.decreaseZoom();
    }
  } else if (e.shiftKey) {
    if (e.deltaY < 0) {
      scrollPosX -= step;
    } else {
      scrollPosX += step;
    }
  } else {
    if (e.deltaY < 0) {
      scrollPosY -= step;
    } else {
      scrollPosY += step;
    }
  }

  myDiagram.position = new go.Point(scrollPosX, scrollPosY);
};

/**
 * Floating Window가 켜질 때, 구석에서 가려지면 자동으로 Diagram의 Viewport를 수정하여 가려지지 않도록 하는 함수
 */
function adjustViewport(marginLeft: number, marginTop: number, position: 'top' | 'bottom') {
  if (!node.value) return;

  // 화면의 크기를 가져옵니다.
  const screenWidth = myDiagram?.div?.clientWidth || 0;
  const screenHeight = myDiagram?.div?.clientHeight || 0;

  // 노드의 위치가 화면 구석에 있는지 판단합니다.
  const inCorner =
    nodeViewPoint.value.x < marginLeft ||
    nodeViewPoint.value.y < marginTop ||
    nodeViewPoint.value.x > screenWidth - marginLeft ||
    nodeViewPoint.value.y > screenHeight - marginTop;

  if (inCorner) {
    // 뷰포인트 조정을 위한 새 위치 계산
    const canvasWidth = myDiagram.viewportBounds.width;
    const canvasHeight = myDiagram.viewportBounds.height;
    // 노드의 너비와 높이를 구함
    const nodeWidth = node.value.actualBounds.width;
    const nodeHeight = node.value.actualBounds.height;

    const scale = myDiagram.scale;
    // 노드의 위치를 캔버스의 오른쪽 아래 구석에 맞추기 위해 필요한 diagram.position을 계산함
    const top = node.value.position.y - marginTop / scale;
    const left = node.value.position.x + nodeWidth / 2 - marginLeft / 2 / scale;
    const right = node.value.position.x - (canvasWidth - nodeWidth / 2) + marginLeft / 2 / scale;
    const bottom = node.value.position.y - (canvasHeight - nodeHeight) + marginTop / scale;

    let newX = myDiagram.position.x;
    let newY = myDiagram.position.y;

    if (myDiagram.position.x > left) newX = left;
    else if (myDiagram.position.x < right) newX = right;

    if (myDiagram.position.y > top) newY = position === 'top' ? top : newY;
    else if (myDiagram.position.y < bottom) newY = position === 'bottom' ? bottom : newY;
    myDiagram.position = new go.Point(newX, newY - 1);
  }
}

/**
 * 해당 컴포넌트를 사용하는 부모 컴포넌트에게 contextRef 객체를 전달하는 코드
 */
watch([contextRef], () => {
  if (contextRef.value) {
    initialized.value(contextRef.value);
  }
});

/**
 * closeOnMove가 true일 때, ViewPort가 변경되거나 커서가 노드를 벗어났을 때 Floating Window를 조작(Off)하는 함수
 */
const closeWhenViewportBoundsChangedHandler = debounce(() => {
  willClose.value = true;
  closeHandler();
}, 100);

const closeHandler = debounce(() => {
  const myDiagramObj = getDiagram.value();
  // 마우스 커서의 위치 가져오기
  const mousePoint = myDiagramObj.lastInput.documentPoint;

  // 해당 좌표에 노드가 있는지 확인
  const part = myDiagramObj.findPartAt(new go.Point(mousePoint.x, mousePoint.y));

  if (!part || part.data.key !== node.value.data.key) {
    contextRef.value?.close();
  }
  willClose.value = false;
}, 2000);

const closeWhenMouseMoveHandler = throttle(
  () => {
    if (willClose.value) return;
    const myDiagramObj = getDiagram.value();
    // 마우스 커서의 위치 가져오기
    const mousePoint = myDiagramObj.lastInput.documentPoint;

    // 해당 좌표에 노드가 있는지 확인
    const part = myDiagramObj.findPartAt(new go.Point(mousePoint.x, mousePoint.y));
    if (!part || part.data.key !== node.value.data.key) {
      contextRef.value?.close();
    }
    willClose.value = false;
  },
  200,
  { edges: ['leading'] },
);

onMounted(() => {
  if (closeOnMove.value) {
    myDiagram.addDiagramListener('ViewportBoundsChanged', closeWhenViewportBoundsChangedHandler);
    window.addEventListener('mousemove', closeWhenMouseMoveHandler);
  }
});

/**
 * ViewPort가 변경되었을 때, Floating Window가 노드를 따라가게 함
 */
onMounted(() => {
  myDiagram.addDiagramListener('ViewportBoundsChanged', getPositionNode);
});

onBeforeUnmount(() => {
  myDiagram.removeDiagramListener('ViewportBoundsChanged', getPositionNode);
  window.removeEventListener('mousemove', closeWhenMouseMoveHandler);
});
</script>
<style lang="scss"></style>
