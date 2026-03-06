<template>
  <RtfReportWidgetPop v-model:visible="settingPopup" :initial-tab="'rtfReport'" />

  <Controller
    :show-filter-button="true"
    :actions="[
      {
        action: 'Search',
        click: () => {
          mainOnLoad();
        },
      },
    ]"
  >
    <template #beforeFilter>
      <div v-if="localState.isRePlan" class="plan-runing-info">
        <button @click="planingInfoPopup.show()">{{ localState.rePlanVer }}</button>
        <span>{{ t('rbpa-msg001') }}</span>
      </div>
      <div v-if="currentPlanCycleSource?.frozen_plan_ver" class="info-frozen-plan-wrapper">
        <IconNotice :style="{ width: 14, height: 14, marginTop: 2 }" />
        <div class="info-frozen-plan-text">
          <i18next :translation="t('text-info_frozen_plan_ver')">
            <template v-slot:planCycle>
              <span class="info-frozen-plan-ver" @click="onClickFrozenCycle">{{
                currentPlanCycleSource?.plan_cycle_id ? currentPlanCycleSource?.plan_cycle_id : ''
              }}</span>
            </template>
            <template v-slot:planVer>
              <span class="info-frozen-plan-ver" @click="onClickFrozenPlanVer">{{
                currentPlanCycleSource?.frozen_plan_ver ? currentPlanCycleSource?.frozen_plan_ver : ''
              }}</span>
            </template>
          </i18next>
        </div>
      </div>
    </template>
    <template #action>
      <Button
        v-if="!currentPlanCycleSource.frozen_plan_ver"
        :text="t('text-frozen')"
        @click="onFreezePopup"
        :disabled="frozenButtonDisabled"
        :loading="isFreezeFetching"
      >
        <template #icon
          ><IconCircleCheck :style="{ width: 14, height: 14 }" :color="frozenButtonDisabled ? '#8998b5' : '#ffffff'"
        /></template>
      </Button>
      <Button
        v-else
        :text="t('text-frozen_cancel')"
        class="confirm-cancel"
        @click="onConfirmCancelPopup"
        :disabled="!currentPlanCycleSource.is_frozen_plan || currentPlanCycleSource.frozen_plan_ver !== planVer"
        :loading="loadCancel"
      >
        <template #icon
          ><IconCircleX
            :color="
              !currentPlanCycleSource.is_frozen_plan || currentPlanCycleSource.frozen_plan_ver !== planVer
                ? '#8998b5'
                : '#4568e0'
            "
        /></template>
      </Button>
      <!-- 
      메뉴 설정 버튼 숨김
      롤백하라고 하면 다시 주석 풀기 
      -->
      <!-- <Button
        :text="t(`${t('text-set-menu-config')}`)"
        @click="
          () => {
            settingPopup = true;
          }
        "
      >
        <template #icon>
          <IconSetting :color="'#ffffff'" />
        </template>
      </Button> -->
    </template>
    <template #filter>
      <div class="controller-container">
        <div class="controller-search-container">
          <Radio
            v-model="summaryType"
            :label="t('text-summary_type')"
            :items-source="summarySource"
            display-expr="label"
            value-expr="value"
          />
          <MultiSelect
            v-if="summaryType === 'cust'"
            :placeholder="`${!custSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
            :label="t('text-upper-customer')"
            v-model="custParam"
            :header-format="'{count:n0} CUSTOMERS'"
            :use-filter="true"
            :use-select-all="true"
            :display-prop="'cust_label'"
            :items-source="custSource"
            :key-prop="'cust_id'"
            @close="
              () => {
                if (!custParam.length) {
                  custParam = custSource.map((item: any) => item.cust_id);
                }
              }
            "
          />
          <MultiSelect
            v-if="summaryType === 'itemGroup'"
            :placeholder="`${!itemGroupSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
            :label="t('text-upper-item_group')"
            v-model="itemGroup"
            :items-source="itemGroupSource"
            :header-format="'{count:n0} GROUPS'"
            :use-select-all="true"
            :use-filter="true"
            display-prop="item_group"
            key-prop="item_group"
            @close="
              () => {
                if (!itemGroup.length) {
                  itemGroup = itemGroupSource.map((item: any) => item.item_group);
                }
              }
            "
          />
          <MultiSelect
            v-if="summaryType === 'region'"
            :placeholder="`${!regionSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
            :label="t('text-upper-region')"
            v-model="region"
            :items-source="regionSource"
            :header-format="'{count:n0} REGIONS'"
            :use-select-all="true"
            :use-filter="true"
            display-prop="value"
            key-prop="value"
            @close="
              () => {
                if (!region.length) {
                  region = regionSource.map((item: any) => item.value);
                }
              }
            "
          />
          <MultiSelect
            v-if="summaryType === 'demandType'"
            :placeholder="`${!demandTypeSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
            :label="t('text-upper-demand_type')"
            v-model="demandType"
            :items-source="demandTypeSource"
            :header-format="'{count:n0} DEMAND TYPES'"
            :use-select-all="true"
            :use-filter="true"
            display-prop="value"
            key-prop="value"
            @close="
              () => {
                if (!demandType.length) {
                  demandType = demandTypeSource.map((item: any) => item.value);
                }
              }
            "
          />
          <Select
            :label="t('text-aggregate_type')"
            v-model="aggType"
            :items-source="aggTypeSource"
            keyProp="value"
            displayProp="label"
          />
          <Select
            :label="t('text-qty_uom')"
            v-model="uomType"
            :items-source="qtyUOMSource"
            keyProp="value"
            displayProp="displayValue"
          />
          <Radio
            v-model="prodStatus"
            :label="t('text-prod_status')"
            :items-source="prodStatusSource"
            display-expr="label"
            value-expr="value"
          />
        </div>
        <div class="widget-setting-button-wrapper">
          <!-- <Button
            :text="t(`${t('text-set-menu-config')}`)"
            @click="
              () => {
                settingPopup = true;
              }
            "
          >
            <template #icon>
              <IconSetting :color="'#ffffff'" />
            </template>
          </Button> -->
        </div>
      </div>
    </template>
  </Controller>
  <div class="moz-frame-for-outer-control">
    <!-- 확대 상태일 때 splitter 숨김 (v-show로 그리드 상태 유지) -->
    <SplitPane horizontal style="max-width: 100%" :class="{ 'hide-splitter': isZoomedDetail }">
      <Pane
        :size="`${isZoomedDetail ? 0 : 60}%`"
        :max-size="`${isZoomedDetail ? 0 : 70}%`"
        :min-size="`${isZoomedDetail ? 0 : 30}%`"
        v-show="!isZoomedDetail"
      >
        <!--  1280:720에서 그룹패널 보기 짤림을 대응 위해 50으로 적용 -->
        <SplitPane>
          <!--    560/1700 = 32.9411765      -->
          <Pane :size="`${mainLoadParams.summary === 'due' ? 36.8 : 39.1}%`" min-size="33%">
            <RarRtfReportSub1 ref="refSub1" :parentsSummaryWidth="`100%`" :parentsSummaryHeight="`100%`" />
          </Pane>
          <!--    200/1700 = 11.7647059      -->
          <Pane :size="`${mainLoadParams?.summary === 'due' ? 63.2 : 60.9}%`" min-size="12%">
            <RarRtfReportSub2 ref="refSub2" :parentsMainWidth="`100%`" :parentsMainHeight="`100%`" />
          </Pane>
        </SplitPane>
      </Pane>
      <Pane
        :size="`${isZoomedDetail ? 100 : 39}%`"
        :max-size="`${isZoomedDetail ? 100 : 70}%`"
        :min-size="`${isZoomedDetail ? 100 : 20}%`"
      >
        <RtfReportProdDetail />
        <!-- <RarRtfReportSub3 ref="refSub3" :parentsMainWidth="`100%`" :parentsMainHeight="`100%`" /> -->
      </Pane>
    </SplitPane>
  </div>

  <Popup
    :title="isClickedFrozenCycle ? t('text-plan_freeze_info_management') : t('text-plan_freeze')"
    v-model:visible="freezePopup"
    :width="500"
    :preset="isClickedFrozenCycle ? 'save' : 'confirm'"
    :onConfirm="onFreezePlan"
    class="frozen-plan-popup"
    :onCancel="
      () => {
        showValidation = false;
        freezePopup = false;
      }
    "
  >
    <div class="plan-freeze-container">
      <div class="plan-freeze-check-wrapper">
        <IconNotice :style="{ width: 20, height: 20 }" color="#4568e0" />
        <div class="plan-freeze-check-text">
          {{ isClickedFrozenCycle ? t('text-repeat_modify_desc') : t('text-repeat_freeze') }}
        </div>
      </div>
      <div class="plan-freeze-info-wrapper">
        <div>
          <span class="plan-freeze-info-key">{{ `${t('text-plan_cycle')}: ` }}</span>
          <span class="plan-freeze-info-value">{{
            isClickedFrozenCycle ? currentPlanCycleSource?.plan_cycle_id : planCycleID
          }}</span>
        </div>
        <div>
          <span class="plan-freeze-info-key">{{ `${t('text-frozen_plan_version')}: ` }}</span>
          <span class="plan-freeze-info-value">{{
            isClickedFrozenCycle ? currentPlanCycleSource?.frozen_plan_ver : planVer
          }}</span>
        </div>
        <div>
          <span class="plan-freeze-info-key">{{ `${t('text-frozen_plan_period')}: ` }}</span>
          <span class="plan-freeze-info-value">{{
            currentPlanCycleSource['frozen_period_desc'] ? currentPlanCycleSource['frozen_period_desc'] : ''
          }}</span>
        </div>
        <div>
          <span class="plan-freeze-info-key">{{ `${t('text-frozen_officer')}: ` }}</span>
          <span class="plan-freeze-info-value">{{ user?.name }}</span>
        </div>
      </div>
      <TextArea
        :label="t('text-description')"
        v-model="freezePlanDesc"
        type="textarea"
        :height="100"
        :is-required="true"
      />
    </div>
  </Popup>
  <Popup
    :title="t('text-warning')"
    :width="445"
    preset="confirm"
    :onConfirm="onCancelFrozen"
    v-model:visible="confirmCancelPopup"
    :onCancel="() => (confirmCancelPopup = false)"
  >
    <div class="confirm-cancel-popup-content-wrapper">
      <IconToastWarning />
      <div class="confirm-cancel-popup-text">{{ t('text-confirm_cancel_popup_info') }}</div>
    </div>
  </Popup>
