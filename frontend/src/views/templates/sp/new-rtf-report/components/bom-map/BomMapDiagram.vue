<template>
  <div
    class="bom-map-outer-wrapper"
    data-onboarding-id="bom-map"
    @wheel="
      (e) => {
        if (e.ctrlKey) {
          e.preventDefault();
        }
      }
    "
  >
    <ExtendedWindow
      style="width: 100%; height: 100%"
      :dirPriority="'horizontal'"
      :windowKey="'bom-map'"
      :edgeStyleLeft="{ resizable: false, stackDir: 'vertical' }"
      :edgeStyleRight="{
        resizable: true,
        stackDir: 'vertical',
        width: lang === 'en' ? '540px' : '350px',
        minWidth: '350px',
        maxWidth: '600px',
        float: !interfaceConfigs.window.demandInfo.isShown,
      }"
      :edgeStyleTop="{ resizable: false }"
      :edgeStyleBottom="{ resizable: false }"
      :useSaveLayout="true"
    >
      <!--      추가적인 Instance가 기획/개발되기 전까지 설정을 제외한 다른 Instance들을 모두 고정. (:fixed-position="true")-->
      <!--      헤더를 '.bom-map-window-title-wrapper'로 대체했었지만 Instance들을 고정하게 됨으로써 대체하지 않도록 함 (:replace-header-with="'.x'") -->
      <template #window>
        <ExtendedWindowInstance
          :instance-key="'overview'"
          :initPosition="'right'"
          v-model="interfaceConfigs.window.overview.isShown"
          :not-allowed="['top', 'bottom']"
          :style-when-fixed="{
            width: '100%',
            height: '100%',
            top: 0,
            bottom: 0,
            left: 0,
            overflow: 'hidden',
            minHeight: '200px',
          }"
          :replace-header-with="'.x'"
          :fixed-position="true"
        >
          <BomMapDiagramOverview data-onboarding-id="overview" :initOverview="initOverview" :get-diagram="getDiagram" />
        </ExtendedWindowInstance>
        <ExtendedWindowInstance
          :instance-key="'demandInfo'"
          :initPosition="'right'"
          v-model="interfaceConfigs.window.demandInfo.isShown"
          :not-allowed="['top', 'bottom']"
          :style-when-fixed="{ width: '100%', height: 'fit-content' }"
          :replace-header-with="'.x'"
          :fixed-position="true"
        >
          <BomMapDiagramDemandInfo
            data-onboarding-id="demand-info"
            :style="{ visibility: interfaceConfigs.window.demandInfo.isShown ? 'visible' : 'hidden' }"
            :demandInfos="demandInfos"
          />
        </ExtendedWindowInstance>
        <ExtendedWindowInstance
          :instance-key="'nodeInfo'"
          :initPosition="'right'"
          v-model="interfaceConfigs.window.demandInfo.isShown"
          :not-allowed="['top', 'bottom']"
          :style-when-fixed="{ width: '100%', height: 'auto' }"
          :replace-header-with="'.x'"
          :fixed-position="true"
        >
          <BomMapDiagramNodeInfo data-onboarding-id="node-info" />
        </ExtendedWindowInstance>
        <ExtendedWindowInstance
          :instance-key="'setting'"
          :initPosition="'float'"
          v-model="interfaceConfigs.window.config.isShown"
          :not-allowed="['top', 'bottom']"
          :style-when-fixed="{ width: '100%', height: 'auto' }"
          :replace-header-with="'.bom-map-window-title-wrapper'"
          :fixed-position="true"
        >
          <BomMapDiagramConfig />
        </ExtendedWindowInstance>
        <ExtendedWindowInstance
          v-model="isInitialized"
          :instance-key="'toolbar'"
          :initPosition="'left'"
          :header-position-when-float="'left'"
          :not-allowed="['bottom', 'right']"
          :style-when-fixed="{ height: 'auto', width: 'auto', flex: '1' }"
          :fixed-position="true"
          :replace-header-with="'.x'"
        >
          <BomMapDiagramToolBar
            data-onboarding-id="toolbar"
            v-if="getDiagram"
            :demand-infos="demandInfos"
            :getDiagram="getDiagram"
            :initKey="initKey"
          />
        </ExtendedWindowInstance>
        <ExtendedWindowInstance
          v-model="isInitialized"
          :instance-key="'topbar'"
          :initPosition="'top'"
          :header-position-when-float="'left'"
          :not-allowed="['bottom', 'right', 'left']"
          :style-when-fixed="{ height: 'auto', width: 'auto', flex: '1' }"
          :fixed-position="true"
          :replace-header-with="'.x'"
        >
          <BomMapDiagramLegends data-onboarding-id="legend" />
        </ExtendedWindowInstance>
      </template>
      <div class="bom-map-diagram-wrapper" @contextmenu.prevent>
        <div id="bom-map-canvas" class="bom-map-canvas" />

        <BomMapDiagramFloatingLabel
          v-if="getDiagram && userAction.hoverLabel.current.node"
          ref="labelFloatingRef"
          :get-diagram="getDiagram"
        />
        <BomMapDiagramFloatingAlertLabel
          v-if="getDiagram && userAction.hoverAlert.current.node"
          ref="alertLabelFloatingRef"
          :get-diagram="getDiagram"
        />
        <BomMapDiagramFloatingNodeInfo
          v-if="getDiagram && userAction.hover.current.node"
          ref="nodeFloatingRef"
          :get-diagram="getDiagram"
        />
        <BomMapDiagramFloatingAlertInfo
          v-if="getDiagram && userAction.click.current.node"
          ref="alertInfoFloatingRef"
          :get-diagram="getDiagram"
        />
      </div>
    </ExtendedWindow>
  </div>
  <ContextMenu ref="contextRef" />
