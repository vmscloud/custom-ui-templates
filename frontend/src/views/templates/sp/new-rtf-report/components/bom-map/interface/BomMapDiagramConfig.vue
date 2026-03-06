<template>
  <div :class="[`bom-map-setting-outer-wrapper`]" :style="{ opacity: `${interfaceConfigs.window.config.opacity}%` }">
    <div class="bom-map-window-title-wrapper">
      <div>{{ t('text-setting') }}</div>
      <div class="bom-map-window-title-right">
        <input
          @mousedown="(e) => e.stopPropagation()"
          type="range"
          min="30"
          max="100"
          value="50"
          class="bom-map-window-slider"
          v-model="interfaceConfigs.window.config.opacity"
        />
        <IconClose style="cursor: pointer" @mousedown="closeHandler" />
      </div>
    </div>
    <div class="bom-map-window-inner-wrapper">
      <BomMapDiagramPopupLabel
        :label="t('text-item_label')"
        :ratio="'40% 60%'"
        :text-align="'right'"
        :align-center="true"
        style="margin: 0px 0px 8px 0px"
      >
        <div style="width: 100%; display: flex; justify-content: flex-end">
          <Select
            v-model="diagramConfigs.bufferNode.label1"
            :itemsSource="configSource.itemLabel"
            :displayProp="'label'"
            :keyProp="'key'"
            :width="180"
          />
        </div>
      </BomMapDiagramPopupLabel>
      <BomMapDiagramPopupLabel
        :label="t('text-site_label')"
        :ratio="'40% 60%'"
        :text-align="'right'"
        :align-center="true"
        style="margin: 0px 0px 8px 0px"
      >
        <div style="width: 100%; display: flex; justify-content: flex-end">
          <Select
            v-model="diagramConfigs.bufferNode.label2"
            :itemsSource="configSource.siteLabel"
            :displayProp="'label'"
            :keyProp="'key'"
            :width="180"
          />
        </div>
      </BomMapDiagramPopupLabel>
      <BomMapDiagramPopupLabel
        :label="t('text-bom_id_label')"
        :ratio="'40% 60%'"
        :text-align="'right'"
        :align-center="true"
        style="margin: 0px 0px 8px 0px"
      >
        <div style="width: 100%; display: flex; justify-content: flex-end">
          <Select
            v-model="diagramConfigs.bomNode.label1"
            :itemsSource="configSource.bomLabel"
            :displayProp="'label'"
            :keyProp="'key'"
            :width="180"
          />
        </div>
      </BomMapDiagramPopupLabel>
      <BomMapDiagramPopupLabel
        :label="t('text-bom_tat_label')"
        :ratio="'40% 60%'"
        :text-align="'right'"
        :align-center="true"
        style="margin: 0px 0px 8px 0px"
      >
        <div style="width: 100%; display: flex; justify-content: flex-end">
          <Select
            v-model="diagramConfigs.bomNode.headerLabel1"
            :itemsSource="configSource.bomHeaderLabel"
            :displayProp="'label'"
            :keyProp="'key'"
            :width="180"
          />
        </div>
      </BomMapDiagramPopupLabel>
    </div>
    <div class="bom-map-window-separator" />
    <div class="bom-map-window-inner-wrapper">
      <BomMapDiagramPopupLabel
        :label="t('text-initial_screen')"
        :ratio="'40% 60%'"
        :text-align="'right'"
        :align-center="true"
        style="margin: 0px 0px 8px 0px"
      >
        <div style="width: 100%; display: flex; justify-content: flex-end">
          <Select
            v-model="diagramConfigs.initialViewPoint"
            :itemsSource="configSource.initialViewPoint"
            :displayProp="'label'"
            :keyProp="'key'"
            :width="180"
          />
        </div>
      </BomMapDiagramPopupLabel>
      <BomMapDiagramPopupLabel
        :label="t('text-initial_layout')"
        :ratio="'40% 60%'"
        :text-align="'right'"
        :align-center="true"
        style="margin: 0px 0px 16px 0px"
      >
        <div style="width: 100%; display: flex; justify-content: flex-end">
          <Select
            v-model="diagramConfigs.layoutMode"
            :itemsSource="configSource.layoutMode"
            :displayProp="'label'"
            :keyProp="'key'"
            :width="180"
            :rules="[
              {
                message: t('msg-bom_map-require-refresh-to-apply'),
                validator: () => false,
                type: 'change',
              },
            ]"
          />
        </div>
      </BomMapDiagramPopupLabel>
    </div>

    <!--    <div class="bom-map-window-separator" />-->
    <!--    <div class="bom-map-window-inner-wrapper">-->
    <!--      <BomMapDiagramPopupLabel-->
    <!--        :label="t('text-qty_unit')"-->
    <!--        :ratio="'40% 60%'"-->
    <!--        :text-align="'right'"-->
    <!--        :align-center="true"-->
    <!--        style="margin: 0px 0px 8px 0px"-->
    <!--      >-->
    <!--        <div style="width: 100%; display: flex; justify-content: flex-end">-->
    <!--          <Select v-model="diagramConfigs.qtyUnit" :itemsSource="configSource.qtyUnit" :displayKey="'label'" />-->
    <!--        </div>-->
    <!--      </BomMapDiagramPopupLabel>-->
    <!--    </div>-->
    <div class="bom-map-window-information-footer" style="display: flex; justify-content: flex-end; gap: 8px">
      <div @click="onClickResetHandler" class="bom-map-text-button" style="margin-right: 13px">
        {{ t('text-reset_setting') }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Select } from '@vmscloud/moz-ui-components';