</template>
<script setup lang="ts">
import {
  apiCall,
  autoTransaction,
  usePlanCycleStore,
  useBroadcastMessage,
  useLoadStore,
  useProjectInfoStore,
  useTextareaValidation,
} from './adapters/stores';
import { Controller } from '@vmscloud/moz-ui-components';
import { Button, MultiSelect, Pane, Popup, Radio, Select, SplitPane, TextArea } from '@vmscloud/moz-ui-components';
import { IconCircleCheck, IconCircleX, IconNotice, IconToastWarning } from '@moz-shared/icons';
import { showDialog, showMessage } from '@moz-shared/utils';
import { useMutation } from '@tanstack/vue-query';
import dayjs from 'dayjs';
import { useTranslation } from 'i18next-vue';
import { storeToRefs } from 'pinia';
import { computed, nextTick, provide, reactive, ref, watch, watchEffect } from 'vue';
import { useRtfReportQuery } from './NewRtfReport';
import RtfReportProdDetail from './NewRtfReportProdDetail.vue';
import RarRtfReportSub1 from './NewRtfReportSub1.vue';
import RarRtfReportSub2 from './NewRtfReportSub2.vue';
import RtfReportWidgetPop from './NewRtfReportWidgetPop.vue';

/**
 * DEFINE DEFAULT VARIABLE
 */

