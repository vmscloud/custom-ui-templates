<template>
  <BomMapDiagramFloating
    class="bom-map-floating-context"
    :style="{ transform: `scale(${currentScale * 1.35})` }"
    v-if="getDiagram"
    :getDiagram="getDiagram"
    :floatingPosition="'top'"
    :node="userAction.hoverAlert.current.node as go.Node"
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
            computedHeight * currentScale * 1.35 -
            (textWrapperRef?.clientHeight - textWrapperRef?.clientHeight * currentScale * 1.35) / 1.5,
        };
      }
    "
    :adjustViewportOnEdge="true"
  >
    <template #alertLabel="{ props }">
      <div
        class="bom-map-node-floating-alert-label"
        style="cursor: pointer"
        @contextmenu="
          (e) => {
            e.stopImmediatePropagation();
          }
        "
        @mousedown="
          (e) => {
            e.stopPropagation();
            onClickAlertHandler();
          }
        "
        v-if="userAction?.hoverAlert?.current?.node?.data?.alerts?.length > 0"
      >
        <div
          :style="{
            backgroundColor:
              ALERT_COLOR[userAction.hoverAlert?.current?.node?.data?.alerts[0]?.short_type?.toUpperCase()].FILL,
          }"
          class="bom-map-node-floating-alert-label-text-wrapper"
        >
          {{ label1 }}
        </div>
      </div>
    </template>
  </BomMapDiagramFloating>
  <div ref="textWrapperRef" class="bom-map-node-floating-alert-label bom-map-node-floating-alert-label-dummy">
    <div class="bom-map-node-floating-alert-label-text-wrapper">
      {{ label1 }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { convertToInternationalization } from '@moz-shared/utils';
import { Diagram } from 'gojs';
import { computed, inject, ref, toRefs } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import { ALERT_COLOR } from '../common/BomMapConstants';
import BomMapDiagramFloating from '../common/BomMapDiagramFloating.vue';

type propsType = {
  getDiagram: () => Diagram;
};

const props = defineProps<propsType>();
const { getDiagram } = toRefs(props);
const { userAction, currentScale, diagramConfigs, alertInfoFloatingRef } = inject(
  'useBomMapInterface',
) as IBomMapIntefaceQuery;
const { transactionUserAction } = inject('useBomMapDiagram') as any;
const contextRef = ref();
const textWrapperRef = ref();
const initialized = (componentRef: any) => {
  contextRef.value = componentRef;
};

const computedHeight = computed(() => {
  if (userAction.value?.hoverAlert?.current?.node?.data?.type === 'bom') {
    if (diagramConfigs.value.bomNode.label1 !== 'hide') {
      return 88;
    }
    if (diagramConfigs.value.bomNode.label1 === 'hide') {
      return 80;
    }
  }
  if (userAction.value?.hoverAlert?.current?.node?.data?.type === 'buffer') {
    if (diagramConfigs.value.bufferNode.label1 !== 'hide' && diagramConfigs.value.bufferNode.label2 !== 'hide') {
      return 98;
    }
    if (diagramConfigs.value.bufferNode.label1 === 'hide' && diagramConfigs.value.bufferNode.label2 === 'hide') {
      return 73;
    }
    if (diagramConfigs.value.bufferNode.label1 === 'hide' || diagramConfigs.value.bufferNode.label2 === 'hide') {
      return 88;
    }
  }
  return 0;
});

const label1 = computed(() => {
  if (userAction.value?.hoverAlert?.current?.node?.data?.alerts?.length > 0) {
    return convertToInternationalization(
      userAction.value?.hoverAlert?.current?.node?.data?.alerts[0]?.short_reason,
      'short',
    );
  }

  return null;
});

const onClickAlertHandler = () => {
  alertInfoFloatingRef.value.context?.close();

  setTimeout(() => {
    transactionUserAction(userAction.value?.hoverAlert?.current?.node, 'clickAlert');
    alertInfoFloatingRef.value.context.open(() => [{ template: 'alertInfo', hover: false }]);
  }, 300);
};

defineExpose({ context: contextRef });
</script>
<style lang="scss">
.bom-map-node-floating-alert-label {
  width: fit-content;
  background-color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;

  & div {
    line-height: 100%;
    white-space: nowrap;
  }
}

.bom-map-node-floating-alert-label-dummy {
  position: absolute;
  visibility: hidden;

  & div {
    line-height: 100%;
    white-space: nowrap;
  }
}

.bom-map-node-floating-alert-label-text-wrapper {
  padding: 1px 8px 0px 8px;
  line-height: 100%;
  color: white !important;
  height: 16px;
  border-radius: 16px;
  white-space: nowrap;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 500;
  min-width: 90px;
}
</style>