</template>

<script setup lang="ts">
// import ContextMenu from '../ContextMenu/ContextMenu.vue';
import ExtendedWindow from '../extended-window/ExtendedWindow.vue';
import ExtendedWindowInstance from '../extended-window/ExtendedWindowInstance.vue';
import { apiCall } from '../../adapters/stores';
import { openLinkNewTab } from '../../adapters/utils';
import { ContextMenu } from '@vmscloud/moz-ui-components';
import { debounce } from 'es-toolkit';
import * as go from 'gojs';
import { Diagram } from 'gojs';
import { useTranslation } from 'i18next-vue';
import { computed, inject, onBeforeUnmount, onMounted, provide, ref, toRefs, watch } from 'vue';
import { initDiagram } from './BomMapDiagramCore';
import { BomMapDataSource, IBomMapIntefaceQuery, ShortLogDataSource } from './BomMapInterface';
import BomMapDiagramConfig from './interface/BomMapDiagramConfig.vue';
import BomMapDiagramDemandInfo from './interface/BomMapDiagramDemandInfo.vue';
import BomMapDiagramFloatingAlertInfo from './interface/BomMapDiagramFloatingAlertInfo.vue';
import BomMapDiagramFloatingAlertLabel from './interface/BomMapDiagramFloatingAlertLabel.vue';
import BomMapDiagramFloatingLabel from './interface/BomMapDiagramFloatingLabel.vue';
import BomMapDiagramFloatingNodeInfo from './interface/BomMapDiagramFloatingNodeInfo.vue';
import BomMapDiagramLegends from './interface/BomMapDiagramLegends.vue';
import BomMapDiagramNodeInfo from './interface/BomMapDiagramNodeInfo.vue';
import BomMapDiagramOverview from './interface/BomMapDiagramOverview.vue';
import BomMapDiagramToolBar from './interface/BomMapDiagramToolBar.vue';
import { useProjectInfo } from '../../adapters/stores';

/**
 * Variables, BomMap.vue에서 선언된 변수를 inject로 내려받고, 이를 toRefs()를 활용하여 구조분해
 */