import { IconClose } from '@moz-shared/icons';
import { useTranslation } from 'i18next-vue';
import { inject } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import BomMapDiagramPopupLabel from '../common/BomMapDiagramPopupLabel.vue';

const { t } = useTranslation(); // 다국어
const { diagramConfigs, interfaceConfigs, diagramConfigsOri, setData } = inject(
  'useBomMapInterface',
) as IBomMapIntefaceQuery;

const closeHandler = () => {
  setData(() => {
    interfaceConfigs.value.window.config.isShown = false;
  });
};

const configSource = {
  itemLabel: [
    { label: t('text-name'), key: 'itemName' },
    { label: t('text-id'), key: 'itemID' },
  ],
  siteLabel: [
    { label: t('text-no_label'), key: 'hide' },
    { label: t('text-name'), key: 'siteName' },
    { label: t('text-id'), key: 'siteID' },
  ],
  bomHeaderLabel: [
    { label: t('text-no_label'), key: 'hide' },
    { label: t('text-yes_label'), key: 'routingTat' },
  ],
  bomLabel: [
    { label: t('text-no_label'), key: 'hide' },
    { label: t('text-yes_label'), key: 'bomID' },
  ],
  qtyUnit: [
    { label: t('text-demand_qty_unit'), key: 'planUnitQty' },
    { label: t('text-isb_qty_unit'), key: 'planQty' },
  ],
  layoutMode: [
    { label: t('text-bom_map-layout1'), key: 0 },
    { label: t('text-bom_map-layout2'), key: 1 },
  ],
  initialViewPoint: [
    { label: t('text-bom_map-toolbar_fit_to_screen'), key: 'fitToScreen' },
    { label: t('text-bom_map-toolbar_fit_to_bom'), key: 'fitToBom' },
  ],
};

const onClickResetHandler = () => {
  // const resetData = {
  //   bufferNode: {
  //     label1: 'itemID',
  //     label2: 'siteID'
  //   },
  //   bomNode: {
  //     headerLabel1: 'hide'
  //   },
  //   qtyUnit: 'planQty',
  //   initialViewPoint: 'fitToScreen',
  //   configsVersion: '0.1.0'
  // };

  setData(() => {
    diagramConfigs.value = diagramConfigsOri;
  });
};
</script>
<style>
.extended-window-edge {
  & .bom-map-setting-outer-wrapper {
    width: 100%;
  }
}

.bom-map-setting-outer-wrapper {
  background-color: white;
  width: 350px;
  height: 100%;
}
</style>
