<template>
  <BomMapDiagram
    :bomNetworkInfos="bomNetworkInfos"
    :shortLogs="shortLogs"
    :demandInfos="demandInfos"
    :initKey="initKey"
    v-if="modelData.nodeDataArray?.length"
  />
</template>

<script setup lang="ts">
import { provide, toRefs } from 'vue';
import BomMapDiagram from './BomMapDiagram.vue';
import { BomMapDataSource, BomMapPlanCycleData, ShortLogDataSource, useBomMapInterfaceQuery } from './BomMapInterface';

/**
 * Variables, Node와 Link의 색상과 선 굵기 등의 상수는 './Common/BomMapConstants.ts'에서 지정
 */
type propsType = {
  bomNetworkInfos: BomMapDataSource;
  shortLogs: ShortLogDataSource;
  demandInfos: any;
  initKey: any;
  planCycleData: BomMapPlanCycleData;
  userID: string;
};
const props = defineProps<propsType>();
const propsToRefs = toRefs(props);
const { bomNetworkInfos, shortLogs, initKey } = propsToRefs;

const useBomMapInterface = useBomMapInterfaceQuery({ ...propsToRefs });
const { modelData } = useBomMapInterface;

provide('useBomMapInterface', useBomMapInterface);
</script>