type propsType = {
  bomNetworkInfos: BomMapDataSource;
  shortLogs: ShortLogDataSource;
  demandInfos: any;
  initKey: any;
};
const props = defineProps<propsType>();
const { demandInfos, initKey } = toRefs(props);
const { t } = useTranslation(); // 다국어
const {
  planCycleData,
  isShiftPressing,
  modelData,
  contextRef,
  userAction,
  isHighlighted,
  isDragMode,
  interfaceConfigs,
  currentScale,
  nodeFloatingRef,
  alertInfoFloatingRef,
  labelFloatingRef,
  alertLabelFloatingRef,
  diagramConfigs,
  isInitialized,
  demandNodeKey,
  setData,
} = inject('useBomMapInterface') as IBomMapIntefaceQuery;

let myDiagram: Diagram;
const getDiagram = ref();
const setConfigs = ref();
const initOverview = ref();

const projectInfoStore = useProjectInfo();
const user = computed(() => projectInfoStore.userInfo);
const lang = computed(() => user.value?.language || 'ko');

// // 임시 정렬 로직
// const temporaryAlignLogic = useBomMapDiagramAlignHandler(getDiagram);

/**
 * Buffer Node 컨텍스트 메뉴
 */
const bufferContextMenu = (selected: any) => [
  {
    text: t('text-context-show_full_path'),
    function() {
      selectFullPath(selected);
    },
  },
  {
    text: t('text-detail_info_on/off'),
    function() {
      setData(() => {
        interfaceConfigs.value.window.demandInfo.isShown = !interfaceConfigs.value.window.demandInfo.isShown;
      });
    },
  },
];

/**
 * Bom Node 컨텍스트 메뉴
 */
const bomContextMenu = (selected: any) => [
  {
    text: t('text-context-show_full_path'),
    function() {
      selectFullPath(selected);
    },
  },
  {
    text: t('text-detail_info_on/off'),
    function() {
      setData(() => {
        interfaceConfigs.value.window.demandInfo.isShown = !interfaceConfigs.value.window.demandInfo.isShown;
      });
    },
  },
  {
    text: t('text-context-open_res_alloc_info'),
    hidden: !planCycleData?.value,
    disabled: !selected.data.resYn,
    function() {
      openResAllocInfo(selected);
    },
  },
];

/**
 * 노드를 클릭했을 때, 인접 노드까지 모두 선택하게 하는 함수
 */
const selectNodesNearBy = (_e: any, node: any) => {
  const diagram = node.diagram!;
  diagram.startTransaction('highlight');
  if (!isShiftPressing.value) {
    diagram.clearSelection();
  }
  if (node instanceof go.Node) {
    node.isSelected = true;
  }
  if (node instanceof go.Node) {
    node.findLinksOutOf().each((l) => (l.isSelected = true));
    node.findNodesOutOf().each((n) => (n.isSelected = true));
    node.findLinksInto().each((l) => (l.isSelected = true));
    node.findNodesInto().each((n) => (n.isSelected = true));
  }
  diagram.commitTransaction('highlight');
};

/**
 * 화면 중앙을 기준으로 모든 Node가 보이게 Scale을 조정하는 함수
 */
function fitDiagramToScreen() {
  myDiagram.scale = 1;
  const diagramBounds = myDiagram.documentBounds;
  const viewportBounds = myDiagram.viewportBounds;
  const scale = Math.min(viewportBounds.width / diagramBounds.width, viewportBounds.height / diagramBounds.height, 1);
  myDiagram.scale = scale * 0.9;
  myDiagram.position = new go.Point(
    -(myDiagram.viewportBounds.width - myDiagram.documentBounds.width) / 2,
    -(myDiagram.viewportBounds.height - myDiagram.documentBounds.height) / 2 - 40 * scale,
  );
}

