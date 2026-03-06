<template>
  <Popup
    class="dashboard-setting-detail-popup"
    :title="rtfWidgetSettingTitle"
    v-model:visible="visible"
    preset="save"
    :width="1037"
    :height="700"
    :on-before-confirm="onConfirmPopup"
    @open="onLoadPopup"
  >
    <Tab vertical v-model="settingPopupCurrentTab" :itemSource="itemSource" class="setting-tab">
      <template #rtfReport>
        <div class="tab-body-content rtf-report-tab">
          <!-- <div class="setting-popup-section">
            <div class="setting-popup-sub-title">{{ t('text-set-demand-group-init-value') }}</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">{{ t('desc-set-rtf-summary-group-init-value') }}</div>
              <div>
                <MultiSelect
                  v-model="rtfSummaryWidget"
                  :headerFormat="'{count:n0} ITEMS'"
                  :useSelectAll="true"
                  :useFilter="true"
                  :itemsSource="widgetSummarySource"
                  keyProp="value"
                  displayProp="label"
                  @close="
                    () => {
                      if (!rtfSummaryWidget?.length) {
                        rtfSummaryWidget = summarySource.map((item: any) => item.value);
                      }
                    }
                  "
                />
              </div>
            </div>
          </div> -->
          <!-- <div class="setting-popup-section">
            <div class="setting-popup-sub-title">{{ t('text-set-plan-aggr-standard') }}</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                {{ t('desc-set-demand-info-plan-qty-summary-standard') }}
              </div>
              <div>
                <Select
                  :key-prop="'value'"
                  :display-prop="'label'"
                  :items-source="planByProdDetailStandardSource"
                  v-model="planByProdDetailStandard"
                ></Select>
              </div>
            </div>
          </div> -->
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">{{ t('text-popup-rtf_aggregate_type_setting') }}</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">{{ t('desc-rtf_aggregate_type_setting') }}</div>
              <Radio
                :valueExpr="'value'"
                :display-expr="'label'"
                :items-source="[
                  { key: 'Lot', value: 'LOT', label: 'LOT' },
                  { key: 'Demand', value: 'DEMAND', label: 'DEMAND' },
                ]"
                v-model="rftStandard"
              ></Radio>
            </div>
          </div>
          <ExtendFlexGrid
            style="flex: 1"
            :alternatingRowStep="0"
            class="rtf-summary-grid"
            :itemsSource="rtfSummarySource?.setting || []"
            :use-tool-box="false"
            :use-extend-footer="false"
            :useContextMenu="false"
            :loading="false"
            :empty-state="{
              isLoading: false,
            }"
            :initialized="onRtfGridInitialized"
            :formatItem="rtfGridFormatItem"
            :name="`${currentMenu.menuID}_pop_grid10`"
          >
            <WjFlexGridColumn
              binding="category"
              :header="t('text-category')"
              :width="125"
              :isReadOnly="true"
              align="center"
            />
            <WjFlexGridColumn
              binding="plan_type"
              :header="t('text-plan_type')"
              :width="130"
              :isReadOnly="true"
              align="center"
            />
            <WjFlexGridColumn binding="apply_early" :header="t('text-plan_dashboard-early')" :width="120">
              <template #cell="{ item }">
                <input
                  type="radio"
                  :name="'apply-radio-' + String(item.category) + '-' + String(item.plan_type)"
                  :checked="item.apply_early"
                />
              </template>
            </WjFlexGridColumn>
            <WjFlexGridColumn binding="apply_on_time" :header="t('text-plan_dashboard-on_time')" :width="120">
              <template #cell="{ item }">
                <input
                  type="radio"
                  :name="'apply-radio-' + String(item.category) + '-' + String(item.plan_type)"
                  :checked="item.apply_on_time"
                />
              </template>
            </WjFlexGridColumn>
            <WjFlexGridColumn binding="apply_late" :header="t('text-plan_dashboard-late')" :width="120">
              <template #cell="{ item }">
                <input
                  type="radio"
                  :name="'apply-radio-' + String(item.category) + '-' + String(item.plan_type)"
                  :checked="item.apply_late"
                />
              </template>
            </WjFlexGridColumn>
            <WjFlexGridColumn binding="apply_short" :header="t('text-plan_dashboard-short')" :width="120">
              <template #cell="{ item }">
                <input
                  type="radio"
                  :name="'apply-radio-' + String(item.category) + '-' + String(item.plan_type)"
                  :checked="item.apply_short"
                />
              </template>
            </WjFlexGridColumn>
            <WjFlexGridColumn binding="apply_excluded" :header="t('text-plan_dashboard-excluded')" :width="120">
              <template #cell="{ item }">
                <input
                  type="radio"
                  :name="'apply-radio-' + String(item.category) + '-' + String(item.plan_type)"
                  :checked="item.apply_excluded"
                />
              </template>
            </WjFlexGridColumn>
          </ExtendFlexGrid>
        </div>
      </template>
    </Tab>
  </Popup>
