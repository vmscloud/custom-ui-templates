<template>
  <div class="bom-map-diagram-toolbar" :data-isToolbarExpanded="interfaceConfigs.isToolbarExpanded">
    <template v-for="(value, key, idx) of toolbarData" :key="key">
      <div class="bom-map-diagram-toolbar-separator" v-if="[3].includes(idx)" />
      <button
        :data-expandIcon="idx > 5"
        :class="{
          'bom-map-diagram-toolbar-button-init': true,
          'bom-map-diagram-toolbar-button': value.enabled,
          'bom-map-diagram-toolbar-disabled': !value.enabled,
          'bom-map-diagram-toolbar-button-selected': value.selected,
        }"
        @click="
          () => {
            value.enabled && value.function();
          }
        "
        v-tooltip="{ text: value.tooltip, position: ['toRight, 4px', 'center'] }"
      >
        <component v-bind:is="toolbarIcon[key]" v-bind="value.props" :color="value.selected ? '#4568E0' : '#8998B5'" />
      </button>
    </template>

    <div
      :class="{
        'bom-map-diagram-toolbar-expand': true,
        'bom-map-diagram-toolbar-expand-true': interfaceConfigs.isToolbarExpanded,
      }"
      @click="toggleToolbarExpand"
    >
      <IconBomMapToolbarExpand />
    </div>
  </div>
</template>
<script setup lang="ts">
import { debounce } from 'es-toolkit';
import * as go from 'gojs';
import { Diagram } from 'gojs';
import { useTranslation } from 'i18next-vue';
import { computed, inject, onBeforeUnmount, onMounted, ref, toRefs, watch } from 'vue';
import IconBomMapToolbarExpand from '../assets/IconBomMapToolbarExpand.vue';
import IconBomMapToolbarInfo from '../assets/IconBomMapToolbarInfo.vue';
import IconBomMapToolbarOptimizeZoom from '../assets/IconBomMapToolbarOptimizeZoom.vue';
import IconBomMapToolbarOverview from '../assets/IconBomMapToolbarOverview.vue';
import IconBomMapToolbarRedo from '../assets/IconBomMapToolbarRedo.vue';
import IconBomMapToolbarScale from '../assets/IconBomMapToolbarScale.vue';
import IconBomMapToolbarSelect from '../assets/IconBomMapToolbarSelect.vue';
import IconBomMapToolbarSetting from '../assets/IconBomMapToolbarSetting.vue';
import IconBomMapToolbarTargetPath from '../assets/IconBomMapToolbarTargetPath.vue';
import IconBomMapToolbarUndo from '../assets/IconBomMapToolbarUndo.vue';
import IconBomMapToolbarZoomIn from '../assets/IconBomMapToolbarZoomIn.vue';
import IconBomMapToolbarZoomOut from '../assets/IconBomMapToolbarZoomOut.vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';

type propsType = {
  demandInfos: any;
  getDiagram: () => Diagram;
  initKey: any;
};

const props = defineProps<propsType>();
const { getDiagram, initKey } = toRefs(props);
const { t } = useTranslation(); // 다국어
const { isHighlighted, isDragMode, interfaceConfigs, setData } = inject('useBomMapInterface') as IBomMapIntefaceQuery;

const { fitDiagramToScreen } = inject('useBomMapDiagram') as any;
const scaleLog = ref({
  previousScale: 0,
  isOptimizedZoom: false,
});

let myDiagram: any;

onMounted(() => {
  myDiagram = getDiagram.value();
  myDiagram.addDiagramListener('Modified', checkSelectionMoved);
});

const toggleToolbarExpand = () => {
  const temp = {
    ...interfaceConfigs.value,
    isToolbarExpanded: !interfaceConfigs.value.isToolbarExpanded,
  };
  setData(() => {
    interfaceConfigs.value = temp;
  });
};