const fitDiagramToNode = () => {
  const viewportBounds = myDiagram.viewportBounds;
  const diagramBounds = myDiagram.documentBounds;
  myDiagram.scale = 0.6;
  let scale;
  if (viewportBounds.width > diagramBounds.width && viewportBounds.height > diagramBounds.height) {
    scale = 0.6;
  } else {
    const max = Math.max(viewportBounds.width / diagramBounds.width, viewportBounds.height / diagramBounds.height);
    const min = Math.min(viewportBounds.width / diagramBounds.width, viewportBounds.height / diagramBounds.height);
    scale = Math.min(0.6, Math.max(0.6, max - min));
  }

  myDiagram.scale = scale;

  // 기존 스케일은 일단 주석처리
  // myDiagram.scale = 0.6;
  const node = userAction.value.click.current.node;

  if (!node) return;

  // 화면 중앙에 노드를 위치하게 하는 코드, 그 밑 코드는 오른쪽에 노드를 위치하게 하는 코드
  // myDiagram.centerRect(node?.actualBounds);

  const nodeBounds = node.actualBounds;
  const nodePosition = node.location;

  // const viewportBounds = myDiagram.viewportBounds;
  const viewportWidth = viewportBounds.width;
  const viewportHeight = viewportBounds.height;

  const x = nodePosition.x - viewportWidth + nodeBounds.width + 105;
  const y = nodePosition.y - viewportHeight / 2 + nodeBounds.height / 2;

  myDiagram.position = new go.Point(x, y);
};

/**
 * ContextMenu 기능
 * 선택된 노드(들)를 기준으로 시작 노드와 끝 노드까지 타고들어가 선택하는 기능
 */
const selectFullPath = (nodeT: go.Node, dir: 'Backwards' | 'Forwards' | 'All' = 'All') => {
  const node = myDiagram.findNodeForKey(nodeT.data.key)!;
  if (dir === 'All' || dir === 'Backwards') {
    node.findLinksInto().each((l) => {
      l.isSelected = true;
    });
    node.findNodesInto().each((n) => {
      selectFullPath(n, 'Backwards');
      n.isSelected = true;
    });
  }
  if (dir === 'All' || dir === 'Forwards') {
    node.findLinksOutOf().each((l) => {
      l.isSelected = true;
    });
    node.findNodesOutOf().each((n) => {
      selectFullPath(n, 'Forwards');
      n.isSelected = true;
    });
  }
};

/**
 * ContextMenu 기능
 * 선택된 노드(들)를 기준으로 ResAllocInfo 페이지를 로드
 */
const openResAllocInfo = async (selected: any) => {
  const resItems = await apiCall({
    url: 'RarBomMapViewNew/GetBomResList',
    param: { planVer: planCycleData.value.planVer, bomID: selected.data.bomID },
    method: 'POST',
  });

  if (planCycleData?.value) {
    openLinkNewTab({
      path: `/wp/ResAllocInfo`,
      query: {
        planVer: planCycleData?.value.planVer,
        planCycle: planCycleData?.value.planCycleID,
        fromDate: planCycleData?.value.fromDate,
        toDate: planCycleData?.value.toDate,
        'res[+]': Array.from(new Set(resItems.data)).join(','),
      },
    });
  }
};

/**
 * Shift 키가 눌려있는지 판단하는 함수들, addEventListner에 부착
 */
const onShiftDownHandler = (e: any) => {
  if (e.key === 'Shift') {
    setData(() => {
      isShiftPressing.value = true;
    });
  }
};
const onShiftUpHandler = (e: any) => {
  if (e.key === 'Shift') {
    setData(() => {
      isShiftPressing.value = false;
    });
  }
};

/**
 * 다이어그램의 확대율을 가져오는 함수
 */
const getCurrentScale = () => {
  currentScale.value = myDiagram.scale;
};

/**
 * Float Window 열기
 */