const planCycleStore = usePlanCycleStore();
const planingInfoPopup: any = ref(null);
const { updatePlanCycleStore } = usePlanCycleStore();
const textareaValidation = useTextareaValidation();
const { showValidation } = storeToRefs(textareaValidation as any);
const settingPopup = ref(false);

const {
  planCycleID,
  planVer,
  planStartDate,
  planPeriod,
  planCycleSource,
  fromDate,
  toDate,
  planStatus,
  currentPlanCycleSource,
} = storeToRefs(planCycleStore as any);
const { t } = useTranslation(); // 다국어
const load = useLoadStore();
const broadcastModule = useBroadcastMessage();

// Frozen Plan
const isClickedFrozenCycle = ref<boolean>(false);
const freezePlanDesc = ref<string>('');
const freezePopup = ref<boolean>(false);
const isClickHyperlink = ref<boolean>(false);
const confirmCancelPopup = ref(false);
const frozenPlanPeriodSource = ref<any>(null);
const selectedPlanVerInfo = ref<any>({});

const isFreezeFetching = computed(() => frozenPlanUpdateDesc.isPending.value || frozenPlanExec.isPending.value);

const projectInfoStore = useProjectInfoStore();
const user = computed(() => projectInfoStore.userInfo);

const useRtfReport = useRtfReportQuery(planVer, planCycleID, fromDate, toDate);
const {
  uomType,
  qtyUOMSource,
  summaryType,
  summarySource,

  aggType,
  aggTypeSource,
  isPageFetching,
  refSub1,
  refSub2,
  onLoad: mainOnLoad,
  custSource,
  custParam,
  itemGroup,
  itemGroupSource,
  mainLoadParams,
  isAggFetching,
  getWidgetValueIsPending,
  region,
  regionSource,
  demandTypeSource,
  demandType,
  prodStatus,
  prodStatusSource,
  isZoomedDetail,
} = useRtfReport;
provide('useRtfReport', useRtfReport);

