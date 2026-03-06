<template>
  <div class="bom-map-legends-outer-wrapper">
    <div class="bom-map-legends-item-wrapper">
      <div class="bom-map-legends-item-alert" style="background-color: #dc5a5a; border: 1px solid #993d48"></div>
      {{ t('text-bom_map-legend_short') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <div class="bom-map-legends-item-alert" style="background-color: #fa9e23; border: 1px solid #e68600"></div>
      {{ t('text-bom_map-legend_late') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <IconBomMapLegendTriangle fill="#BAC6D4" stroke="#6A7184" />
      {{ t('text-bom_map-legend_material') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <IconBomMapLegendSquare fill="#FFFFFF" stroke="#6A7184" />
      {{ t('text-bom_map-legend_dummy') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <IconBomMapLegendSquare fill="#DDDDEC" stroke="#6A7184" />
      {{ t('text-bom_map-legend_operation') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <IconBomMapArrow color="#6A7184" />
      {{ t('text-bom_map-legend_normal') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <IconBomMapArrow color="#F28270" />
      {{ t('text-bom_map-legend_assembly') }}
    </div>
    <div class="bom-map-legends-item-separator" />
    <div class="bom-map-legends-item-wrapper">
      <IconBomMapArrow color="#A768D6" />
      {{ t('text-bom_map-legend_split') }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { useTranslation } from 'i18next-vue';
import IconBomMapArrow from '../assets/IconBomMapArrow.vue';
import IconBomMapLegendSquare from '../assets/IconBomMapLegendSquare.vue';
import IconBomMapLegendTriangle from '../assets/IconBomMapLegendTriangle.vue';

const { t } = useTranslation(); // 다국어
</script>
<style lang="scss" scoped>
.bom-map-legends-outer-wrapper {
  // position: absolute;
  // bottom: -1px;
  z-index: 3;
  width: 100%;
  height: 32px;
  background-color: #f8f8fd;
  // border: 1px solid #c1c1d8;
  display: flex;
  align-items: center;
  padding-left: 32px;
}

.bom-map-legends-item-wrapper {
  padding: 0 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: #28364e;
}

.bom-map-legends-item-separator {
  width: 1px;
  height: 10px;
  background-color: #c1c1d8;
}

.bom-map-legends-item-alert {
  width: 20px;
  height: 20px;
  justify-content: center;
  align-items: center;
  display: flex;
  border-radius: 100%;
  border: 1px solid;
}
</style>