const openFloatWindow = debounce(
  (type: string) => {
    if (type === 'alertLabel') {
      if (!alertLabelFloatingRef.value) return;
      alertLabelFloatingRef.value.context.open(() => [{ template: type, hover: false }]);
    } else if (type === 'alertInfo') {
      if (!alertInfoFloatingRef.value) return;
      alertInfoFloatingRef.value.context.open(() => [{ template: type, hover: false }]);
    } else if (type === 'bomNode' || type === 'bufferNode') {
      if (!nodeFloatingRef.value) return;
      nodeFloatingRef.value.context.open(() => [{ template: type, hover: false }]);
    } else if (type === 'label') {
      if (!labelFloatingRef.value) return;
      labelFloatingRef.value.context.open(() => [{ template: type, hover: false }]);
    }
  },
  300,
  { edges: ['leading'] },
);

/**
 * 유저 액션을 Transaction
 */
const transactionUserAction = (
  node: go.Node,
  action: 'click' | 'doubleClick' | 'hover' | 'clickAlert' | 'hoverLabel' | 'hoverAlert',
) => {
  setData(() => {
    userAction.value[action].prev.node = userAction.value[action].current.node;
  });
  setData(() => {
    userAction.value[action].current.node = node;
  });
};

/**
 * 초기화 후에 실행되는 함수
 */
const onInitialized = () => {
  setData(() => {
    isHighlighted.value = false;
  });
  setData(() => {
    isDragMode.value = false;
  });

  const node = myDiagram.findNodeForKey(demandNodeKey.value)!;
  node.isSelected = true;

  setData(() => {
    userAction.value.click = {
      current: {
        node,
      },
      prev: {
        node: null,
      },
    };
  });
  setData(() => {
    userAction.value.hover = {
      current: {
        node,
      },
      prev: {
        node: null,
      },
    };
  });
  setData(() => {
    userAction.value.clickAlert = {
      current: {
        node,
      },
      prev: {
        node: null,
      },
    };
  });
  setData(() => {
    userAction.value.hoverLabel = {
      current: {
        node,
      },
      prev: {
        node: null,
      },
    };
  });
  setData(() => {
    userAction.value.hoverAlert = {
      current: {
        node,
      },
      prev: {
        node: null,
      },
    };
  });

  myDiagram?.undoManager.clear();
};

const onAfterInitialized = () => {
  isInitialized.value = true;
  if (diagramConfigs.value.initialViewPoint === 'fitToScreen') {
    fitDiagramToScreen();
  } else {
    fitDiagramToNode();
  }
};

/**
 * 영역 선택 모드를 토글하는 로직
 */
watch([isDragMode], () => {
  if (isDragMode.value) {
    myDiagram.toolManager.dragSelectingTool.delay = 0;
  } else {
    myDiagram.toolManager.dragSelectingTool.delay = 100;
  }
});

/**
 * BomMap 데이터의 기준이 되는 데이터가 변하면, 새로 초기화되야 하는 옵션들 초기화하는 로직
 */
watch([initKey, modelData], () => {
  myDiagram.model = new go.GraphLinksModel(modelData.value.nodeDataArray, modelData.value.linkDataArray);
  onInitialized();
});

/**
 * BomMap 초기화
 */