const localState: {
  rowFlag: boolean;
  showDetail: boolean;
  isRePlan: boolean;
  frozenYN: boolean;
  frozenRange: string;
  rePlanVer: string;
  isClickSearch: boolean;
  planingInfo: {
    planVer: string;
    demandVer: string;
    planStartDate: string;
    planPeriod: string;
    scenarioID: string;
    description: string;
    runTime: Date;
    sender: string;
  } | null;
  frozenPlanVer: string;
} = reactive({
  rowFlag: true,
  showDetail: false,
  isRePlan: false,
  frozenYN: false,
  frozenRange: '',
  rePlanVer: '',
  planingInfo: null,
  frozenPlanVer: '',
  isClickSearch: false,
});

/**
 * INITIALIZE
 */
broadcastModule.$subscribe((mutation: any, state: any) => {
  if (user.value?.email !== state.sender) return;

  switch (state.message) {
    case 'START':
    case 'ING':
      localState.rePlanVer = state.planVer;
      localState.isRePlan = true;
      localState.planingInfo = {
        planVer: state.planVer,
        demandVer: state.demandVer,
        planStartDate: state.planStartDate,
        planPeriod: state.planPeriod,
        scenarioID: state.planScenario,
        description: state.description,
        runTime: state.runTime,
        sender: state.sender,
      };
      break;

    case 'DONE':
      localState.isRePlan = false;

      planingInfoPopup.value.hide();
      showDialog({
        type: 'success', // 'error' | 'warning' | 'success' | 'info'
        preset: 'check', // 'confirm' : (확인 / 취소) | 'check' : (확인)
        message: `${state.planVer} ${t('rbpa-msg002')}`,
      });

      planCycleStore.$patch({ planCycleID: state.planCycleID, planVer: state.planVer });

      break;
    default:
      break;
  }
});

const onLoad = async () => {
  await getFrozenPeriod.mutateAsync({ plan_ver: planVer.value });
  if (!isClickHyperlink.value) localState.isClickSearch = false;

  await getFrozenStatus.mutateAsync({
    planCycleID: planCycleID.value,
    planVer: planVer.value,
  });

  selectedPlanVerInfo.value = getSelectedPlanVer();
};

const onClickFrozenCycle = () => {
  isClickedFrozenCycle.value = true;
  freezePlanDesc.value = currentPlanCycleSource.value.frozen_desc;
  freezePopup.value = true;
};

const onClickFrozenPlanVer = async () => {
  isClickHyperlink.value = true;
  const frozenPlanCycleId = currentPlanCycleSource.value?.plan_cycle_id;
  const frozenPlanVer = currentPlanCycleSource.value?.frozen_plan_ver;

  // planCycleID와 planVer을 먼저 업데이트
  planCycleID.value = frozenPlanCycleId;
  planVer.value = frozenPlanVer;
  planStartDate.value = currentPlanCycleSource.value?.start_date;
  toDate.value = dayjs(planStartDate.value).add(planPeriod.value, 'day');
  localState.isClickSearch = true;

  const planStatusIndex = planCycleSource.value.findIndex(
    (item: any) => item.plan_cycle_id === frozenPlanCycleId && item.plan_ver === frozenPlanVer,
  );
  if (planStatusIndex !== -1) {
    planStatus.value = planCycleSource.value[planStatusIndex].plan_status;
  }

  await onLoad();
};

