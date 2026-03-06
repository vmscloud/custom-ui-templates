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
            <ExtendFlexGrid
              :key="tab.id"
              v-if="tab.id in isbDataSource && isbDataSource[tab.id]?.length"
              class="bom-map-isb-info-grid"
              style="display: grid; max-width: 100%; overflow: hidden; height: 230px"
              :alternatingRowStep="0"
              :itemsSource="tab.id in isbDataSource ? isbDataSource[tab.id] : []"
              :isReadOnly="true"
              :use-tool-box="false"
              :use-extend-footer="false"
              :initialized="onIsbGridInitialized"
              :formatItem="formatItem"
              :autoGenerateColumns="false"
              :useContextMenu="false"
              :name="'bom-map-diagram-node-info-grid1'"
            >
              <WjFlexGridColumn
                v-if="isbDataSource && isbDataSource[tab.id]?.length"
                v-for="({ binding, header, width }, idx) in generateColumn(
                  tab.id in isbDataSource ? isbDataSource[tab.id] : [],
                )"
                :width="width"
                :binding="binding"
                :header="header"
              />
            </ExtendFlexGrid>
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
          v-if="bomDataSource?.bomMapRouteInfos?.itemCount"
          :style="{
            minHeight: '231px',
            maxWidth: '100%',
            display: 'grid',
            overflow: 'hidden',
            borderRight: '1px solid #c1c1d8',
            borderBottom: '1px solid #c1c1d8',
          }"
        >
          <WjMultiRow
            class="bom-map-bom-information-multirow"
            :style="{ width: 'calc(100% + 2px)', height: 'calc(100% + 2px)' }"
            :headersVisibility="'Column'"
            :formatItem="formatBomMapRouteItem"
            :itemsSource="bomDataSource?.bomMapRouteInfos"
            :allow-sorting="0"
            :autoRowHeights="true"
            :isReadOnly="true"
          >
            <!--          :layoutDefinition="bomGridLayout"-->

            <WjMultiRowCellGroup header="oper">
              <WjMultiRowCell
                :header="t('text-bom_map-oper_id')"
                :binding="'oper_id'"
                :width="69"
                :allowMerging="true"
              />
              <WjMultiRowCell :header="t('text-bom_map-oper_type')" :binding="'oper_type'" :width="69" />
            </WjMultiRowCellGroup>

            <WjMultiRowCellGroup header="qty">
              <WjMultiRowCell :header="t('text-bom_map-target_qty')" :binding="'target_qty'" :width="66" />
              <WjMultiRowCell :header="t('text-bom_map-plan_qty')" :binding="'plan_qty'" :width="66" />
            </WjMultiRowCellGroup>

            <WjMultiRowCellGroup header="time">
              <WjMultiRowCell :header="t('text-bom_map-total_tat')" :binding="'total_tat'" :width="80">
                <!--              <WjMultiRowCellTemplate :cellType="'ColumnHeader'" v-slot="cell">-->
                <!--                <div>헤더에 템플릿 지정이 가능함</div>-->
                <!--              </WjMultiRowCellTemplate>-->
                <WjMultiRowCellTemplate cellType="Cell" v-slot="cell">
                  <div
                    class="bom-map-node-info-column-template-wrapper"
                    v-tooltip="{
                      text:
                        Math.floor(cell.item.total_tat / (60 * 60 * 24)) +
                        dayjs
                          .duration(Math.floor(Math.abs(cell.item.total_tat) % (60 * 60 * 24)), 'seconds')
                          .format(' [Day] HH:mm'),

                      onlyEllipsis: true,
                    }"
                  >
                    {{
                      Math.floor(cell.item.total_tat / (60 * 60 * 24)) +
                      dayjs
                        .duration(Math.floor(Math.abs(cell.item.total_tat) % (60 * 60 * 24)), 'seconds')
                        .format(' [Day] HH:mm')
                    }}
                  </div>
                </WjMultiRowCellTemplate>
              </WjMultiRowCell>
              <WjMultiRowCell :header="t('text-elapse_time')" :binding="'elapse_sec'" :width="80">
                <WjMultiRowCellTemplate cellType="Cell" v-slot="cell">
                  <div
                    class="bom-map-node-info-column-template-wrapper"
                    v-tooltip="{
                      text:
                        Math.floor(cell.item.elapse_sec / (60 * 60 * 24)) +
                        dayjs
                          .duration(Math.floor(Math.abs(cell.item.elapse_sec) % (60 * 60 * 24)), 'seconds')
                          .format(' [Day] HH:mm'),
                      onlyEllipsis: true,
                    }"
                  >
                    {{
                      Math.floor(cell.item.elapse_sec / (60 * 60 * 24)) +
                      dayjs
                        .duration(Math.floor(Math.abs(cell.item.elapse_sec) % (60 * 60 * 24)), 'seconds')
                        .format(' [Day] HH:mm')
                    }}
                  </div>
                </WjMultiRowCellTemplate>
              </WjMultiRowCell>
            </WjMultiRowCellGroup>

            <WjMultiRowCellGroup header="res">
              <WjMultiRowCell :header="t('text-available_res_id')" :binding="'all_res_list'" width="*" />
              <WjMultiRowCell :header="t('text-used_res_id')" :binding="'res_list'" width="*" />
            </WjMultiRowCellGroup>
          </WjMultiRow>
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
            <ExtendFlexGrid
              v-if="tab.id in bomDataSource && bomDataSource[tab.id]?.length"
              :height="1200"
              :key="tab.id"
              class="bom-map-isb-info-grid"
              style="display: grid; max-width: 100%; overflow: hidden; height: 230px"
              :alternatingRowStep="0"
              :itemsSource="tab.id in bomDataSource ? bomDataSource[tab.id] : []"
              :isReadOnly="true"
              :use-tool-box="false"
              :use-extend-footer="false"
              :initialized="onBomGridInitialized"
              :formatItem="formatItem"
              :autoGenerateColumns="false"
              :useContextMenu="false"
              :name="'bom-map-diagram-node-info-grid2'"
            >
              <WjFlexGridColumn
                v-if="bomDataSource && bomDataSource[tab.id]?.length"
                v-for="({ binding, header, width }, idx) in generateColumn(
                  tab.id in bomDataSource ? bomDataSource[tab.id] : [],
                )"
                :width="width"
                :binding="binding"
                :header="header"
              />
            </ExtendFlexGrid>
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
import { CollectionView } from '@vmscloud/moz-wijmo-grid/wijmo';
import { AllowMerging, CellRange, CellType, FlexGrid, GridPanel, MergeManager } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import {
  WjMultiRow,
  WjMultiRowCell,
  WjMultiRowCellGroup,
  WjMultiRowCellTemplate,
} from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid.multirow';
import { Tab } from '@vmscloud/moz-ui-components';
import { ExtendFlexGrid } from '@vmscloud/moz-wijmo-grid';
import { ExtendGrid } from '@vmscloud/moz-wijmo-grid';
import { isDataCell } from '@vmscloud/moz-wijmo-grid/utils';
import { addTooltipEvent, formatCompactNumber, showMessage, dayjs } from '@moz-shared/utils';
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