onMounted(() => {
  initDiagram({
    diagramID: 'bom-map-canvas',
    overviewID: 'bom-map-overview',
    initConfigs: diagramConfigs.value,
  }).then((res) => {
    myDiagram = res.getDiagram();
    myDiagram.model = new go.GraphLinksModel(modelData.value.nodeDataArray, modelData.value.linkDataArray);
    getDiagram.value = res.getDiagram;
    initOverview.value = res.initOverview;
    setConfigs.value = res.setConfigs;
    setConfigs.value(diagramConfigs.value);

    onInitialized();
    onAfterInitialized();

    myDiagram.addDiagramListener('InitialLayoutCompleted', onAfterInitialized);
    myDiagram.addDiagramListener('ViewportBoundsChanged', getCurrentScale);

    res.setNodeEvents({
      bom: {
        contextClick: (_e: any, node: any) => {
          transactionUserAction(node, 'click');
          contextRef.value.open(bomContextMenu, node);
        },
        click: (_e: any, node: any) => {
          transactionUserAction(node, 'click');

          // setData(() => {
          //   interfaceConfigs.value.window.nodeInfo.isShown = true;
          // });

          selectNodesNearBy(_e, node);
        },
      },
      buffer: {
        contextClick: (_e: any, node: any) => {
          transactionUserAction(node, 'click');
          contextRef.value.open(bufferContextMenu, node);
        },
        click: (_e: any, node: any) => {
          transactionUserAction(node, 'click');

          // setData(() => {
          //   interfaceConfigs.value.window.nodeInfo.isShown = true;
          // });

          transactionUserAction(node, 'hover');
          openFloatWindow('bufferNode');
          selectNodesNearBy(_e, node);
        },
        doubleClick: (_: any, node: any) => {
          transactionUserAction(node, 'doubleClick');
        },
        mouseEnter: (_: any, node: any) => {
          transactionUserAction(node, 'hover');
          openFloatWindow('bufferNode');
        },
        mouseLeave: () => {},
      },
      alert: {
        click: (_e: any, node: any) => {
          transactionUserAction(node, 'clickAlert');
          selectNodesNearBy(_e, node);
          openFloatWindow('alertInfo');
        },
        mouseEnter: (_: any, node: any) => {
          transactionUserAction(node, 'hoverAlert');
          openFloatWindow('alertLabel');
        },
      },
      label: {
        mouseEnter: (_: any, node: any) => {
          transactionUserAction(node, 'hoverLabel');
          openFloatWindow('label');
        },
        mouseLeave: () => {},
      },
    });

    const getBomID = localStorage.getItem(
      `${planCycleData.value.projectID}-${planCycleData.value.planVer}-${planCycleData.value.demandID}-bomID`,
    );
    if (getBomID) {
      const targetNode = myDiagram.findNodeForKey(getBomID);
      if (targetNode) {
        myDiagram.select(targetNode); // 노드 선택
        myDiagram.scale = 0.6;
        myDiagram.centerRect(targetNode.actualBounds); // 노드를 다이어그램의 중앙으로 이동
        transactionUserAction(targetNode, 'click');
        localStorage.removeItem(
          `${planCycleData.value.projectID}-${planCycleData.value.planVer}-${planCycleData.value.demandID}-bomID`,
        );
      }
    }
  });
});

/**
 * 불러오거나 변경된 설정값을 다이어그램에 반영
 */
watch(
  [diagramConfigs],
  () => {
    setConfigs.value(diagramConfigs.value);
  },
  { deep: true },
);

/**
 * Shift 키가 눌려있는지 판단하는 함수를 EventListner에 부착하고 제거
 */
onMounted(() => {
  window.addEventListener('keydown', onShiftDownHandler);
  window.addEventListener('keyup', onShiftUpHandler);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onShiftDownHandler);
  window.removeEventListener('keyup', onShiftUpHandler);
  myDiagram.removeDiagramListener('ViewportBoundsChanged', getCurrentScale);
  myDiagram.removeDiagramListener('InitialLayoutCompleted', onAfterInitialized);
});

provide('useBomMapDiagram', {
  fitDiagramToScreen,
  transactionUserAction,
  openFloatWindow,
});
</script>

<style lang="scss" scoped>
:deep(.extended-window__bom-map) {
  & .extended-window__instance-header {
    & {
      position: relative;
      left: 0;
      top: 0;
    }
  }

  & .extended-window__instance-body {
    overflow: hidden;
    & > div {
      position: relative;
      left: 0;
      top: 0;
    }
  }

  & .extended-window__instance {
    outline: 1px solid #c1c1d8;
  }
}
.bom-map-canvas {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
}

// /* 아래의 모든 코드는 영역::코드로 사용 */
// .bom-map-canvas > div::-webkit-scrollbar {
//   width: 5px; /* 스크롤바의 너비 */
//   height: 5px;
// }

// .bom-map-canvas > div::-webkit-scrollbar-thumb {
//   height: 30%; /* 스크롤바의 길이 */
//   background: #d9d9d9; /* 스크롤바의 색상 */

