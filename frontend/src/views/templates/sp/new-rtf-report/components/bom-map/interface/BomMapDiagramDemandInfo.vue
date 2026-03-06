<template>
  <div
    v-if="demandInfos"
    :class="[`bom-map-demand-information-outer-wrapper`]"
    :style="{ opacity: `${interfaceConfigs.window.demandInfo.opacity}%` }"
  >
    <div class="bom-map-window-title-wrapper">
      {{ t('text-upper-demand_information') }}
      <div class="bom-map-window-title-right">
        <input
          @mousedown="(e) => e.stopPropagation()"
          type="range"
          min="30"
          max="100"
          value="50"
          class="bom-map-window-slider"
          v-model="interfaceConfigs.window.demandInfo.opacity"
        />
        <div
          @click="onClickExpandHandler"
          :class="{
            'bom-map-text-button': true,
          }"
          style="margin-right: 4px"
        >
          {{ isExpanded ? t('text-fold') : t('text-more') }}
        </div>
        <IconClose style="cursor: pointer" @mousedown="closeHandler" />
      </div>
    </div>
    <div class="bom-map-window-inner-wrapper" data-responsive="true" style="margin-bottom: 0">
      <BomMapDiagramPopupLabel
        v-for="(value, key, idx) in demandInfoSchema1"
        :key="key"
        :label="key"
        :value="value"
        :ratio="'35% 65%'"
        :text-align="'right'"
        style="margin: 0px 0px 8px 0px"
      />
    </div>
    <div :data-isExpanded="isExpanded" class="bom-map-window-separator" style="margin-top: 4px" />
    <div
      :data-isExpanded="isExpanded"
      class="bom-map-window-inner-wrapper"
      data-responsive="true"
      style="margin-bottom: 0"
    >
      <BomMapDiagramPopupLabel
        v-for="(value, key) in demandInfoSchema2"
        :key="key"
        :label="key"
        :value="value"
        :ratio="'auto auto'"
        :text-align="'right'"
        style="margin: 0px 0px 8px 0px"
      />
    </div>
    <div :data-isExpanded="isExpanded" class="bom-map-window-inner-wrapper" style="margin-top: 0">
      <BomMapDiagramPopupLabel
        v-for="(value, key) in demandInfoSchema3"
        :key="key"
        :label="key"
        :value="value"
        :ratio="'auto auto'"
        :text-align="'right'"
        style="margin: 0px 0px 8px 0px"
      />
    </div>
    <!--    <div class="bom-map-window-information-footer">-->
    <!--      <div-->
    <!--        @click="onClickExpandHandler"-->
    <!--        :class="{-->
    <!--          'bom-map-text-button': true-->
    <!--        }"-->
    <!--        style="margin-right: 13px"-->
    <!--      >-->
    <!--        {{ isExpanded ? t('text-fold') : t('text-more') }}-->
    <!--      </div>-->
    <!--    </div>-->
  </div>
</template>

<script setup lang="ts">
import { useProjectInfoStore } from '../../../adapters/stores';
import { IconClose } from '@moz-shared/icons';
import { useTranslation } from 'i18next-vue';
import { computed, inject, ref, toRefs } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import BomMapDiagramPopupLabel from '../common/BomMapDiagramPopupLabel.vue';

type propsType = {
  demandInfos: any;
};
const props = defineProps<propsType>();
const { demandInfos } = toRefs(props);

const { interfaceConfigs } = inject('useBomMapInterface') as IBomMapIntefaceQuery;
const isExpanded = ref(false);
const { t } = useTranslation(); // 다국어
const projectModule = useProjectInfoStore();