const frozenButtonDisabled = computed(
  () =>
    !currentPlanCycleSource.value.is_frozen_plan ||
    currentPlanCycleSource.value.plan_cycle_id !== planCycleID.value ||
    selectedPlanVerInfo.value.plan_status !== 'DONE',
);

const onFreezePopup = () => {
  freezePlanDesc.value = '';
  freezePopup.value = true;
};

const onConfirmCancelPopup = () => {
  confirmCancelPopup.value = true;
};

const onFreezePlan = async () => {
  if (isClickedFrozenCycle.value) {
    await frozenPlanUpdateDesc.mutateAsync({
      planCycleID: currentPlanCycleSource.value.plan_cycle_id,
      description: freezePlanDesc.value,
    });
    isClickedFrozenCycle.value = false;
  } else {
    await frozenPlanExec.mutateAsync({
      planCycleID: planCycleID.value,
      planVer: planVer.value,
      createUser: user.value?.email,
      description: freezePlanDesc.value,
    });
    if (planCycleID.value) {
      updatePlanCycleStore(planCycleID.value, ['frozen_plan_ver'], [planVer.value]);
    }
    onLoad();
  }

  freezePopup.value = false;
};

const loadCancel = ref<boolean>(false);

const onCancelFrozen = async () => {
  loadCancel.value = true;

  await frozenPlanRemove.mutateAsync({
    planCycleID: planCycleID.value,
    planVer: planVer.value,
    createUser: user.value?.email,
  });
  updatePlanCycleStore(planCycleID.value, ['frozen_plan_ver'], [null]);

  planCycleSource.value.forEach((item: any) => {
    if (item.plan_cycle_id === planCycleID.value && item.plan_ver === planVer.value) {
      item.plan_status = 'DONE';
    }
  });

  onLoad();
  confirmCancelPopup.value = false;
  loadCancel.value = false;
};

const getSelectedPlanVer = () => {
  const result = planCycleSource.value.filter((item: any) => item.plan_ver === planVer.value);

  return result[0] || [];
};

watchEffect(() => {
  load.set(isPageFetching.value);
});

const frozenPlanUpdateDesc = useMutation({
  mutationFn: (param: any) => autoTransaction({ url: 'PlmPlanExecute/Frozen', param, method: 'PUT' }),
  onSuccess: (result) => {
    if (!result || !result.data) {
      showMessage(t('msg-toast-save_error'), false);
    }
  },
  onError: () => {
    showMessage(t('msg-toast-save_error'), false);
  },
});

const frozenPlanExec = useMutation({
  mutationFn: (param: any) => autoTransaction({ url: 'PlmPlanExecute/FrozenIns', param, method: 'POST' }),
  onSuccess: (result) => {
    if (result && result.data) {
      showMessage(t('msg-toast-plan_ver_frozen'), true);
      getFrozenStatus.mutateAsync({
        planCycleID: planCycleID.value,
        planVer: planVer.value,
      });
    } else {
      showMessage(t('msg-toast-save_error'), false);
    }
  },
  onError: () => {
    showMessage(t('msg-toast-save_error'), false);
  },
});

// frozen Plan
const getFrozenStatus = useMutation({
  mutationFn: async (param: any) =>
    // 조회 목적으로 GET 유지해야 함
    await apiCall({ url: 'PlmPlanExecute/Frozen', param, method: 'GET' }),

  onSuccess: (result) => {
    if (result && result.data) {
      localState.frozenPlanVer = result.data[0]?.frozen_plan_ver ? result.data[0]?.frozen_plan_ver : '';
      localState.frozenYN = result.data[0]?.frozenYN;
      localState.frozenRange = result.data[0]?.frozenRange;
    } else {
      localState.frozenYN = false;
      localState.frozenRange = '';
    }
  },
  onError: () => {
    showMessage(t('msg-toast-get_error'), false);
    localState.frozenYN = false;
    localState.frozenRange = '';
  },
});