//   border-radius: 10px;
// }

// .bom-map-canvas > div::-webkit-scrollbar-track {
//   background: rgba(0, 0, 0, 0); /*스크롤바 뒷 배경 색상*/
// }

.bom-map-outer-wrapper {
  &:before {
    width: calc(100% - 40px);
    height: calc(100% - 20px);
    border: 1px solid #c1c1d8;
    content: '';
    position: absolute;
    z-index: 11;
    pointer-events: none;
  }
  width: 100%;
  height: 100%;
  overflow: hidden !important;
}

.bom-map-diagram-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

:deep(.bom-map-window-inner-wrapper) {
  margin: 13px 13px 13px 13px;
}

:deep(.bom-map-window-inner-sub-wrapper) {
  padding: 0px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.bom-map-window-information-footer) {
  width: 100%;
  height: 30px;
  border-top: 1px solid #c1c1d8;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

:deep(.bom-map-text-button) {
  color: #4568e0;
  font-size: 12px;
  cursor: pointer;
  user-select: none;
}

:deep(.bom-map-window-separator) {
  width: 100%;
  height: 1px;
  border-top: 1px solid #c1c1d8;
  margin: 13px 0px 0px 0;
}

:deep(.bom-map-empty-status) {
  &:after {
    content: '-';
  }
}

:deep(.bom-map-window-title-wrapper) {
  width: 100%;
  height: 30px;
  border-bottom: 1px solid #c1c1d8;
  background-color: #eaebf3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #6a7184;
  font-weight: 500;
  padding: 10px;
}

:deep(.bom-map-window-title-right) {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 8px;
}

:deep(.bom-map-window-sub-title) {
  font-size: 13px;
  color: #565f6e;
  line-height: 100%;
  margin-bottom: 4px;
  font-weight: 500;
}

:deep(.bom-map-window-slider) {
  outline: 0;
  outline: 1px solid #bac6d4;
  border-radius: 500px;
  width: 50px;
  max-width: 100%;
  transition: box-shadow 0.2s ease-in-out;
  cursor: ew-resize;
}

:deep(.bom-map-window-slider[type='range']) {
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

:deep(.bom-map-window-slider[type='range']::-webkit-slider-runnable-track) {
  height: 8px;
  -webkit-appearance: none;
  color: #444;
  -webkit-transition: box-shadow 0.5s ease-in-out;
  transition: box-shadow 0.5s ease-in-out;
}

:deep(.bom-map-window-slider[type='range']::-webkit-slider-thumb) {
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

:deep(.bom-map-window-slider[type='range']:active::-webkit-slider-thumb) {
  background: #4568e0;
  box-shadow:
    -70px 0 0 65px #4568e0,
    inset 0 0 0 40px #ffffff;
}
//.bom-map-window-slider[type='range']::-moz-range-progress {
//  background-color: #43e5f7;
//}
//.bom-map-window-slider[type='range']::-moz-range-track {
//  background-color: #9a905d;
//}
//.bom-map-window-slider[type='range']::-ms-fill-lower {
//  background-color: #43e5f7;
//}
//.bom-map-window-slider[type='range']::-ms-fill-upper {
//  background-color: #9a905d;
//}

:deep(.extended-window__bom-map) {
  & .extended-window-edge {
    & .extended-window__instance-body > * {
      & .bom-map-window-slider {
        display: none;
      }
      opacity: 100% !important;
    }
  }
}

:deep(.bom-map-floating-context) {
  & .context-menu-content-wrapper {
    background-color: rgba(255, 255, 255, 0);
    border: none;
    box-shadow: 0px 5px 5px 0px rgba(0, 0, 0, 0.15);
  }
}

// edge에 창 고정시, 윗부분 선이 사라지는 현상 방지
:deep(.extended-window__instance:not([data-currentposition='float'])) {
  .bom-map-window-title-wrapper {
    border-top: 1px solid #c1c1d8;
  }
}
</style>