const isbGrid = ref<FlexGrid | null>(null); // Wijmo grid
const isbExtendGrid = ref<ExtendGrid | null>(null); // Wijmo grid 확장 기능

const onIsbGridInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  isbGrid.value = flexGrid;
  isbExtendGrid.value = _extendGrid;
};

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
const bomGrid = ref<FlexGrid | null>(null); // Wijmo grid
const bomExtendGrid = ref<ExtendGrid | null>(null); // Wijmo grid 확장 기능

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
        bomMapRouteInfos: new CollectionView(result.data.bomMapRouteInfos),
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

const generateColumn = (newData: any): { binding: string; header: string; width: number | string }[] => {
  const result: { binding: string; header: string; width: number | string }[] = [];
  Object.keys(newData[0]).forEach((key) => {
    if (key !== 'descending' && key !== 'ascending') {
      result.push({
        binding: key,
        header: t(`text-bom_map-${key}`),
        width: '*',
      });
    }
  });
  return result;
};

class CustomMergeManager extends MergeManager {
  getMergedRange(panel: GridPanel, r: number, c: number): CellRange | null {
    if (panel.cellType !== CellType.Cell) return null;
    // 0, 1번 컬럼만 병합
    if (c !== 0 && c !== 1) return null;

    const rng = new CellRange(r, c);

    // 가로 병합 (0, 1번 컬럼만)
    for (let i = rng.col; i < Math.min(panel.columns.length - 1, 1); i++) {
      if (
        String(panel.getCellData(rng.row, i, true)).trim() !== String(panel.getCellData(rng.row, i + 1, true)).trim()
      ) {
        break;
      }
      rng.col2 = i + 1;
    }
    for (let i = rng.col; i > 0; i--) {
      if (
        String(panel.getCellData(rng.row, i, true)).trim() !== String(panel.getCellData(rng.row, i - 1, true)).trim()
      ) {
        break;
      }
      rng.col = i - 1;
    }

    // 세로 병합 (0, 1번 컬럼만)
    for (let i = rng.row; i < panel.rows.length - 1; i++) {
      if (
        String(panel.getCellData(i, rng.col, true)).trim() !== String(panel.getCellData(i + 1, rng.col, true)).trim()
      ) {
        break;
      }
      rng.row2 = i + 1;
    }
    for (let i = rng.row; i > 0; i--) {
      if (
        String(panel.getCellData(i, rng.col, true)).trim() !== String(panel.getCellData(i - 1, rng.col, true)).trim()
      ) {
        break;
      }
      rng.row = i - 1;
    }

    return rng;
  }
}

const onBomGridInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  bomGrid.value = flexGrid;
  bomExtendGrid.value = _extendGrid;

  bomGrid.value.allowMerging = AllowMerging.Cells;
  bomGrid.value.mergeManager = new CustomMergeManager();
  bomGrid.value.columns.forEach((col) => {
    col.allowMerging = true;
  });
};

const formatBomMapRouteItem = (s: FlexGrid, e: any) => {
  if (!isDataCell(s, e)) {
    if (e.col === 0 && e.row % 2 === 1) {
      e.cell.classList.add('bom-map-multirow-oper');
    }

    addTooltipEvent(e.cell, e.cell.innerText, true);
    return;
  }
  if (e.col === 0 && e.row % 2 === 0) {
    e.cell.classList.add('bom-map-multirow-oper');
  }

  if (e.cell.innerText.trim() === 'TOTAL') {
    if (e.row % 2 === 1) {
      e.cell.classList.add('bom-map-multirow-total');
    }
    if (e.row % 2 === 0) {
      e.cell.classList.add('bom-map-multirow-total-hide');
    }
  }

  if (!Number.isNaN(e.cell.innerText.trim())) {
    e.cell.classList.add('bom-map-multirow-number-cell');
  }

  if (e.cell.innerText.trim() === '') {
    e.cell.classList.add('bom-map-empty-status');
  }

  addTooltipEvent(e.cell, e.cell.innerText, true);
};

const formatItem = (s: FlexGrid, e: any) => {
  if (!isDataCell(s, e)) return;

  // 병합된 셀의 왼쪽 위 셀만 값 표시
  const range = s.mergeManager?.getMergedRange(s.cells, e.row, e.col);
  if (range && (e.row !== range.topRow || e.col !== range.leftCol)) {
    e.cell.innerHTML = '';
    return;
  }

  // node 정보 grid의 모든 type은 string으로 처리하도록 요청 받아 주석 처리 2025-11-03 danny
  // if (!Number.isNaN(Number(e.cell.innerText)) && !!e.cell.innerText) {
  //   e.cell.innerText = formatCompactNumber(Number(e.cell.innerText.trim()), { returnWhenInvalid: '-' });
  // }

  if (e.cell.innerText.trim() === '') {
    e.cell.classList.add('bom-map-empty');
  }
  const item = e.getRow()?.dataItem;
  if (!item) return;
  const col = e.getColumn().binding;
  const colIndex = e.col; // 현재 컬럼의 인덱스

  // more_info가 null이고 이전 컬럼이 prop_id인 경우
  if (col === 'more_info' && colIndex > 0) {
    const prevCol = s.columns[colIndex - 1].binding; // 이전 컬럼의 binding
    if (prevCol === 'prop_id' && item?.more_info === null) {
      // 병합 로직은 CustomMergeManager가 처리
    }
  }
};

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

.bom-map-multirow-number-cell {
  text-align: right;
}

.bom-map-multirow-total {
  height: 62px !important;
  top: 0px !important;
  padding-top: 22px !important;
}

.bom-map-multirow-total-hide {
  display: none !important;
}

.bom-map-bom-information-multirow {
  & .wj-state-selected .bom-map-node-info-column-template-wrapper {
    color: #4568e0 !important;
    //background-color: red;
  }

  & .wj-state-multi-selected .bom-map-node-info-column-template-wrapper {
    color: #4568e0 !important;
    //background-color: red;
  }

  &.wj-multirow .wj-cell.wj-record-end:not(.wj-header) {
    border-bottom-color: #bbc6d9 !important;
  }

  & .wj-cell.wj-alt {
    background-color: unset !important;
  }

  & .wj-cell.wj-header.wj-group-start.wj-group-end {
    display: block !important;
    line-height: 100%;
    padding-top: 8px;

    overflow: hidden !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    word-break: break-all !important;
  }

  & .wj-row {
    & .wj-cell {
      display: block !important;
      line-height: 100%;
      padding: 8px 8px 0px 8px;

      overflow: hidden !important;
      white-space: nowrap !important;
      text-overflow: ellipsis !important;
      word-break: break-all !important;

      &:hover {
        background-color: #cacde3 !important;
      }

      & div {
        width: 100%;
        height: 100%;
        overflow: hidden !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        word-break: break-all !important;
      }
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
