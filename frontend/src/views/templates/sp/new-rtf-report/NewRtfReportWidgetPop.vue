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
          <MozGrid
            style="flex: 1"
            class="rtf-summary-grid"
            :coreConfig="rtfGridCoreConfig"
            :use-tool-box="false"
            :use-extend-footer="false"
            :useContextMenu="false"
            :loading="false"
            :name="`${currentMenu.menuID}_pop_grid10`"
            @ready="onRtfGridReady"
          >
            <CellTemplate v-for="field in radioColumns" :key="field" :field="field" #default="{ rowData }">
              <label class="custom-radio">
                <input
                  type="radio"
                  :name="'apply-radio-' + String(rowData.category) + '-' + String(rowData.plan_type)"
                  :checked="!!rowData[field]"
                  @change="(event: Event) => onChangeApplyRadio(event, rowData, field)"
                />
                <span></span>
              </label>
            </CellTemplate>
          </MozGrid>
        </div>
      </template>
    </Tab>
  </Popup>
</template>

<script setup lang="ts">
import { useMenuStore, usePlanCycleStore } from './adapters/stores';
import { useProjectInfoStore } from './adapters/stores';
import { usePlanDashboardSubQuery } from './adapters/types';
import { CellTemplate, MozGrid } from '@vmscloud/moz-ui-grid-vue';
import type { GridChrome, MozGridCoreProps, PureSheet } from '@vmscloud/moz-ui-grid-vue';
import { Popup, Radio, Tab } from '@vmscloud/moz-ui-components-vue';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import { computed, inject, ref, shallowRef, toRaw, watch } from 'vue';
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

const rtfGrid = shallowRef<PureSheet>();

const rtfSummaryWidget = ref<any[]>(['cust', 'itemGroup', 'due']);
const planByProdDetailStandard = ref('BUFFER');

const menuModule = useMenuStore();
const { currentMenu } = storeToRefs(menuModule);

const rtfWidgetSettingTitle = computed(
  () => `${t(currentMenu.value.parentMenuName || '')} > ${t(currentMenu.value.menuName)} > ${t('text-menu-setting')}`,
);

const onRtfGridReady = (grid: PureSheet, _chrome: GridChrome) => {
  rtfGrid.value = grid;
  // 같은 구분(category) 셀을 세로로 병합한다
  grid.setMergeConfig({ type: 'content', columns: ['category'] });
};

const radioColumns = ['apply_early', 'apply_on_time', 'apply_late', 'apply_short', 'apply_excluded'];

const onChangeApplyRadio = (event: Event, rowData: any, field: string) => {
  const input = event.target as HTMLInputElement;
  if (!input.checked) return;

  rtfSummarySource.value.setting = rtfSummarySource.value.setting.map((item) => {
    if (item.category !== rowData.category || item.plan_type !== rowData.plan_type) return item;
    const next = { ...item };
    radioColumns.forEach((column) => {
      (next as any)[column] = column === field;
    });
    return next;
  });
};

const CATEGORY_LABEL_KEYS: Record<string, string> = {
  within_plan: 'text-demand_within_plan_period',
  after_plan: 'text-demand_beyond_plan_period',
};

const PLAN_TYPE_LABEL_KEYS: Record<string, string> = {
  early: 'text-global-upper-early',
  on_time: 'text-global-upper-on_time',
  late: 'text-global-upper-late',
  remain: 'text-global-upper-remain',
  short: 'text-global-upper-short',
};

const rtfGridCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: 'flat',
  keyFields: ['category', 'plan_type'],
  data: rtfSummarySource.value?.setting || [],
  rowHeader: { width: 73 },
  // 셀 선택 비활성화
  cellSelection: { mode: 'none' },
  fields: [
    {
      id: 'category',
      header: t('text-category'),
      dataType: 'string',
      width: 125,
      readonly: true,
      align: 'center',
      sortable: false,
      cellAttributes: { class: 'rtf-grid-category' },
      mask: {
        type: 'function',
        formatter: (value: unknown) =>
          CATEGORY_LABEL_KEYS[String(value)]
            ? t(CATEGORY_LABEL_KEYS[String(value)], { br: '\n', interpolation: { escapeValue: false } })
            : String(value ?? ''),
      },
    },
    {
      id: 'plan_type',
      header: t('text-plan_type'),
      dataType: 'string',
      width: 130,
      readonly: true,
      align: 'center',
      sortable: false,
      cellAttributes: { class: 'rtf-grid-border-right' },
      headerAttributes: { class: 'rtf-grid-border-right' },
      mask: {
        type: 'function',
        formatter: (value: unknown) =>
          PLAN_TYPE_LABEL_KEYS[String(value)] ? t(PLAN_TYPE_LABEL_KEYS[String(value)]) : String(value ?? ''),
      },
    },
    { id: 'apply_early', header: t('text-plan_dashboard-early'), dataType: 'boolean', width: 120, sortable: false },
    { id: 'apply_on_time', header: t('text-plan_dashboard-on_time'), dataType: 'boolean', width: 120, sortable: false },
    { id: 'apply_late', header: t('text-plan_dashboard-late'), dataType: 'boolean', width: 120, sortable: false },
    { id: 'apply_short', header: t('text-plan_dashboard-short'), dataType: 'boolean', width: 120, sortable: false },
    {
      id: 'apply_excluded',
      header: t('text-plan_dashboard-excluded'),
      dataType: 'boolean',
      width: 120,
      sortable: false,
    },
  ],
}));

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

.rtf-grid-category {
  white-space: pre-line;
}
</style>
