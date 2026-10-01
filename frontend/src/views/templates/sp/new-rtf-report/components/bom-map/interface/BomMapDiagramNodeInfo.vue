<template>
  <div
    :class="[`bom-map-node-information-outer-wrapper`]"
    :style="{ opacity: `${interfaceConfigs.window.nodeInfo.opacity}%` }"
  >
    <div class="bom-map-window-title-wrapper">
      <div>
        {{
          userAction.click.current.node?.data?.type === 'buffer'
            ? t('text-upper-isb_information')
            : t('text-upper-bom_information')
        }}
      </div>
      <div class="bom-map-window-title-right">
        <input
          @mousedown="(e) => e.stopPropagation()"
          type="range"
          min="30"
          max="100"
          value="50"
          class="bom-map-window-slider"
          v-model="interfaceConfigs.window.nodeInfo.opacity"
        />
        <!--        <IconClose style="cursor: pointer" @mousedown="closeHandler" />-->
      </div>
    </div>
    <div v-show="userAction.click.current.node?.data?.type === 'buffer' && isbDataSource?.bomMapIsbInfo?.item_id">
      <div class="bom-map-window-inner-wrapper">
        <div
          class="bom-map-window-inner-sub-wrapper"
          style="padding: 12px 12px; border: 1px solid #e1e3f0; background-color: #f8f8fd"
        >
          <BomMapDiagramPopupLabel
            v-for="(value, key, idx) in isbInfoSchema1"
            :key="key"
            :label="key"
            :value="value"
            :ratio="'calc(47% + 2px) calc(53% - 2px)'"
            :copy-index="0"
          />
        </div>
      </div>
      <div class="bom-map-window-inner-wrapper" style="display: grid; grid-template-columns: 47% 53%">
        <div class="bom-map-window-inner-sub-wrapper">
          <div class="bom-map-window-sub-title">{{ t('text-bom_map-wip_usage_info') }}</div>
          <BomMapDiagramPopupLabel
            v-for="(value, key, idx) in isbInfoSchema2"
            :key="key"
            :label="key"
            :value="value"
            :ratio="'auto auto'"
            :text-align="'right'"
          />
        </div>
        <div class="bom-map-window-inner-sub-wrapper">
          <div class="bom-map-window-sub-title">{{ t('text-bom_map-intarget_info') }}</div>
          <BomMapDiagramPopupLabel
            v-for="(value, key, idx) in isbInfoSchema3"
            :key="key"
            :label="key"
            :value="value"
            :ratio="'auto auto'"
            :text-align="'right'"
          />
        </div>
      </div>
      <div class="bom-map-window-separator" />
      <div class="bom-map-window-inner-wrapper">
        <div class="bom-map-window-inner-sub-wrapper">
          <div class="bom-map-window-sub-title">{{ t('text-bom_map-prod_plan_info') }}</div>
          <template v-if="isbDataSource?.bomMapIsbInfo?.target_datetime">
            <BomMapDiagramPopupLabel
              v-for="(value, key, idx) in isbInfoSchema4"
              :key="key"
              :label="key"
              :value="value"
              :ratio="'90px 220px'"
              :text-align="'left'"
            />
            <BomMapDiagramPopupLabel
              v-for="(value, key, idx) in isbInfoSchema5"
              :key="key"
              :label="key"
              :value="value"
              :ratio="'90px 103.5px'"
              :text-align="'right'"
            />
          </template>
          <div v-else class="bom-map-info-empty" style="width: 100%; height: 81.5px">
            <span style="width: 150px; word-break: keep-all; white-space: pre-wrap; text-align: center">
              {{ t('desc-bom_map-no_target') }}
            </span>
          </div>
        </div>
      </div>
      <div class="bom-map-window-separator" />
      <div class="bom-map-window-inner-wrapper">
        <Tab v-model="currentTab" :itemSource="isbTabs" :closeAble="false">
          <!-- :tabWidth="80" -->
          <template #bomMapItemProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="isbDataSource?.bomMapItemProp?.length">
                {{ isbDataSource?.bomMapItemProp?.length }}
              </div>
            </div>
          </template>
          <template #bomMapSiteProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="isbDataSource?.bomMapSiteProp?.length">
                {{ isbDataSource?.bomMapSiteProp?.length }}
              </div>
            </div>
          </template>
          <template #bomMapBufferProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="isbDataSource?.bomMapBufferProp?.length">
                {{ isbDataSource?.bomMapBufferProp?.length }}
              </div>
            </div>
          </template>
          <template #bomMapIsbProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="isbDataSource?.bomMapIsbProp?.length">
                {{ isbDataSource?.bomMapIsbProp?.length }}
              </div>
            </div>
          </template>
          <template #[tab.id] v-for="tab in isbTabs">
            <MozGrid
              :key="tab.id"
              v-if="tab.id in isbDataSource && isbDataSource[tab.id]?.length"
              class="bom-map-isb-info-grid"
              style="display: grid; max-width: 100%; overflow: hidden"
              :height="230"
              :coreConfig="isbPropCoreConfigs[tab.id]"
              :use-tool-box="false"
              :use-extend-footer="false"
              :useContextMenu="false"
              :name="'bom-map-diagram-node-info-grid1'"
            />
            <div v-else class="bom-map-info-empty" data-border="true" style="width: 100%; height: 115px">
              <span style="width: 150px; word-break: keep-all; white-space: pre-wrap; text-align: center">
                {{ t('msg-data_empty') }}
              </span>
            </div>
          </template>
        </Tab>
      </div>
    </div>
    <div v-show="userAction.click.current.node?.data?.type === 'bom' && bomDataSource?.bomMasterInfo">
      <div class="bom-map-window-inner-wrapper">
        <div
          class="bom-map-window-inner-sub-wrapper"
          style="padding: 12px 12px; border: 1px solid #e1e3f0; background-color: #f8f8fd"
        >
          <BomMapDiagramPopupLabel
            v-for="(value, key, idx) in bomInfoSchema1"
            :key="key"
            :label="key"
            :value="value"
            :ratio="'auto auto'"
            :copy-index="0"
            :textAlign="'right'"
          />
        </div>
      </div>
      <div class="bom-map-window-separator" />
      <div class="bom-map-window-inner-wrapper" style="display: grid">
        <div class="bom-map-window-sub-title">{{ t('text-bom_map-prod_plan_info') }}</div>
        <div
          v-if="bomDataSource?.bomMapRouteInfos?.length"
          :style="{
            minHeight: '231px',
            maxWidth: '100%',
            display: 'grid',
            overflow: 'hidden',
            borderRight: '1px solid #c1c1d8',
            borderBottom: '1px solid #c1c1d8',
          }"
        >
          <MozGrid
            class="bom-map-bom-information-multirow"
            :style="{ width: 'calc(100% + 2px)', height: 'calc(100% + 2px)' }"
            :height="routeGridHeight"
            :coreConfig="routeCoreConfig"
            :use-tool-box="false"
            :use-extend-footer="false"
            :useContextMenu="false"
            :useSort="false"
          >
            <CellTemplate field="total_tat" #default="{ value }">
              <div
                class="bom-map-node-info-column-template-wrapper"
                v-tooltip="{
                  text: formatDuration(Number(value)),
                  onlyEllipsis: true,
                }"
              >
                {{ formatDuration(Number(value)) }}
              </div>
            </CellTemplate>
            <CellTemplate field="elapse_sec" #default="{ value }">
              <div
                class="bom-map-node-info-column-template-wrapper"
                v-tooltip="{
                  text: formatDuration(Number(value)),
                  onlyEllipsis: true,
                }"
              >
                {{ formatDuration(Number(value)) }}
              </div>
            </CellTemplate>
          </MozGrid>
        </div>

        <div v-else class="bom-map-info-empty" data-border="true" style="width: 100%; height: 231px">
          <span style="width: 150px; word-break: keep-all; white-space: pre-wrap; text-align: center">
            {{ t('desc-bom_map-no_target') }}
          </span>
        </div>
      </div>
      <div class="bom-map-window-separator" />
      <div class="bom-map-window-inner-wrapper">
        <Tab v-model="currentBomTab" :itemSource="bomTabs" :closeAble="false">
          <template #bomMapBomProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="bomDataSource?.bomMapBomProp?.length">
                {{ bomDataSource?.bomMapBomProp?.length }}
              </div>
            </div>
          </template>
          <template #bomMapRoutingProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="bomDataSource?.bomMapRoutingProp?.length">
                {{ bomDataSource?.bomMapRoutingProp?.length }}
              </div>
            </div>
          </template>
          <template #bomMapOperProp-tab="{ text, active }: any">
            <div class="bom-map-window-tab-wrapper" :class="{ active }">
              {{ text }}
              <div class="bom-map-window-badge" :data-count="bomDataSource?.bomMapOperProp?.length">
                {{ bomDataSource?.bomMapOperProp?.length }}
              </div>
            </div>
          </template>
          <template #[tab.id] v-for="tab in bomTabs">
            <MozGrid
              v-if="tab.id in bomDataSource && bomDataSource[tab.id]?.length"
              :key="tab.id"
              class="bom-map-isb-info-grid"
              style="display: grid; max-width: 100%; overflow: hidden"
              :height="230"
              :coreConfig="bomPropCoreConfigs[tab.id]"
              :use-tool-box="false"
              :use-extend-footer="false"
              :useContextMenu="false"
              :name="'bom-map-diagram-node-info-grid2'"
              @ready="onBomGridReady"
            />
            <div v-else class="bom-map-info-empty" data-border="true" style="width: 100%; height: 115px">
              <span style="width: 150px; word-break: keep-all; white-space: pre-wrap; text-align: center">
                {{ t('msg-data_empty') }}
              </span>
            </div>
          </template>
        </Tab>
      </div>
    </div>

    <!--    선택된 노드가 없거나 페칭중일 때... 지금은 필요성이 없어보임-->
    <!--    <div-->
    <!--      v-show="-->
    <!--        !(userAction.click.current.node?.data?.type === 'buffer' && isbDataSource?.bomMapIsbInfo?.item_id) &&-->
    <!--        !(userAction.click.current.node?.data?.type === 'bom' && bomDataSource?.bomMasterInfo)-->
    <!--      "-->
    <!--    >-->
    <!--      <div style="display: flex; justify-content: center; align-items: center; padding: 16px 0; font-size: 12px; color: #28364e">-->
    <!--        노드 데이터를 불러오는 중입니다.-->
    <!--      </div>-->
    <!--    </div>-->
    <!--    <div v-show="!userAction.click.current.node">-->
    <!--      <div style="display: flex; justify-content: center; align-items: center; padding: 16px 0; font-size: 12px; color: #28364e">-->
    <!--        선택된 노드가 없습니다.-->
    <!--      </div>-->
    <!--    </div>-->
  </div>
