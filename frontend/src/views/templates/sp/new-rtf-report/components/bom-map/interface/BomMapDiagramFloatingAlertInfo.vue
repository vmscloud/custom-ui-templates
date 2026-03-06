<template>
  <BomMapDiagramFloating
    v-if="getDiagram"
    :getDiagram="getDiagram"
    :floatingPosition="'bottom'"
    :node="userAction.clickAlert.current.node as go.Node"
    :initialized="initialized"
    :correction="
      (nodeWidth: number, nodeHeight: number) => {
        return {
          x: nodeWidth / 2 - 16,
          y: nodeHeight + (userAction.clickAlert.current.node?.data.type === 'bom' ? -10 : -20),
        };
      }
    "
  >
    <template #alertInfo="{ props }">
      <div class="bom-map-floating-alert" style="padding: 11px 11px 7px 11px" :data-isExpanded="isExpanded">
        <ExtendFlexGrid
          v-if="isExpanded"
          class="bom-map-floating-info-grid"
          :style="{ width: 'calc(100% - 1px)', height: 'fit-content' }"
          :alternatingRowStep="0"
          :itemsSource="userAction.clickAlert.current.node?.data.alerts"
          :isReadOnly="true"
          :use-tool-box="false"
          :use-extend-footer="false"
          :initialized="onInitialized"
          :formatItem="formatItem"
          :name="'bom-map-diagram-floating-alert-info-grid1'"
        >
          <WjFlexGridColumn
            v-if="userAction.clickAlert.current.node?.data.type === 'bom'"
            :width="73"
            binding="oper_id"
            :header="t('text-oper_id')"
          />
          <WjFlexGridColumn :width="380" binding="short_reason" :header="t('text-short_reason')">
            <WjFlexGridCellTemplate cellType="Cell" v-slot="cell">
              <div class="bom-map-floating-grid-short-reason-expanded">
                <div
                  v-tooltip="{
                    text: `${cell.item.short_reason}: ${t(`desc-${cell.item.short_type}-${cell.item.short_category}${cell.item.short_category !== 'Factor' ? '-' + cell.item.short_reason : ''}`)}`,
                    onlyEllipsis: true,
                  }"
                >
                  <span
                    :style="{
                      backgroundColor: ALERT_COLOR[cell.item.short_type?.toUpperCase()].FILL,
                    }"
                  >
                    {{ convertToInternationalization(cell.item.short_reason, 'short') }}
                  </span>
                  {{
                    t(
                      `desc-${cell.item.short_type}-${cell.item.short_category}${cell.item.short_category !== 'Factor' ? '-' + cell.item.short_reason : ''}`,
                    )
                  }}
                </div>
              </div>
            </WjFlexGridCellTemplate>
          </WjFlexGridColumn>
          <WjFlexGridColumn
            :width="100"
            binding="short_qty"
            :header="t('text-short_qty')"
            dataType="Number"
            :format="projectModule.formatGrid('qty')"
          />
          <!--          <WjFlexGridColumn-->
          <!--            v-if="userAction.clickAlert.current.node?.data.type === 'bom'"-->
          <!--            :width="100"-->
          <!--            binding="res_id"-->
          <!--            :header="t('text-res_id')"-->
          <!--          />-->
          <WjFlexGridColumn :width="360" binding="short_detail_info" :header="t('text-short_detail_info')">
            <WjFlexGridCellTemplate cellType="Cell" v-slot="cell">
              <div class="bom-map-floating-grid-short-detail-info-expanded">
                {{ cell.item.short_detail_info }}
              </div>
            </WjFlexGridCellTemplate>
          </WjFlexGridColumn>
        </ExtendFlexGrid>
        <ExtendFlexGrid
          v-else
          class="bom-map-floating-info-grid"
          style="height: fit-content"
          :alternatingRowStep="0"
          :itemsSource="userAction.clickAlert.current.node?.data.alerts"
          :isReadOnly="true"
          :use-tool-box="false"
          :use-extend-footer="false"
          :initialized="onInitialized"
          :formatItem="formatItem"
          :name="'bom-map-diagram-floating-alert-info-grid2'"
        >
          <WjFlexGridColumn
            v-if="userAction.clickAlert.current.node?.data.type === 'bom'"
            :width="73"
            binding="oper_id"
            :header="t('text-oper_id')"
          />
          <WjFlexGridColumn :width="120" binding="short_reason" :header="t('text-short_reason')">
            <WjFlexGridCellTemplate cellType="Cell" v-slot="cell">
              <div class="bom-map-floating-grid-short-reason">
                <span
                  :style="{
                    backgroundColor: ALERT_COLOR[cell.item.short_type?.toUpperCase()].FILL,
                  }"
                  v-tooltip="{
                    text: `${cell.item.short_reason}: ${t(`desc-${cell.item.short_type}-${cell.item.short_category}${cell.item.short_category !== 'Factor' ? '-' + cell.item.short_reason : ''}`)}`,
                    onlyEllipsis: false,
                  }"
                >
                  {{ convertToInternationalization(cell.item.short_reason, 'short') }}
                </span>
              </div>
            </WjFlexGridCellTemplate>
          </WjFlexGridColumn>
          <WjFlexGridColumn :width="100" binding="short_qty" :header="t('text-short_qty')" />
          <!--          <WjFlexGridColumn-->
          <!--            v-if="userAction.clickAlert.current.node?.data.type === 'bom'"-->
          <!--            :width="100"-->
          <!--            binding="res_id"-->
          <!--            :header="t('text-res_id')"-->
          <!--          />-->
          <WjFlexGridColumn :width="470" binding="short_detail_info" :header="t('text-short_detail_info')" />
        </ExtendFlexGrid>
        <div
          @click="onClickExpandHandler"
          :class="{
            'bom-map-text-button': true,
          }"
          style="margin-top: 5px"
        >
          {{ isExpanded ? t('text-collapse_view') : t('text-expand_view') }}
        </div>
      </div>
    </template>
  </BomMapDiagramFloating>