const toolbarIcon: { [prop: string]: any } = {
  demandInfo: IconBomMapToolbarInfo,
  // windowOpacity: IconBomMapToolbarInfoOpacity,
  zoomIn: IconBomMapToolbarZoomIn,
  zoomOut: IconBomMapToolbarZoomOut,
  fitToScreen: IconBomMapToolbarScale,
  optimizeZoom: IconBomMapToolbarOptimizeZoom,
  highlightTargetBom: IconBomMapToolbarTargetPath,
  redo: IconBomMapToolbarRedo,
  undo: IconBomMapToolbarUndo,
  overview: IconBomMapToolbarOverview,
  select: IconBomMapToolbarSelect,
  // 일시적 비활성화
  // align: IconBomMapToolbarAlign,
  config: IconBomMapToolbarSetting,
};

const toolbarData = ref<{
  [prop: string]: { props: any; function: Function; enabled: any; selected: any; tooltip: string };
}>({
  demandInfo: {
    props: {},
    function: () => {
      setData(() => {
        interfaceConfigs.value.window.demandInfo.isShown = !interfaceConfigs.value.window.demandInfo.isShown;
      });
    },
    enabled: true,
    selected: computed(() => interfaceConfigs.value.window.demandInfo.isShown),
    tooltip: t('text-detail_info_on/off'),
  },
  overview: {
    props: {},
    function: () => {
      setData(() => {
        interfaceConfigs.value.window.overview.isShown = !interfaceConfigs.value.window.overview.isShown;
      });
    },
    enabled: true,
    selected: computed(() => interfaceConfigs.value.window.overview.isShown),
    tooltip: t('text-bom_map-toolbar_toggle_overview'),
  },
  config: {
    props: {},
    function: () => {
      setData(() => {
        interfaceConfigs.value.window.config.isShown = !interfaceConfigs.value.window.config.isShown;
      });
    },
    enabled: true,
    selected: computed(() => interfaceConfigs.value.window.config.isShown),
    tooltip: t('text-setting'),
  },
  highlightTargetBom: {
    props: {},
    function: () => highlightTargetBom(),
    enabled: true,
    selected: isHighlighted,
    tooltip: t('text-bom_map-toolbar_target_bom'),
  },
  fitToScreen: {
    props: {},
    function: () => fitDiagramToScreen(),
    enabled: true,
    selected: false,
    tooltip: t('text-bom_map-toolbar_fit_to_screen'),
  },
  optimizeZoom: {
    props: {},
    function: () => optimizeZoom(),
    enabled: true,
    selected: computed(() => scaleLog.value.isOptimizedZoom),
    tooltip: t('text-bom_map-toolbar_fit_to_bom'),
  },
  zoomIn: {
    props: {},
    function: () => myDiagram.commandHandler.increaseZoom(),
    enabled: true,
    selected: false,
    tooltip: t('text-bom_map-toolbar_zoom_in'),
  },
  zoomOut: {
    props: {},
    function: () => myDiagram.commandHandler.decreaseZoom(),
    enabled: true,
    selected: false,
    tooltip: t('text-bom_map-toolbar_zoom_out'),
  },
  select: {
    props: {},
    function: () => (isDragMode.value = !isDragMode.value),
    enabled: true,
    selected: isDragMode,
    tooltip: t('text-bom_map-toolbar_select_tool'),
  },
  redo: {
    props: {},
    function: () => redoHandler(),
    enabled: false,
    selected: false,
    tooltip: t('text-bom_map-toolbar_redo'),
  },
  undo: {
    props: {},
    function: () => undoHandler(),
    enabled: false,
    selected: false,
    tooltip: t('text-bom_map-toolbar_undo'),
  },
  // 일시적 비활성화
  // align: {
  //   props: {
  //     align: alignOrientation
  //   },
  //   function: () => toggleAlignOrientation(),
  //   enabled: true,
  //   selected: false,
  //   tooltip: t('text-bom_map-toolbar_toggle_align')
  // }
});

/**
 * 정렬 방향을 토글하는 로직
 */