</template>

<script setup lang="ts">
import { useMenuStore, usePlanCycleStore } from './adapters/stores';
import { useProjectInfoStore } from './adapters/stores';
import { usePlanDashboardSubQuery } from './adapters/types';
import { AllowMerging, CellType, FlexGrid, FormatItemEventArgs, SelectionMode } from '@vmscloud/moz-wijmo-grid/wijmo.grid';
import { WjFlexGridColumn } from '@vmscloud/moz-wijmo-grid/wijmo.vue2.grid';
import { Popup, Radio, Tab } from '@vmscloud/moz-ui-components';
import { ExtendFlexGrid } from '@vmscloud/moz-wijmo-grid';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import { computed, inject, ref, toRaw, watch } from 'vue';
import { IRtfReportQuery } from './NewRtfReport';

type PropsType = {
  initialTab: 'rtfReport' | 'stdSummary' | 'peggingReport' | 'stockInPlan' | 'resGroupSummary';
};

const planCycleStore = usePlanCycleStore();
const { planVer } = storeToRefs(planCycleStore as any);
const { invalidateAllCache } = usePlanDashboardSubQuery(planVer);
const props = defineProps<PropsType>();
const visible = defineModel('visible', { type: Boolean, default: false, required: true });
const projectInfoStore = useProjectInfoStore();
const userID = computed(() => projectInfoStore.userInfo?.id || '');
const { t } = useTranslation(); // 다국어

const rtfSummarySource = ref<{
  uomType: UomType;
  rtfStd: string;
  setting: ISetting[];
}>({
  uomType: 'DEFAULT',
  rtfStd: 'LOT',
  setting: [],
});
const rftStandard = ref('LOT');

const {
  // summarySource,
  saveRtfWidgetValue,
  // widgetSummarySource,
  currentWidgetSetting,
  // planByProdDetailStandardSource,
  getPlanByProdDetailQuery,
  // getRtfSummaryQuery,
  originWidgetSetting,
} = inject('useRtfReport') as IRtfReportQuery;

type UomType = 'DEFAULT' | 'CONVERSION';

interface ISetting {
  category: string;
  plan_type: string;
  apply_early: boolean;
  apply_on_time: boolean;
  apply_late: boolean;
  apply_short: boolean;
  apply_excluded: boolean;
}

const rtfGrid = ref<FlexGrid>();

const rtfSummaryWidget = ref<any[]>(['cust', 'itemGroup', 'due']);
const planByProdDetailStandard = ref('BUFFER');

const menuModule = useMenuStore();
const { currentMenu } = storeToRefs(menuModule);

const rtfWidgetSettingTitle = computed(
  () => `${t(currentMenu.value.parentMenuName || '')} > ${t(currentMenu.value.menuName)} > ${t('text-menu-setting')}`,
);

const onRtfGridInitialized = (flexGrid: FlexGrid) => {
  flexGrid.rowHeaders.columns.maxSize = 73;
  flexGrid.rowHeaders.columns.minSize = 73;

  // 셀 선택 비활성화
  flexGrid.selectionMode = SelectionMode.None;

  rtfGrid.value = flexGrid;

  if (flexGrid) {
    flexGrid.allowMerging = AllowMerging.Cells;
    flexGrid.columns[0].allowMerging = true;
  }
};

