<template>
  <template v-for="(innerValue, idx) in value">
    <span
      v-if="typeof innerValue[0] === 'string' || typeof innerValue[0] === 'number'"
      class="bom-map-label-item-value"
      :style="innerValue[1]"
      v-tooltip="tooltip"
    >
      {{ innerValue[0] }}
    </span>
    <span v-else-if="innerValue[0] instanceof Array" :style="[innerValue[innerValue.length - 1]]">
      <BomMapDiagramPopupLabelValue
        :value="
          (typeof innerValue[innerValue.length - 1] === 'string'
            ? innerValue.slice(0, innerValue.length - 1)
            : innerValue) as tokenType
        "
      />
    </span>
  </template>
</template>
<script setup lang="ts">
import { toRefs } from 'vue';

type tokenType = Array<string[] | tokenType>;
type propsType = {
  value?: tokenType;
  tooltip?: any;
};

const props = withDefaults(defineProps<propsType>(), {});
const { value } = toRefs(props);
</script>
<script lang="scss"></script>