// const toggleAlignOrientation = () => {
//   if (alignOrientation.value === 'Horizontal') {
//     myDiagram.layout = $(CustomTreeLayout, {
//       portSpot: go.Spot.Center,
//       childPortSpot: go.Spot.Center,
//       angle: 90,
//       alignment: go.TreeLayout.AlignmentStart,
//       layerSpacingParentOverlap: 0.3,
//       // arrangement: go.TreeLayout.ArrangementVertical
//     });
//     alignOrientation.value = 'Vertical';
//   } else {
//     myDiagram.layout = $(CustomTreeLayout, {
//       portSpot: go.Spot.Center,
//       childPortSpot: go.Spot.Center,
//       angle: 0,
//       alignment: go.TreeLayout.AlignmentStart,
//       layerSpacingParentOverlap: 0.3,
//       // arrangement: go.TreeLayout.ArrangementVertical
//     });
//     alignOrientation.value = 'Horizontal';
//   }
// };

/**
 * Target Bom 하이라이팅 토글 함수
 */
const highlightTargetBom = () => {
  // myDiagram.clearSelection();
  myDiagram.skipsUndoManager = true;
  isHighlighted.value = !isHighlighted.value;
  myDiagram.links.each((link: go.Link) => {
    if (link.data.isForcePath) {
      if (link.toNode) {
        link.toNode.isHighlighted = isHighlighted.value;
      }
    } else if (link.data.isTargetPath) {
      link.isHighlighted = isHighlighted.value;
      if (link.toNode) {
        link.toNode.isHighlighted = isHighlighted.value;
      }
      if (link.fromNode) {
        link.fromNode.isHighlighted = isHighlighted.value;
      }
    }
  });
  myDiagram.skipsUndoManager = false;
};

/**
 * 정 비율로 스케일하는 기능
 */
const targetScale = 0.6;

const optimizeZoom = () => {
  if (scaleLog.value.isOptimizedZoom) {
    myDiagram.scale = scaleLog.value.previousScale;
    scaleLog.value.previousScale = 0;
    scaleLog.value.isOptimizedZoom = false;
    myDiagram.removeDiagramListener('ViewportBoundsChanged', onZoomHandler);
  } else {
    scaleLog.value.previousScale = myDiagram.scale;
    scaleLog.value.isOptimizedZoom = true;
    myDiagram.scale = targetScale;
    myDiagram.addDiagramListener('ViewportBoundsChanged', onZoomHandler);
  }
};

const onZoomHandler = debounce(() => {
  if (targetScale !== myDiagram.scale) {
    scaleLog.value.isOptimizedZoom = false;
    myDiagram.removeDiagramListener('ViewportBoundsChanged', onZoomHandler);
  }
}, 200);

/**
 * Redo/Undo 함수
 */
const redoHandler = () => {
  myDiagram.model.undoManager.redo();
  checkSelectionMoved();
};

const undoHandler = () => {
  myDiagram.model.undoManager.undo();
  checkSelectionMoved();
};

/**
 * Redo/Undo가 가능한지 체크하는 함수
 */
const checkSelectionMoved = () => {
  toolbarData.value.undo.enabled = myDiagram.model.undoManager.canUndo();
  toolbarData.value.redo.enabled = myDiagram.model.undoManager.canRedo();
};

/**
 * initKey가 바뀌면 Redo/Undo 버튼 비활성화
 */
watch([initKey], () => {
  toolbarData.value.undo.enabled = false;
  toolbarData.value.redo.enabled = false;
});

onBeforeUnmount(() => {
  myDiagram.removeDiagramListener('Modified', checkSelectionMoved);
  myDiagram.removeDiagramListener('ViewportBoundsChanged', onZoomHandler);
});
</script>

<style lang="scss">
.extended-window-edge__top {
  .bom-map-diagram-toolbar {
    height: 38px;
    padding: 0px 4px;
    margin-top: 1px;
  }

  .bom-map-diagram-toolbar-separator {
    width: 1px;
    height: 100%;
    background-color: #c1c1d8;
  }

  & > div:first-child .bom-map-diagram-toolbar-expand {
    display: none;
  }
}

