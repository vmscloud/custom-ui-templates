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
        <MozGrid
          v-if="isExpanded"
          :key="`expanded-${gridKey}`"
          class="bom-map-floating-info-grid"
          :style="{ width: 'calc(100% - 1px)' }"
          :height="gridHeight"
          :coreConfig="expandedCoreConfig"
          :use-tool-box="false"
          :use-extend-footer="false"
          :name="'bom-map-diagram-floating-alert-info-grid1'"
          @ready="onReady"
        >
          <CellTemplate field="short_reason" #default="{ rowData }">
            <div class="bom-map-floating-grid-short-reason-expanded">
              <div
                v-tooltip="{
                  text: `${rowData.short_reason}: ${t(shortDescKey(rowData))}`,
                  onlyEllipsis: true,
                }"
              >
                <span
                  :style="{
                    backgroundColor: alertFill(rowData),
                  }"
                >
                  {{ convertToInternationalization(rowData.short_reason, 'short') }}
                </span>
                {{ t(shortDescKey(rowData)) }}
              </div>
            </div>
          </CellTemplate>
          <CellTemplate field="short_detail_info" #default="{ rowData }">
            <div class="bom-map-floating-grid-short-detail-info-expanded">
              {{ rowData.short_detail_info }}
            </div>
          </CellTemplate>
        </MozGrid>
        <MozGrid
          v-else
          :key="`collapsed-${gridKey}`"
          class="bom-map-floating-info-grid"
          :height="gridHeight"
          :coreConfig="collapsedCoreConfig"
          :use-tool-box="false"
          :use-extend-footer="false"
          :name="'bom-map-diagram-floating-alert-info-grid2'"
          @ready="onReady"
        >
          <CellTemplate field="short_reason" #default="{ rowData }">
            <div class="bom-map-floating-grid-short-reason">
              <span
                :style="{
                  backgroundColor: alertFill(rowData),
                }"
                v-tooltip="{
                  text: `${rowData.short_reason}: ${t(shortDescKey(rowData))}`,
                  onlyEllipsis: false,
                }"
              >
                {{ convertToInternationalization(rowData.short_reason, 'short') }}
              </span>
            </div>
          </CellTemplate>
        </MozGrid>
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
import { ROW_KEY, withRowKey } from '../../../adapters/utils';
import { CellTemplate, MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { FieldDef, GridChrome, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
import { convertToInternationalization } from '@moz-shared/utils';
import { Diagram } from 'gojs';
import { useTranslation } from 'i18next-vue';
import { computed, inject, ref, toRefs } from 'vue';
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
const isExpanded = ref(true);

const alerts = computed<any[]>(() => userAction.value.clickAlert.current.node?.data.alerts ?? []);
const isBomNode = computed(() => userAction.value.clickAlert.current.node?.data.type === 'bom');
// 노드 종류가 바뀌면 그리드를 다시 만든다 (컬럼 구성과 병합 설정이 노드 종류에 따라 달라짐)
const gridKey = computed(() => (isBomNode.value ? 'bom' : 'buffer'));

// 옛 그리드의 fit-content 높이를 대신해 행 수로 높이를 정한다
const ROW_HEIGHT = { expanded: 56, collapsed: 36 };
const HEADER_HEIGHT = 32;
const gridHeight = computed(
  () =>
    HEADER_HEIGHT +
    2 +
    Math.max(alerts.value.length, 1) * (isExpanded.value ? ROW_HEIGHT.expanded : ROW_HEIGHT.collapsed),
);

const shortDescKey = (item: any) =>
  `desc-${item.short_type}-${item.short_category}${item.short_category !== 'Factor' ? '-' + item.short_reason : ''}`;

const alertFill = (item: any) => (ALERT_COLOR as any)[item.short_type?.toUpperCase()]?.FILL;

const emptyCellAttributes = ({ value, columnId }: { value: unknown; columnId: string }) => {
  const classes: string[] = [];
  if (columnId === 'short_reason') classes.push('short-reason-height');
  if (String(value ?? '').trim() === '') classes.push('bom-map-empty-status');
  return classes.length ? { class: classes.join(' ') } : undefined;
};

const buildCoreConfig = (expanded: boolean): MozGridCoreProps => {
  const qtyMask = projectModule.maskGrid('qty');
  const operFields: FieldDef[] = isBomNode.value
    ? [{ id: 'oper_id', header: t('text-oper_id'), dataType: 'string', width: 73 }]
    : [];
  const fields: FieldDef[] = [
    ...operFields,
    { id: 'short_reason', header: t('text-short_reason'), dataType: 'string', width: expanded ? 380 : 120 },
    {
      id: 'short_qty',
      header: t('text-short_qty'),
      dataType: 'number',
      width: 100,
      ...(expanded ? { mask: qtyMask } : {}),
    },
    // { id: 'res_id', header: t('text-res_id'), width: 100 },  (bom 노드만)
    { id: 'short_detail_info', header: t('text-short_detail_info'), dataType: 'string', width: expanded ? 360 : 470 },
  ];

  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: withRowKey(alerts.value),
    headerHeight: HEADER_HEIGHT,
    rowHeight: expanded ? ROW_HEIGHT.expanded : ROW_HEIGHT.collapsed,
    dynamicRowHeights: expanded,
    fields: fields.map((field) => ({ ...field, sortable: false, cellAttributes: emptyCellAttributes })),
  };
};

const expandedCoreConfig = computed(() => buildCoreConfig(true));
const collapsedCoreConfig = computed(() => buildCoreConfig(false));

const onReady = (grid: PureSheet, _chrome: GridChrome) => {
  // 첫 컬럼(공정)의 같은 값을 세로로 병합한다
  if (isBomNode.value) grid.setMergeConfig({ type: 'content', columns: ['oper_id'] });
};

const projectModule = useProjectInfoStore();

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

  & .ps-cell {
    overflow: hidden;

    &:has(.bom-map-floating-grid-short-reason) {
      padding: 0;
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
  .ps-cell.short-reason-height {
    white-space: normal;
  }
}
</style>