</template>
<script setup lang="ts">
import { useProjectInfoStore } from '../../../adapters/stores';
import { AllowMerging, FlexGrid } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { WjFlexGridCellTemplate, WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import { ExtendFlexGrid } from '@vmscloud/moz-wijmo-grid';
import { ExtendGrid } from '@vmscloud/moz-wijmo-grid';
import { isDataCell } from '@vmscloud/moz-wijmo-grid/utils';
import { convertToInternationalization } from '@moz-shared/utils';
import { Diagram } from 'gojs';
import { useTranslation } from 'i18next-vue';
import { inject, ref, toRefs } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import { ALERT_COLOR } from '../common/BomMapConstants';
import BomMapDiagramFloating from '../common/BomMapDiagramFloating.vue';

type propsType = {
  getDiagram: () => Diagram;
};

const props = defineProps<propsType>();
const { getDiagram } = toRefs(props);
const { t } = useTranslation(); // 다국어
const { userAction } = inject('useBomMapInterface') as IBomMapIntefaceQuery;
const contextRef = ref();
const grid = ref<FlexGrid | null>(null); // Wijmo grid
const extendGrid = ref<ExtendGrid | null>(null); // Wijmo grid 확장 기능
const isExpanded = ref(true);
const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
  extendGrid.value = _extendGrid;

  grid.value.autoRowHeights = true;
  grid.value.allowMerging = AllowMerging.All;
  grid.value.columns[0].allowMerging = true;
};

const projectModule = useProjectInfoStore();

const formatItem = (s: FlexGrid, e: any) => {
  if (!isDataCell(s, e)) return;

  if (e?.getColumn()?.binding === 'short_reason') {
    e.cell.classList.add('short-reason-height');
  }

  if (e.cell.innerText.trim() === '') {
    e.cell.classList.add('bom-map-empty-status');
  }
};

const onClickExpandHandler = () => {
  isExpanded.value = !isExpanded.value;
};

const initialized = (componentRef: any) => {
  contextRef.value = componentRef;
};

defineExpose({ context: contextRef });
</script>
<style lang="scss">
.bom-map-floating-alert {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.bom-map-floating-alert[data-isExpanded='false'] {
  z-index: 3 !important;

  & .wj-cell {
    width: 100%;
    overflow: hidden;

    &:has(.bom-map-floating-grid-short-reason) {
      padding: 0;
    }

    & > div:has(div) {
      width: 100%;
      height: 100%;
      overflow: hidden;

      & > div:has(div) {
        width: 100%;
        height: 100%;
      }
    }
  }
}

.bom-map-floating-grid-short-reason {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  overflow: hidden;
  padding: 10px;

  & > span {
    padding: 0 8px;
    line-height: 16px;
    color: white !important;
    height: 16px;
    border-radius: 16px;
    text-overflow: ellipsis;
    white-space: nowrap;
    word-wrap: normal;
    overflow: hidden;
  }
}

.bom-map-floating-grid-short-reason-expanded {
  display: flex;
  align-items: center;

  & > div {
    width: 100%;
    height: fit-content;
    overflow: hidden;
    padding: 7px 0px;
    word-break: break-all;

    & > span {
      padding: 0 8px;
      line-height: 16px;
      color: white !important;
      height: 16px;
      border-radius: 16px;
      text-overflow: ellipsis;
      white-space: nowrap;
      word-wrap: normal;
      overflow: hidden;
    }
  }
}

.bom-map-floating-grid-short-detail-info-expanded {
  padding: 7px 0px;
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

.bom-map-floating-info-grid {
  .wj-cell.short-reason-height {
    // Wijmo의 글자수 계산을 통한 height와 css의 fit-content가 일치하지 않는 경우가 있음 ==> 운없는 높이 :(
    // 근데 이걸 빼버리면 처음에 높이 계산이 제대로 안됨... 좋은 방법 있으면 코드 수정 바랍니다.
    height: fit-content !important;
  }
}
</style>
