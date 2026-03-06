<template>
  <BomMapDiagramFloating
    class="bom-map-floating-context"
    :style="{ transform: `scale(${currentScale * 1.35})` }"
    v-if="getDiagram"
    :getDiagram="getDiagram"
    :floatingPosition="'top'"
    :node="userAction.hoverLabel.current.node as go.Node"
    :initialized="initialized"
    :closeOnMove="true"
    :correction="
      (nodeWidth: number, nodeHeight: number) => {
        return {
          x:
            (nodeWidth - textWrapperRef?.clientWidth * currentScale * 1.35) / 2 -
            11 -
            (textWrapperRef?.clientWidth - textWrapperRef?.clientWidth * currentScale * 1.35) / 2,
          y:
            74 * currentScale * 1.35 -
            (textWrapperRef?.clientHeight - textWrapperRef?.clientHeight * currentScale * 1.35) / 1.5,
        };
      }
    "
    :adjustViewportOnEdge="false"
  >
    <!--    nodeWidth / 2 - (textWrapperRef?.clientWidth || 0) / 3 - 28-->
    <template #label="{ props }">
      <div
        class="bom-map-node-floating-label"
        @contextmenu="
          (e) => {
            e.stopImmediatePropagation();
          }
        "
      >
        <template v-if="userAction?.hoverLabel?.current?.node?.data.type === 'buffer'">
          <div>
            {{ bufferLabel1 }}
          </div>
          <div>
            {{ bufferLabel2 }}
          </div>
        </template>
        <template v-if="userAction?.hoverLabel?.current?.node?.data.type === 'bom'">
          <div>
            {{ bomLabel1 }}
          </div>
        </template>
      </div>
    </template>
  </BomMapDiagramFloating>
  <div ref="textWrapperRef" class="bom-map-node-floating-label bom-map-node-floating-label-dummy">
    <template v-if="userAction?.hoverLabel?.current?.node?.data.type === 'buffer'">
      <div>
        {{ bufferLabel1 }}
      </div>
      <div>
        {{ bufferLabel2 }}
      </div>
    </template>
    <template v-if="userAction?.hoverLabel?.current?.node?.data.type === 'bom'">
      <div>
        {{ bomLabel1 }}
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
import { Diagram } from 'gojs';
import { computed, inject, ref, toRefs } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import BomMapDiagramFloating from '../common/BomMapDiagramFloating.vue';

type propsType = {
  getDiagram: () => Diagram;
};

const props = defineProps<propsType>();
const { getDiagram } = toRefs(props);
const { userAction, currentScale, diagramConfigs } = inject('useBomMapInterface') as IBomMapIntefaceQuery;
const contextRef = ref();
const textWrapperRef = ref();
const initialized = (componentRef: any) => {
  contextRef.value = componentRef;
};

const bufferLabel1 = computed(() => {
  if (diagramConfigs.value.bufferNode.label1 === 'itemID') {
    return userAction.value?.hoverLabel?.current?.node?.data.itemID;
  }
  return userAction.value?.hoverLabel?.current?.node?.data.itemName;
});

const bufferLabel2 = computed(() => {
  if (diagramConfigs.value.bufferNode.label2 === 'siteID') {
    return userAction.value?.hoverLabel?.current?.node?.data.siteID;
  } else if (diagramConfigs.value.bufferNode.label2 === 'siteName') {
    return userAction.value?.hoverLabel?.current?.node?.data.siteName;
  }
  return '';
});

const bomLabel1 = computed(() => {
  if (diagramConfigs.value.bomNode.label1 === 'bomID') {
    return userAction.value?.hoverLabel?.current?.node?.data.bomID;
  }
  return '';
});

defineExpose({ context: contextRef });
</script>
<style lang="scss">
.bom-map-node-floating-label {
  width: fit-content;
  background-color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;

  max-width: 160px;

  overflow: hidden;

  & div {
    line-height: 100%;

    word-break: keep-all;
    word-wrap: break-word;
    // white-space: nowrap;
  }
}

.bom-map-node-floating-label-dummy {
  position: absolute;
  visibility: hidden;

  & div {
    line-height: 100%;
    white-space: nowrap;
  }
}
</style>
