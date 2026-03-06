<template>
  <BomMapDiagramFloating
    v-if="getDiagram"
    :getDiagram="getDiagram"
    :floatingPosition="'top'"
    :node="userAction.hover.current.node as go.Node"
    :initialized="initialized"
    :closeOnMove="true"
    :correction="
      (nodeWidth: number, nodeHeight: number) => {
        return {
          x: nodeWidth / 2 - 11.5,
          y: -5,
        };
      }
    "
  >
    <template #bufferNode="{ props }">
      <div class="bom-map-floating-buffer">
        <div class="bom-map-floating-buffer-item-outer-wrapper">
          <div class="bom-map-floating-buffer-item-inner-wrapper">
            <BomMapDiagramPopupLabel
              v-if="getNodeData.targetDatetime"
              v-for="(value, key) in bufferInfoSchema1"
              :label="key"
              :value="value"
              :ratio="'auto auto'"
              :textAlign="'right'"
              :disable-copy="true"
              :disable-tooltip="true"
            />
            <div
              v-else
              style="
                width: 100%;
                text-align: center;
                font-size: 12px;
                font-weight: 400;
                color: #565f6e;
                word-break: keep-all;
              "
            >
              {{ t('desc-bom_map-no_target') }}
            </div>
          </div>
          <div style="width: 100%; height: 1px; background-color: #c1c1d8" />
          <div class="bom-map-floating-buffer-item-inner-wrapper" data-background="true">
            <BomMapDiagramPopupLabel
              v-for="(value, key) in bufferInfoSchema2"
              :label="key"
              :value="value"
              :ratio="'45% 55%'"
              :textAlign="'right'"
              :disable-copy="true"
              :disable-tooltip="true"
            />
          </div>
        </div>
      </div>
    </template>
  </BomMapDiagramFloating>
</template>
<script setup lang="ts">
import { useProjectInfoStore } from '../../../adapters/stores';
import { formatCompactNumber, dayjs } from '@moz-shared/utils';
import { Diagram } from 'gojs';
import { useTranslation } from 'i18next-vue';
import { computed, inject, ref, toRefs } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import BomMapDiagramFloating from '../common/BomMapDiagramFloating.vue';
import BomMapDiagramPopupLabel from '../common/BomMapDiagramPopupLabel.vue';

type propsType = {
  getDiagram: () => Diagram;
};

const props = defineProps<propsType>();
const { getDiagram } = toRefs(props);
const { t } = useTranslation(); // 다국어
const { userAction } = inject('useBomMapInterface') as IBomMapIntefaceQuery;
const contextRef = ref();

const projectModule = useProjectInfoStore();

const getNodeData = computed(() => {
  if (userAction.value.hover.current.node) {
    return userAction.value.hover.current.node?.data;
  }
  return [];
});

//----------------------------------------------------------------------------------------------------------------------
/**
 * BufferInfo
 */
const calcDate = computed(() => {
  const diff = dayjs(getNodeData.value.planDatetime).diff(dayjs(getNodeData.value.targetDatetime), 'seconds');

  const day = Math.floor(Math.abs(diff) / (60 * 60 * 24));
  const datetime = dayjs.duration(Math.floor(Math.abs(diff) % (60 * 60 * 24)), 'seconds').format(' [Day] HH:mm');

  return diff < 0 ? day * -1 + datetime : day + datetime;
});
const bufferInfoSchema1 = computed(() => ({
  [t('text-bom_map-target_datetime')]: [
    [projectModule.convertToFormat('dateTime', getNodeData.value.targetDatetime), 'margin-right: 4px'],
  ],
  [t('text-bom_map-plan_datetime')]: [
    [
      getNodeData.value.planDatetime ? projectModule.convertToFormat('dateTime', getNodeData.value.planDatetime) : '-',
      'margin-right: 4px',
    ],
    ['', 'display: block;'],
    getNodeData.value.planDatetime && [
      ['('],
      [calcDate.value, `color: ${calcDate.value[0] === '-' ? '#339A88' : '#FA9E23'} `],
      [')'],
    ],
  ],
  [t('text-bom_map-wip_usage_qty')]: [
    [
      getNodeData.value.pegQty
        ? formatCompactNumber(getNodeData.value.pegQty, {
            returnWhenInvalid: '-',
            convertUnit: { standard: 1_000_000 },
          })
        : '-',
      'margin-right: 4px',
    ],
  ],
}));

const bufferInfoSchema2 = computed(() => ({
  [t('text-max_cum_tat')]: [[getNodeData.value.maxCumTat, 'margin-right: 4px']],
  [t('text-min_cum_tat')]: [[getNodeData.value.minCumTat, 'margin-right: 4px']],
}));

const initialized = (componentRef: any) => {
  contextRef.value = componentRef;
};

defineExpose({ context: contextRef });
</script>
<style lang="scss">
.bom-map-floating-buffer {
  width: 220px;
}

.bom-map-floating-buffer-item-outer-wrapper {
  overflow: hidden;
  border-radius: 4px;
}

.bom-map-floating-buffer-item-inner-wrapper {
  padding: 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;

  &[data-background='true'] {
    background-color: #f8f8fd;
  }
}
</style>