const demandInfoSchema1 = computed(() => {
  if (!demandInfos.value) return null;
  return {
    'text-demand_id': [[demandInfos.value.demand_id]],
    // 'text-rtf': [[`${formatNumber(demandInfos.value.rtf_ratio)}% (${formatCompactNumber(demandInfos.value.rtf_qty, 1_000_000, '-')})`]],
    // 'text-demand_qty': [[formatCompactNumber(demandInfos.value.qty, 1_000_000, '-')]],
    // 'text-plan_dashboard-on_time_delivery': [
    //   [`${formatNumber(demandInfos.value.on_time_ratio)}% (${formatCompactNumber(demandInfos.value.on_time_qty, 1_000_000, '-')})`]
    // ],
    'text-rtf': [
      [`${formatNumber(demandInfos.value.rtf_ratio)}%`],
      { text: `${formatNumber(demandInfos.value.rtf_ratio)}% (${demandInfos.value.rtf_qty?.toLocaleString() || '-'})` },
    ],
    'text-demand_qty': [[demandInfos.value.qty?.toLocaleString() || '-']],
    'text-on_time_production': [
      [`${formatNumber(demandInfos.value.on_time_ratio)}%`],
      {
        text: `${formatNumber(demandInfos.value.on_time_ratio)}% (${demandInfos.value.on_time_qty?.toLocaleString() || '-'})`,
      },
    ],
    'text-due_datetime': [[projectModule.convertToFormat('dateTime', demandInfos.value.due_date)]],
    // 'text-short': [
    //   [`${formatNumber(demandInfos.value.short_ratio)}% (${formatCompactNumber(demandInfos.value.short_qty, 1_000_000, '-')})`]
    // ]
    'text-late_production': [
      [`${formatNumber(demandInfos.value.late_ratio)}%`],
      {
        text: `${formatNumber(demandInfos.value.late_ratio)}% (${demandInfos.value.late_qty?.toLocaleString() || '-'})`,
      },
    ],
    'text-bom_map-extended_due_datetime': [
      [projectModule.convertToFormat('dateTime', demandInfos.value.extended_due_date)],
    ],
    'text-short_production': [
      [`${formatNumber(demandInfos.value.short_ratio)}%`],
      {
        text: `${formatNumber(demandInfos.value.short_ratio)}% (${demandInfos.value.short_qty?.toLocaleString() || '-'})`,
      },
    ],
  };
});

const demandInfoSchema2 = computed(() => {
  if (!demandInfos.value) return null;
  return {
    'text-max_earliness_day': [[demandInfos.value.max_earliness_day?.toLocaleString() || '-']],
    'text-demand_priority': [[demandInfos.value.priority?.toLocaleString() || '-']],
    'text-max_lateness_day': [[demandInfos.value.max_lateness_day?.toLocaleString() || '-']],
    'text-cust_id': [[demandInfos.value.cust_id?.toLocaleString() || '-']],
  };
});

const demandInfoSchema3 = computed(() => {
  if (!demandInfos.value) return null;
  return {
    [`${t('text-demand_item_id')} / ${t('text-name')}`]: [
      [`${demandInfos.value.item_id} / ${demandInfos.value.item_name}` || demandInfos.value.item_id],
    ],
    [`${t('text-demand_site_id')} / ${t('text-name')}`]: [
      [
        `${demandInfos.value.site_id} / ${
          demandInfos.value.site_name !== null ? demandInfos.value.site_name : demandInfos.value.site_id
        }`,
      ],
    ],
  };
});

const onClickExpandHandler = () => {
  isExpanded.value = !isExpanded.value;
};

const formatNumber = (number: number) => {
  if (Number.isInteger(number)) {
    return number?.toString();
  }
  return number?.toFixed(1);
};

const closeHandler = () => {
  interfaceConfigs.value.window.demandInfo.isShown = false;
};
</script>

<style>
.extended-window-edge {
  & .bom-map-demand-information-outer-wrapper {
    width: 100%;
    min-width: 342px;
    height: 100%;

    & .bom-map-window-inner-wrapper {
      /* padding: 0px 10px; */
    }
  }
}

.bom-map-demand-information-outer-wrapper {
  min-width: 342px;
  height: fit-content;
  background-color: #ffffff;
  z-index: 10;

  container-type: inline-size;
  container-name: parent; /* 쿼리 컨테이너 이름 지정 */
}

@container parent (min-width: 0px) {
  /* 쿼리 컨테이너 이름 사용 */
  .bom-map-window-inner-wrapper[data-responsive='true'] {
    display: grid;
    grid-template-columns: calc(58% - 12px) calc(42% - 12px);
    justify-content: space-between;
  }
}

.bom-map-window-separator[data-isExpanded='false'] {
  display: none;
}
.bom-map-window-inner-wrapper[data-isExpanded='false'] {
  display: none;
}
</style>
