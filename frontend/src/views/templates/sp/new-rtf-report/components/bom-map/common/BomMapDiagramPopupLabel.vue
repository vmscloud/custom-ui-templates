<template>
  <div :style="[alignCenter && { alignItems: 'center' }]" class="bom-map-label-item">
    <span class="bom-map-label-item-key">{{ t(String(label)) }} </span>
    <div
      v-if="value"
      class="bom-map-label-item-value"
      :style="[{ lineHeight: 0, display: 'flex', justifyContent: 'space-between' }]"
    >
      <div
        v-if="!$slots.default"
        ref="wrapperRef"
        class="bom-map-label-item-value-wrapper"
        :style="{ lineHeight: '100%', flex: 1, display: 'grid', position: 'relative', textAlign: textAlign }"
      >
        <BomMapDiagramPopupLabelValue
          :value="value && Array.isArray(value[value?.length - 1]) ? value : value?.slice(0, value?.length - 1)"
          :tooltip="
            !disableTooltip &&
            (value && !Array.isArray(value[value?.length - 1])
              ? value[value?.length - 1]
              : { text: getFullValue(), onlyEllipsis: true })
          "
        />
      </div>
      <IconCopy
        v-if="!disableCopy"
        style="min-width: 12px; min-height: 12px; cursor: pointer; margin-left: 6px"
        @click="copyHandler"
      />
    </div>
    <slot v-else :props="value"></slot>
  </div>
</template>
<script setup lang="ts">
import { IconCopy } from '@moz-shared/icons';
import { copyToClipboard, showMessage } from '@moz-shared/utils';
import { useTranslation } from 'i18next-vue';
import { ref, toRefs } from 'vue';
import BomMapDiagramPopupLabelValue from './BomMapDiagramPopupLabelValue.vue';

type tokenType = Array<any>;

type propsType = {
  disableCopy?: boolean;
  disableTooltip?: boolean;
  // ' / '를 기준으로 split한 배열에서 copyIndex에 해당하는 문자열을 복사하게 함
  copyIndex?: number;
  label: string | number;
  value?: tokenType;
  textAlign?: 'left' | 'right';
  ratio?: string;
  alignCenter?: boolean;
};

const props = withDefaults(defineProps<propsType>(), {
  textAlign: 'left',
  ratio: '50% 50%',
});

const { disableCopy, disableTooltip, copyIndex, value, textAlign, ratio } = toRefs(props);
const { t } = useTranslation(); // 다국어
const wrapperRef = ref();
const getFullValue = () => {
  let acc = '';
  const recur = (token: any) => {
    if (!(token instanceof Array)) return;
    token.forEach((innerToken: any) => {
      if (!(typeof innerToken[0] === 'string' || typeof innerToken[0] === 'number')) {
        recur(innerToken);
      } else if (
        (typeof innerToken[0] === 'string' || typeof innerToken[0] === 'number') &&
        typeof innerToken !== 'string' &&
        typeof innerToken !== 'number'
      ) {
        acc += innerToken[0];
      }
    });
  };

  recur(value.value);
  return acc;
};

const copyHandler = () => {
  let text = '';
  if (typeof copyIndex.value === 'number') {
    const splitted = getFullValue().split(' / ');
    text = splitted[copyIndex.value];
  } else {
    text = getFullValue();
  }

  copyToClipboard(text).then(() => {
    showMessage(t('msg-toast-copy_success'), true);
  });
};
</script>
<style lang="scss" scoped>
.bom-map-label-item {
  height: fit-content;
  display: grid;
  grid-template-columns: v-bind(ratio);
}
.bom-map-label-item-key {
  font-size: 12px;
  font-weight: 500;
  color: #28364e;
  line-height: 120%;
}
.bom-map-label-item-value {
  font-size: 12px;
  color: #6a7184;
  max-width: 100%;
  //padding-left: 8px;

  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  word-break: break-all;
  line-height: 120%;
}

.bom-map-label-item-value-wrapper {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  word-break: break-all;
  padding-left: 10px;
}

.bom-map-label-item-value {
  & svg {
    display: none;
  }

  &:hover {
    & svg {
      display: block;
    }
  }
}
</style>