const radioColumns = ['apply_early', 'apply_on_time', 'apply_late', 'apply_short', 'apply_excluded'];

const rtfGridFormatItem = (s: FlexGrid, e: FormatItemEventArgs) => {
  if (e.panel.cellType === CellType.Cell) {
    const col = s.columns[e.col];
    if (radioColumns.includes(col?.binding || '')) {
      const row = s.rows[e.row].dataItem;
      const checked = row[col?.binding || ''];
      e.cell.innerHTML = `
        <label class="custom-radio">
          <input type="radio" name="apply-radio-${String(row.category)}-${String(row.plan_type)}" ${checked ? 'checked' : ''} />
          <span></span>
        </label>
      `;
      e.cell.querySelector('input')?.addEventListener('change', (event) => {
        const input = event.target as HTMLInputElement;
        if (input.checked) {
          radioColumns.forEach((field) => {
            row[field] = field === col?.binding;
          });
          s.collectionView.refresh();
        }
      });
    }

    if (e.col === 0) {
      if (e.cell.innerText === 'within_plan') {
        e.cell.innerText = t('text-demand_within_plan_period', { br: '\n', interpolation: { escapeValue: false } });
      }

      if (e.cell.innerText === 'after_plan') {
        e.cell.innerText = t('text-demand_beyond_plan_period', { br: '\n', interpolation: { escapeValue: false } });
      }
    }

    if (e.col === 1) {
      if (e.cell.innerText === 'early') {
        e.cell.innerText = t('text-global-upper-early');
      }

      if (e.cell.innerText === 'on_time') {
        e.cell.innerText = t('text-global-upper-on_time');
      }

      if (e.cell.innerText === 'late') {
        e.cell.innerText = t('text-global-upper-late');
      }

      if (e.cell.innerText === 'remain') {
        e.cell.innerText = t('text-global-upper-remain');
      }

      if (e.cell.innerText === 'short') {
        e.cell.innerText = t('text-global-upper-short');
      }
    }
  }

  if (s.columns[e.col]?.binding === 'plan_type') {
    e.cell.classList.add('rtf-grid-border-right');
  }
};

// const getRtfSummaryQuery = useMutation({
//   mutationFn: () => apiCall(GET_RTF_SUMMARY, { userID: userID.value, planVer: planVer.value }, 'POST'),
//   onSuccess: (result) => {
//     if (result && result.data) {
//     } else showMessage(t('msg-toast-save_error'), false);
//   },
//   onError: () => {
//     showMessage(t('msg-toast-save_error'), false);
//   },
// });

// watch(visible, () => {
//   if (visible.value) {
//     getRtfSummaryQuery.mutate();
//   }
// });

// -----------------------------------------------------------------------

const itemSource = [{ id: 'rtfReport' as const, text: t(`${t(currentMenu.value.menuName)}`) }] satisfies {
  id: PropsType['initialTab'];
  text: string;
}[];

const settingPopupCurrentTab = ref(props.initialTab);

/**
 * modal 켰을 때 '설비 가동 현황', '구간별 재고 현황'으로 고정
 */
watch(visible, (newVisible) => {
  if (newVisible) settingPopupCurrentTab.value = props.initialTab;
});

// endregion

const onConfirmPopup = async () => {
  const param = [
    {
      widget_id: 'rtfSummaryPopup',
      menu_id: '/pa/PlanDashboard',
      user_id: userID.value,
      widget_value: JSON.stringify({
        ...currentWidgetSetting.value,
        rtfStd: rftStandard.value,
        setting: rtfSummarySource.value?.setting,
        summaryTypes: {
          due: !!rtfSummaryWidget.value.includes('due'),
          cust: !!rtfSummaryWidget.value.includes('cust'),
          itemGroup: !!rtfSummaryWidget.value.includes('itemGroup'),
          region: !!rtfSummaryWidget.value.includes('region'),
          demandType: !!rtfSummaryWidget.value.includes('demandType'),
        },
        detailType: planByProdDetailStandard.value,
      }),
    },
  ];

  await saveRtfWidgetValue.mutateAsync(param);

  await getPlanByProdDetailQuery.refetch();

  await invalidateAllCache();

  return true;
};