const frozenPlanRemove = useMutation({
  mutationFn: (param: any) => autoTransaction({ url: 'PlmPlanExecute/FrozenDel', param, method: 'POST' }),
  onSuccess: (result) => {
    if (result && result.data) {
      getFrozenStatus.mutateAsync({
        planCycleID: planCycleID.value,
        planVer: planVer.value,
      });
      showMessage(t('msg-toast-frozen_cancel'), true);
    } else {
      showMessage(t('msg-toast-save_error'), false);
    }
  },
  onError: () => {
    showMessage(t('msg-toast-save_error'), false);
  },
});

const getFrozenPeriod = useMutation({
  mutationFn: async (param: any) => {
    if (!param.plan_ver) return null;
    //

    return apiCall({ url: `PlmSysOperPlan/FrozenPeriod`, param, method: 'POST' });
  },

  onSuccess: (result) => {
    if (result && result.data) {
      frozenPlanPeriodSource.value = result.data;
    }
  },
  onError: () => {
    showMessage(t('msg-toast-get_error'), false);
    frozenPlanPeriodSource.value = null;
  },
  onSettled: () => {
    //
  },
});

const callWatch = watch(
  [planVer, planStartDate, fromDate, toDate, isAggFetching, getWidgetValueIsPending],
  () => {
    if (
      planVer.value &&
      fromDate.value &&
      toDate.value &&
      planStartDate.value &&
      !isAggFetching.value &&
      !getWidgetValueIsPending.value
    ) {
      nextTick(() => {
        mainOnLoad();
        onLoad();
        callWatch();
      });
    }
  },
  { immediate: true, flush: 'post' },
);
</script>
<style lang="scss" scoped>
:deep(.controller-container) {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between !important;

  .controller-search-container {
    display: flex;
    gap: 6px;
  }

  .widget-setting-button-wrapper {
    display: flex;
    justify-content: flex-end;
    align-items: center;
  }

  .controller-option-contatiner {
    align-self: center;
  }
}

.plan-freeze-container {
  display: flex;
  flex-direction: column;
  gap: 20px;

  .plan-freeze-check-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 500;

    .plan-freeze-check-text {
      padding-top: 1px;
    }
  }
}

.plan-freeze-info-wrapper {
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background-color: #f8f8fd;
  border-radius: 4px;
  border: solid 1px #e1e3f0;

  .plan-freeze-info-key {
    display: inline-block;
    width: 150px;
    font-size: 12px;
    color: #28364e;
    font-weight: 500;
  }

  .plan-freeze-info-value {
    font-size: 12px;
    color: #565f6e;
  }
}

// 확대 상태일 때 splitter 숨김
:deep(.hide-splitter) {
  .splitpanes__splitter {
    display: none !important;
  }
}

.confirm-cancel-popup-content-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;

  .confirm-cancel-popup-text {
    font-size: 14px;
    color: #28364e;
    font-weight: 400;
  }
}

.info-frozen-plan-wrapper {
  max-width: fit-content;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  border: 1px solid #bac6d4;
  border-radius: 50px;
  background-color: #f8f8fd;
  margin-right: 5px;
  padding: 0 10px;

  .info-frozen-plan-text {
    font-size: 13px;
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

.confirm-cancel-popup-content-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;

  .confirm-cancel-popup-text {
    font-size: 14px;
    color: #28364e;
    font-weight: 400;
  }
}

// 확정 취소 버튼 스타일 변경
:deep(.moz-button.moz-default-button.confirm-cancel) {
  background-color: #d6def8;
  border: solid 1px #d6def8;

  svg {
    fill: #4568e0;
  }

  span {
    font-weight: 300;
    color: #4568e0;
  }

  &:disabled {
    background-color: #e0e1ec;
    border-color: #e0e1ec;
  }

  &:disabled svg {
    fill: #a7b1bc;
  }

  &:disabled span {
    color: #a7b1bc;
  }

  &:hover:not(:disabled) {
    background-color: #4568e04d;
    border-color: #4568e033;
  }
}
</style>