.extended-window-edge__left {
  .bom-map-diagram-toolbar {
    height: 100%;
    width: 38px;
    flex-direction: column;
    margin-left: 1px;
    padding: 4px 0px;
  }

  .bom-map-diagram-toolbar-separator {
    width: 100%;
    height: 1px;
    background-color: #c1c1d8;
  }

  .bom-map-diagram-toolbar-expand {
    height: 12px;
    width: 100%;
    border: none;
    border-top: 1px solid #c1c1d8;
    & > svg {
      transform: rotate(0deg);
    }
  }

  .bom-map-diagram-toolbar-expand-true {
    & > svg {
      transform: rotate(180deg);
    }
  }
}

.extended-window-edge__top,
.extended-window-edge__bottom {
  & .bom-map-diagram-toolbar[data-isToolbarExpanded='false'] {
    .bom-map-diagram-toolbar-button-init[data-expandIcon='true'] {
      display: block;
    }
  }

  .bom-map-diagram-toolbar-expand {
    width: 12px;
    border: none;
    border-left: 1px solid #c1c1d8;
  }
}

.extended-window-edge__left {
  & > div:first-child .bom-map-diagram-toolbar[data-isToolbarExpanded='false'] {
    .bom-map-diagram-toolbar-button-init[data-expandIcon='true'] {
      display: block;
    }
  }

  & div:first-child .bom-map-diagram-toolbar {
    height: 100%;
  }

  & > div:first-child .bom-map-diagram-toolbar-expand {
    display: none;
  }
}

.extended-window-edge__right {
  & > div:last-child .bom-map-diagram-toolbar[data-isToolbarExpanded='false'] {
    .bom-map-diagram-toolbar-button-init[data-expandIcon='true'] {
      display: block;
    }
  }

  & div:last-child .bom-map-diagram-toolbar {
    height: 100%;
  }

  & div:not(:last-child) .bom-map-diagram-toolbar {
    height: auto;
  }

  & > div:last-child .bom-map-diagram-toolbar-expand {
    display: none;
  }
}

.bom-map-diagram-toolbar[data-isToolbarExpanded='false'] {
  .bom-map-diagram-toolbar-button-init[data-expandIcon='true'] {
    display: none;
  }
}

.bom-map-diagram-toolbar-expand {
  width: 12px;
  height: 36px;
  border-left: 1px solid #c1c1d8;
  display: flex;
  justify-content: center;
  align-items: center;

  background-color: #eaebf3;
  cursor: pointer;
  & > svg {
    transform: rotate(-90deg);
  }
}

.bom-map-diagram-toolbar-expand-true {
  & > svg {
    transform: rotate(90deg);
  }
}

.bom-map-diagram-toolbar {
  z-index: 3;
  background-color: #f8f8fd;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0px 4px;
}

.bom-map-diagram-toolbar-separator {
  width: 1px;
  height: 26px;
  background-color: #c1c1d8;
}

.bom-map-diagram-toolbar-button-init {
  background-color: rgba(0, 0, 0, 0);
  border: none;
  max-width: 26px;
  max-height: 26px;
  min-width: 26px;
  min-height: 26px;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 2px;
  cursor: default;
  opacity: 50%;
  padding: 0;
}

.bom-map-diagram-toolbar-button {
  cursor: pointer;
  opacity: 1;
}

.bom-map-diagram-toolbar-button:hover {
  background-color: rgba(137, 152, 181, 0.16);
}

.bom-map-diagram-toolbar-disabled {
  cursor: not-allowed;
}

.extended-window-edge__top {
  & > div:first-child .bom-map-diagram-toolbar {
    width: 100%;
  }
}

.extended-window-edge__bottom {
  & > div:last-child .bom-map-diagram-toolbar {
    width: 100%;
  }
}
</style>