const onLoadPopup = async () => {
  const result = originWidgetSetting.value;

  if (result && result.summaryTypes) {
    // period를 due로 마이그레이션: 기존 period 설정을 due로 변환
    const summaryTypeKeys = Object.keys(result.summaryTypes).filter(
      (key) => result.summaryTypes![key as keyof typeof result.summaryTypes],
    );

    // period가 있으면 due로 변환하고 period는 제거
    rtfSummaryWidget.value = summaryTypeKeys.map((key) => (key === 'period' ? 'due' : key));

    // 중복 제거 (period와 due가 모두 true였던 경우 대비)
    rtfSummaryWidget.value = Array.from(new Set(rtfSummaryWidget.value));

    if (result?.detailType) {
      planByProdDetailStandard.value = result.detailType;
    }

    if (result?.rtfStd) {
      rftStandard.value = result.rtfStd;
    }

    if (result?.setting?.length) {
      rtfSummarySource.value.setting = toRaw(result.setting.map((item: any) => ({ ...item })));
    }
  }
};
</script>
<style lang="scss">
.dashboard-setting-detail-popup {
  .moz-popup-body {
    padding: 0 !important;
  }

  .setting-tab {
    height: 100%;
    overflow-x: hidden;
    overflow-y: auto;

    .moz-tab-body {
      overflow: hidden;
    }

    .moz-tabs {
      min-width: 140px !important;
      .tab-label {
        // 완제품 생산 현황 기준으로 right-padding 12px을 위해 아래 설정 추가
        // 영어는 생각하는 것을 잠시 보류
        text-overflow: clip !important;
      }
    }

    .currentTab {
      padding: 24px 16px;

      .tab-body-content {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        gap: 20px;

        &.rtf-report-tab {
          gap: 0;
        }

        .std-summary-grid {
          .sudo-read-only.wj-state-multi-selected,
          .sudo-read-only.wj-state-active {
            // hover로 row 전체 색변경은 유지하지만 체크박스로 cell의 글자색 변경은 방지
            color: #28364e;
            background-color: #e2e7fa !important;
            span.wj-cell-text {
              color: #28364e;
            }
          }
        }
      }

      .setting-popup-sub-title {
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 0;
        line-height: normal;
        height: 20px;
      }

      .setting-popup-sub-desc {
        font-size: 12px;
        font-weight: 400;
        color: rgba(67, 76, 96, 1);
        line-height: normal;

        &.rtf-summary-grid-desc {
          margin-bottom: 2px;
        }
      }

      .setting-popup-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 10px;

        .setting-popup-sub-section {
          border: 1px solid rgba(186, 198, 212, 1);
          background-color: rgba(248, 248, 253, 1);
          border-radius: 6px;
          padding: 16px;

          display: flex;
          align-items: center;
          justify-content: space-between;
        }
      }
    }
  }

  // 특정 plan cycle에 확정 계획이 있는 경우 안내 TEXT
  .info-frozen-plan-wrapper {
    // max-width: fit-content;
    height: 28px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 6px;
    border: 1px solid #bac6d4;
    border-radius: 50px;
    background-color: #f8f8fd;
    margin: 12px 5px 0 0;
    padding: 0 10px;

    .info-frozen-plan-text {
      font-size: 12px;
      color: #434c60;
      word-break: break-all;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 1;
      -webkit-box-orient: vertical;
    }

    .info-frozen-plan-ver {
      color: #4568e0;
      cursor: pointer;
      text-decoration: underline;
    }

    @media (max-width: 1350px) {
      .info-frozen-plan-wrapper {
      }

      .info-frozen-plan-text {
        width: 100%;
      }
    }
  }
}

.custom-radio {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  input[type='radio'] {
    display: none;
  }
  span {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 1px solid #bac6d4;
    border-radius: 50%;
    background: #fff;
    position: relative;
    transition: border-color 0.2s;
  }
  input[type='radio']:checked + span {
    background: #4568e0;
    border: none;
  }
  input[type='radio']:checked + span::after {
    content: '';
    display: block;
    width: 6px;
    height: 6px;
    background: #fff;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
}

.rtf-grid-border-right {
  border-right: 1px solid #6a7184 !important;
}
</style>