</template>
<script setup lang="ts">
import { apiCall } from '../../../adapters/stores';
import { useProjectInfoStore } from '../../../adapters/stores';
import { ROW_KEY, withRowKey } from '../../../adapters/utils';
import { CellTemplate, MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { GridChrome, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
import { Tab } from '@vmscloud/moz-ui-components-vue';
import { formatCompactNumber, showMessage, dayjs } from '@moz-shared/utils';
import { useMutation } from '@tanstack/vue-query';
import { useTranslation } from 'i18next-vue';
import { computed, inject, ref, watch } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import BomMapDiagramPopupLabel from '../common/BomMapDiagramPopupLabel.vue';

const { t } = useTranslation(); // 다국어
const { planCycleData, interfaceConfigs, userAction } = inject('useBomMapInterface') as IBomMapIntefaceQuery;
const isbDataSource = ref<any>({});
const projectModule = useProjectInfoStore();

const isbInfoSchema1 = computed(() => {
  if (!isbDataSource.value?.bomMapIsbInfo) return null;
  return {
    [`${t('text-item_id')} / ${t('text-name')}`]: [
      [
        `${isbDataSource.value.bomMapIsbInfo.item_id} / ${isbDataSource.value.bomMapIsbInfo.item_name || isbDataSource.value.bomMapIsbInfo.item_id}`,
      ],
    ],
    [`${t('text-site_id')} / ${t('text-name')}`]: [
      [
        `${isbDataSource.value.bomMapIsbInfo.site_id} / ${isbDataSource.value.bomMapIsbInfo.site_name || isbDataSource.value.bomMapIsbInfo.site_id}`,
      ],
    ],
    [`${t('text-buffer_id')} / ${t('text-seq')}`]: [
      [`${isbDataSource.value.bomMapIsbInfo.buffer_id} / ${isbDataSource.value.bomMapIsbInfo.buffer_seq || '-'}`],
    ],
  };
});

const isbInfoSchema2 = computed(() => {
  if (!isbDataSource.value?.bomMapIsbInfo) return null;
  return {
    // [t('text-bom_map-wip_init_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.wip_qty, 1_000_000, '-')]],
    // [t('text-bom_map-wip_usage_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.peg_qty, 1_000_000, '-')]],
    // [t('text-bom_map-wip_remain_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.unpeg_qty, 1_000_000, '-')]]
    [t('text-bom_map-wip_init_qty')]: [
      [
        formatCompactNumber(isbDataSource.value.bomMapIsbInfo.wip_qty, {
          returnWhenInvalid: '-',
          fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
        }) || '-',
      ],
    ],
    [t('text-bom_map-wip_usage_qty')]: [
      [
        formatCompactNumber(isbDataSource.value.bomMapIsbInfo.peg_qty, {
          returnWhenInvalid: '-',
          fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
        }) || '-',
      ],
    ],
    [t('text-bom_map-wip_remain_qty')]: [
      [
        formatCompactNumber(isbDataSource.value.bomMapIsbInfo.unpeg_qty, {
          returnWhenInvalid: '-',
          fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
        }) || '-',
      ],
    ],
  };
});

const isbInfoSchema3 = computed(() => {
  if (!isbDataSource.value?.bomMapIsbInfo) return null;
  return {
    // [t('text-bom_map-intarget_target_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.input_target_qty, 1_000_000, '-')]],
    // [t('text-bom_map-intarget_plan_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.input_plan_qty, 1_000_000, '-')]],
    [t('text-bom_map-intarget_target_qty')]: [
      [
        isbDataSource.value.bomMapIsbInfo.input_target_qty !== null
          ? formatCompactNumber(isbDataSource.value.bomMapIsbInfo.input_target_qty, {
              returnWhenInvalid: '-',
              fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
            })
          : '-',
      ],
    ],
    [t('text-bom_map-intarget_plan_qty')]: [
      [
        isbDataSource.value.bomMapIsbInfo.input_plan_qty !== null
          ? formatCompactNumber(isbDataSource.value.bomMapIsbInfo.input_plan_qty, {
              returnWhenInvalid: '-',
              fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
            })
          : '-',
      ],
    ],
    [t('text-bom_map-intarget_option')]: [
      isbDataSource.value.bomMapIsbInfo.input_option_yn !== null
        ? [
            isbDataSource.value.bomMapIsbInfo.input_option_yn === 'Y'
              ? t('text-bom_map-intarget_y')
              : t('text-bom_map-intarget_n'),
            `${isbDataSource.value.bomMapIsbInfo.input_option_yn === 'Y' ? 'color: #357E63' : 'color: #DC5A5A'}`,
          ]
        : ['-'],
    ],
  };
});

const isbInfoSchema4 = computed(() => {
  if (!isbDataSource.value?.bomMapIsbInfo) return null;
  return {
    [t('text-bom_map-target_datetime')]: [
      isbDataSource.value.bomMapIsbInfo.extd_target_datetime
        ? [
            `${projectModule.convertToFormat('dateTime', isbDataSource.value.bomMapIsbInfo.target_datetime)} (${projectModule.convertToFormat('dateTime', isbDataSource.value.bomMapIsbInfo.extd_target_datetime)})`,
            'display: inline !important;',
          ]
        : [projectModule.convertToFormat('dateTime', isbDataSource.value.bomMapIsbInfo.target_datetime)],
    ],
    [t('text-bom_map-plan_datetime')]: [
      isbDataSource.value.bomMapIsbInfo.plan_gap_sec
        ? [
            [projectModule.convertToFormat('dateTime', isbDataSource.value.bomMapIsbInfo.plan_datetime)],
            [` (`],
            [
              Math.floor(isbDataSource.value.bomMapIsbInfo.plan_gap_sec / (60 * 60 * 24)) +
                dayjs
                  .duration(
                    Math.floor(Math.abs(isbDataSource.value.bomMapIsbInfo.plan_gap_sec) % (60 * 60 * 24)),
                    'seconds',
                  )
                  .format(' [Day] HH:mm'),
              `color: ${isbDataSource.value.bomMapIsbInfo.plan_gap_sec < 0 ? '#339A88' : '#FA9E23'};`,
            ],
            [`)`],
            'display: inline',
          ]
        : [
            isbDataSource.value.bomMapIsbInfo.plan_datetime
              ? projectModule.convertToFormat('dateTime', isbDataSource.value.bomMapIsbInfo.plan_datetime)
              : '-',
          ],
    ],
    // [t('text-bom_map-target_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.target_qty, 1_000_000, '-')]],
    // [t('text-bom_map-plan_qty')]: [[formatCompactNumber(isbDataSource.value.bomMapIsbInfo.plan_qty, 1_000_000, '-')]]
  };
});

const isbInfoSchema5 = computed(() => {
  if (!isbDataSource.value?.bomMapIsbInfo) return null;
  return {
    [t('text-bom_map-target_qty')]: [
      [
        formatCompactNumber(isbDataSource.value.bomMapIsbInfo.target_qty, {
          returnWhenInvalid: '-',
          fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
        }) || '-',
      ],
    ],
    [t('text-bom_map-plan_qty')]: [
      [
        formatCompactNumber(isbDataSource.value.bomMapIsbInfo.plan_qty, {
          returnWhenInvalid: '-',
          fixDecimalPoint: { onlyWhenDecimal: true, decimalPoint: 2 },
        }) || '-',
      ],
    ],
  };
});

const currentTab = ref('bomMapItemProp'); // 초기 탭 ID
const isbTabs = [
  { id: 'bomMapItemProp', text: t('text-global-item') },
  { id: 'bomMapSiteProp', text: t('text-global-site') },
  { id: 'bomMapBufferProp', text: t('text-global-buffer') },
  { id: 'bomMapIsbProp', text: t('text-global-isb') },
];

const getIsbInfo = useMutation({
  mutationFn: async (param: any) => await apiCall({ url: `RarBomMapViewNew/GetBomMapIsbInfo`, param, method: 'POST' }),

  onSuccess: (result) => {
    if (result && result.data) {
      isbDataSource.value = result.data;
    } else {
      isbDataSource.value = {};
    }
  },
  onError: () => {
    showMessage(t('msg-toast-get_error'), false);
  },
});

// ---------------------------------------------------------------------------------------------------------------------

const bomDataSource = ref<any>([]);
const currentBomTab = ref('bomMapBomProp'); // 초기 BOM 탭 ID
const bomTabs = [
  { id: 'bomMapBomProp', text: t('text-global-bom') },
  { id: 'bomMapRoutingProp', text: t('text-global-routing') },
  { id: 'bomMapOperProp', text: t('text-global-operation') },
];

const bomInfoSchema1 = computed(() => {
  const bomMasterInfo = bomDataSource.value?.bomMasterInfo;
  if (!bomMasterInfo?.[0]?.bom_id) return null;
  return {
    [t('text-bom_id')]: [[bomMasterInfo[0].bom_id]],
    [`${t('text-bom_map-bom_type')} / ${t('text-priority')}`]: [
      [`${bomMasterInfo[0].bom_type} / ${bomMasterInfo[0].bom_priority || '-'}`],
    ],
  };
});

const getBomInfo = useMutation({
  mutationFn: async (param: any) =>
    await apiCall({ url: `RarBomMapViewNew/GetBomMapRouteInfo`, param, method: 'POST' }),

  onSuccess: (result) => {
    if (result && result.data) {
      bomDataSource.value = {
        ...result.data,
        bomMapBomProp: [...result.data.bomMapBomProp],
        bomMapRouteInfos: withRowKey(result.data.bomMapRouteInfos),
      };
    } else {
      bomDataSource.value = {};
    }
  },
  onError: () => {
    showMessage(t('msg-toast-get_error'), false);
  },
});

// ---------------------------------------------------------------------------------------------------------------------

const generateColumn = (newData: any): { binding: string; header: string }[] => {
  const result: { binding: string; header: string }[] = [];
  Object.keys(newData[0]).forEach((key) => {
    if (key !== 'descending' && key !== 'ascending') {
      result.push({
        binding: key,
        header: t(`text-bom_map-${key}`),
      });
    }
  });
  return result;
};

const emptyCellAttributes = ({ value }: { value: unknown }) =>
  String(value ?? '').trim() === '' ? { class: 'bom-map-empty' } : undefined;

/**
 * 속성(prop) 탭 그리드 설정 — 데이터의 키로 컬럼을 만든다
 */
const buildPropCoreConfig = (rows: any[] | undefined): MozGridCoreProps => {
  if (!rows?.length) return { mode: 'flat', keyFields: [ROW_KEY], data: [], fields: [] };
  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: withRowKey(rows),
    fields: generateColumn(rows).map(({ binding, header }) => ({
      id: binding,
      header,
      dataType: 'string',
      flex: 1,
      minWidth: 60,
      cellAttributes: emptyCellAttributes,
    })),
  };
};

const isbPropCoreConfigs = computed<Record<string, MozGridCoreProps>>(() =>
  Object.fromEntries(isbTabs.map((tab) => [tab.id, buildPropCoreConfig(isbDataSource.value?.[tab.id])])),
);

const bomPropCoreConfigs = computed<Record<string, MozGridCoreProps>>(() =>
  Object.fromEntries(bomTabs.map((tab) => [tab.id, buildPropCoreConfig(bomDataSource.value?.[tab.id])])),
);

/**
 * BOM 속성 그리드 병합 — 0, 1번 컬럼만 병합한다.
 * 두 컬럼 값이 같으면 가로로 묶고, 위아래 행이 같은 모양이면 세로로 이어 붙인다.
 */
const onBomGridReady = (grid: PureSheet, _chrome: GridChrome) => {
  const mergeColumns = grid.columns.getVisibleColumns().slice(0, 2).map((column: any) => column.id);

  grid.setMergeConfig({
    type: 'custom',
    columns: mergeColumns,
    getMergedRange: ({ rowIndex, colIndex, columnsInOrder, getCellValue, totalRowCount }: any) => {
      if (colIndex !== 0 && colIndex !== 1) return null;

      const [firstCol, secondCol] = columnsInOrder;
      const text = (row: number, columnId: string) => String(getCellValue(row, columnId) ?? '').trim();
      const isRowMerged = (row: number) => !!secondCol && text(row, firstCol) === text(row, secondCol);

      const rowMerged = isRowMerged(rowIndex);
      const startCol = rowMerged ? 0 : colIndex;
      const endCol = rowMerged ? 1 : colIndex;
      const columnId = columnsInOrder[startCol];
      const value = text(rowIndex, columnId);
      const sameShape = (row: number) => isRowMerged(row) === rowMerged && text(row, columnId) === value;

      let startRow = rowIndex;
      let endRow = rowIndex;
      while (startRow > 0 && sameShape(startRow - 1)) startRow--;
      while (endRow < totalRowCount - 1 && sameShape(endRow + 1)) endRow++;

      if (startRow === endRow && startCol === endCol) return null;
      return { startRow, endRow, startCol, endCol };
    },
  });
};

/**
 * 생산계획 정보 (옛 MultiRow) — 한 데이터 행을 두 줄로 보여준다
 */
const ROUTE_ROW_HEIGHT = 28;
const routeGridHeight = computed(() =>
  Math.max(231, ROUTE_ROW_HEIGHT * 2 * ((bomDataSource.value?.bomMapRouteInfos?.length ?? 0) + 1) + 2),
);

const routeCellAttributes = ({ value, columnId }: { value: unknown; columnId: string }) => {
  const text = String(value ?? '').trim();
  const classes: string[] = [];
  if (columnId === 'oper_id') classes.push('bom-map-multirow-oper');
  if (text === 'TOTAL') classes.push('bom-map-multirow-total');
  if (text === '') classes.push('bom-map-empty-status');
  return classes.length ? { class: classes.join(' ') } : undefined;
};

const routeCoreConfig = computed<MozGridCoreProps>(() => {
  const numberField = { dataType: 'number', align: 'right' };
  return {
    mode: 'flat',
    keyFields: [ROW_KEY],
    data: bomDataSource.value?.bomMapRouteInfos ?? [],
    rowHeight: ROUTE_ROW_HEIGHT,
    tooltipMode: 'overflow',
    rowSelection: { mode: 'single' },
    rowTemplate: {
      rowCount: 2,
      layout: [
        [
          { id: 'oper_id', width: 69 },
          { id: 'target_qty', width: 66 },
          { id: 'total_tat', width: 80 },
          { id: 'all_res_list' },
        ],
        [
          { id: 'oper_type', width: 69 },
          { id: 'plan_qty', width: 66 },
          { id: 'elapse_sec', width: 80 },
          { id: 'res_list' },
        ],
      ],
    },
    fields: [
      { id: 'oper_id', header: t('text-bom_map-oper_id'), dataType: 'string', width: 69 },
      // TOTAL 행은 공정 유형 자리를 비운다 (옛 MultiRow 는 TOTAL 을 두 줄에 걸쳐 표시)
      {
        id: 'oper_type',
        header: t('text-bom_map-oper_type'),
        dataType: 'string',
        width: 69,
        mask: { type: 'function', formatter: (value: unknown) => (value === 'TOTAL' ? '' : String(value ?? '')) },
      },
      { id: 'target_qty', header: t('text-bom_map-target_qty'), width: 66, ...numberField },
      { id: 'plan_qty', header: t('text-bom_map-plan_qty'), width: 66, ...numberField },
      { id: 'total_tat', header: t('text-bom_map-total_tat'), width: 80, ...numberField },
      { id: 'elapse_sec', header: t('text-elapse_time'), width: 80, ...numberField },
      { id: 'all_res_list', header: t('text-available_res_id'), dataType: 'string', flex: 1 },
      { id: 'res_list', header: t('text-used_res_id'), dataType: 'string', flex: 1 },
    ].map((field) => ({ ...field, sortable: false, cellAttributes: routeCellAttributes })),
  };
});

const formatDuration = (sec: number) =>
  Math.floor(sec / (60 * 60 * 24)) +
  dayjs.duration(Math.floor(Math.abs(sec) % (60 * 60 * 24)), 'seconds').format(' [Day] HH:mm');

watch(
  () => userAction.value.click.current.node,
  () => {
    const node = userAction.value.click.current.node;
    if (node && node?.data?.type) {
      if (node.data.type === 'buffer') {
        getIsbInfo.mutate({
          projectID: planCycleData.value.projectID,
          planVer: planCycleData.value.planVer,
          demandID: planCycleData.value.demandID,
          itemID: node.data.itemID,
          siteID: node.data.siteID,
          bufferID: node.data.bufferID,
        });
      } else {
        getBomInfo.mutate({
          projectID: planCycleData.value.projectID,
          planVer: planCycleData.value.planVer,
          demandID: planCycleData.value.demandID,
          bomID: node.data.bomID,
        });
      }
    }
  },
);
</script>
<style lang="scss">
.extended-window-edge {
  & .bom-map-node-information-outer-wrapper {
    width: 100%;
  }
}

.bom-map-node-information-outer-wrapper {
  background-color: white;
  width: 350px;
  padding-bottom: 0.1px;

  & .tab {
    padding-left: 8px !important;
    padding-right: 8px !important;

    & .tab-label {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 4px;
    }
  }
}

.bom-map-window-badge {
  width: 17px;
  height: 16px;
  border-radius: 4px;
  font-weight: 300;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background-color: #4568e0;

  &[data-count='0'] {
    background-color: #8998b5;
  }
}

.bom-map-info-empty {
  &[data-border='true'] {
    border: 1px solid #bbc6d9;
  }

  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  color: #6a7184;
}

.bom-map-multirow-oper {
  border-bottom: none !important;
}

.bom-map-multirow-total {
  font-weight: 500;
}

.bom-map-bom-information-multirow {
  & .ps-row.ps-selected .bom-map-node-info-column-template-wrapper {
    color: #4568e0 !important;
  }

  & .ps-cell {
    overflow: hidden !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    word-break: break-all !important;

    &:hover {
      background-color: #cacde3 !important;
    }

    & div {
      width: 100%;
      overflow: hidden !important;
      white-space: nowrap !important;
      text-overflow: ellipsis !important;
      word-break: break-all !important;
    }
  }
}

.bom-map-window-tab-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;

  &.active,
  &:hover {
    color: #4568e0;
  }
}
</style>
