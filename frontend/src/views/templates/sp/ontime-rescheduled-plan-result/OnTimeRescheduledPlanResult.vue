<template>
  <div class="ontime-rescheduled-plan-result-page">
    <!-- Controller -->
    <Controller
      :navigations="['생산 계획', 'Replan RTF 납기준수율']"
      showFilterButton
      :actions="[
        {
          action: 'Search',
          click: handleSearch,
          disabled: loading || !planVer,
        },
      ]"
    >
      <template #beforeFilter>
        <!-- Frozen Plan Info Pill -->
        <div
          v-if="frozenStatus?.frozen_plan_ver"
          class="info-frozen-plan-wrapper"
        >
          <span class="info-frozen-plan-text">
            확정 계획:
            <span class="info-frozen-plan-ver" @click="onClickFrozenPlanVer">
              {{ frozenStatus.frozen_plan_ver }}
            </span>
            ({{ frozenStatus.plan_cycle_id }})
          </span>
        </div>
      </template>

      <template #action>
        <Button
          v-if="!frozenStatus?.frozen_plan_ver"
          text="확정"
          @click="onFreezePopup"
          :disabled="freezeButtonDisabled"
          :loading="freezeLoading"
        />
        <Button
          v-else
          text="확정 취소"
          class="confirm-cancel"
          @click="onConfirmCancelPopup"
          :disabled="frozenStatus?.frozen_plan_ver !== planVer"
          :loading="cancelLoading"
        />
      </template>

      <template #filter>
        <div class="controller-container">
          <div class="controller-search-container">
            <Radio
              label="지역"
              valueExpr="value"
              display-expr="label"
              :items-source="regionSource"
              v-model="region"
            />
            <Radio
              label="상세"
              valueExpr="value"
              display-expr="label"
              :items-source="hkDetailSource"
              v-model="hkDetail"
              :disabled="region !== 'HK'"
            />
            <Radio
              v-model="summaryType"
              label="요약 유형"
              :items-source="summaryOptions"
              display-expr="label"
              value-expr="value"
              variant="boxed"
            />
            <MultiSelect
              v-if="summaryType === 'itemGroup'"
              :placeholder="!itemGroupSource.length ? '데이터 없음' : ''"
              label="제품 그룹"
              v-model="selectedItemGroups"
              :items-source="itemGroupSource"
              key-prop="item_group"
              display-prop="item_group"
              header-format="{count:n0} GROUPS"
              :use-filter="true"
              :use-select-all="true"
              @close="onItemGroupsClose"
            />
            <MultiSelect
              v-if="summaryType === 'prodType'"
              :placeholder="!prodTypeSource.length ? '데이터 없음' : ''"
              label="생산 유형"
              v-model="selectedProdTypes"
              :items-source="prodTypeSource"
              key-prop="value"
              display-prop="value"
              header-format="{count:n0} PROD TYPES"
              :use-filter="true"
              :use-select-all="true"
              @close="onProdTypesClose"
            />
            <Select
              label="집계 유형"
              v-model="aggType"
              :items-source="aggTypeOptions"
              key-prop="value"
              display-prop="label"
            />
            <Select
              label="수량 단위"
              v-model="uomType"
              :items-source="uomOptions"
              key-prop="value"
              display-prop="label"
            />
            <Radio
              v-model="prodStatus"
              label="생산 상태"
              :items-source="prodStatusOptions"
              display-expr="label"
              value-expr="value"
              variant="boxed"
            />
          </div>
        </div>
      </template>
    </Controller>

    <!-- Main Content -->
    <section class="content-section">
      <!-- Empty State -->
      <div v-if="summaryData.length === 0 && !loading" class="empty-state">
        <EmptyState :is-read-only="true" />
      </div>

      <!-- SplitPane Layout -->
      <SplitPane
        v-else
        horizontal
        style="max-width: 100%"
        :class="{ 'hide-splitter': isZoomedDetail }"
      >
        <!-- Top: Summary + Detail -->
        <Pane
          :size="`${isZoomedDetail ? 0 : 60}%`"
          :max-size="`${isZoomedDetail ? 0 : 70}%`"
          :min-size="`${isZoomedDetail ? 0 : 30}%`"
          v-show="!isZoomedDetail"
        >
          <SplitPane>
            <Pane size="39%" min-size="30%">
              <OnTimeRescheduledPlanResultSub1
                :data="summaryData"
                :summary-type="committedSummaryType"
                :agg-type="committedAggType"
                :loading="loading"
                @row-selected="handleSummaryRowSelect"
              />
            </Pane>
            <Pane size="61%" min-size="20%">
              <OnTimeRescheduledPlanResultSub2
                :data="detailData"
                :loading="detailLoading"
                :plan-ver="planVer"
                :uom-type="committedUomType"
                :short-data="shortData"
                @demand-selected="handleDemandSelect"
                @load-short="(id: string) => loadShort(planVer, id)"
              />
            </Pane>
          </SplitPane>
        </Pane>

        <!-- Bottom: Production Detail -->
        <Pane
          :size="`${isZoomedDetail ? 100 : 40}%`"
          :max-size="`${isZoomedDetail ? 100 : 70}%`"
          :min-size="`${isZoomedDetail ? 100 : 20}%`"
        >
          <OnTimeRescheduledPlanResultDetail
            :data="prodDetailData"
            :demand-summary-data="demandSummaryData"
            :demand-info-data="demandInfoData"
            :peg-info-data="pegInfoData"
            :bom-map-data="bomMapData"
            :plan-ver="planVer"
            :demand-id="selectedDemandID"
            :is-zoomed="isZoomedDetail"
            :loading="prodDetailLoading"
            @toggle-zoom="isZoomedDetail = !isZoomedDetail"
            @load-demand-info="(id: string) => loadDemandInfo(planVer, id)"
            @load-peg-info="(id: string) => loadPegInfo(planVer, id)"
            @load-bom-map="(id: string) => loadBomMap(planVer, id)"
          />
        </Pane>
      </SplitPane>
    </section>

    <!-- Freeze Popup -->
    <Popup
      :title="isEditingFrozenDesc ? '계획 확정 정보 관리' : '계획 확정'"
      v-model:visible="freezePopup"
      :width="500"
      :preset="isEditingFrozenDesc ? 'save' : 'confirm'"
      :onConfirm="onFreezePlan"
      :onCancel="
        () => {
          freezePopup = false;
        }
      "
    >
      <div class="plan-freeze-container">
        <div class="plan-freeze-check-wrapper">
          <span class="plan-freeze-check-text">
            {{ isEditingFrozenDesc ? '확정 설명을 수정합니다.' : '선택한 계획을 확정합니다.' }}
          </span>
        </div>
        <div class="plan-freeze-info-wrapper">
          <div>
            <span class="plan-freeze-info-key">Plan Cycle: </span>
            <span class="plan-freeze-info-value">{{ planCycleID }}</span>
          </div>
          <div>
            <span class="plan-freeze-info-key">확정 버전: </span>
            <span class="plan-freeze-info-value">{{ planVer }}</span>
          </div>
          <div>
            <span class="plan-freeze-info-key">확정 기간: </span>
            <span class="plan-freeze-info-value">{{ frozenStatus?.frozen_period_desc || '' }}</span>
          </div>
          <div>
            <span class="plan-freeze-info-key">담당자: </span>
            <span class="plan-freeze-info-value">{{ userInfo?.name }}</span>
          </div>
        </div>
        <TextArea
          label="설명"
          v-model="freezePlanDesc"
          type="textarea"
          :height="100"
          :is-required="true"
        />
      </div>
    </Popup>

    <!-- Cancel Freeze Popup -->
    <Popup
      title="경고"
      :width="445"
      preset="confirm"
      :onConfirm="onCancelFrozen"
      v-model:visible="confirmCancelPopup"
      :onCancel="() => (confirmCancelPopup = false)"
    >
      <div class="confirm-cancel-popup-content-wrapper">
        <span>확정을 취소하시겠습니까?</span>
      </div>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import {
  Controller,
  Select,
  MultiSelect,
  Radio,
  Button,
  Popup,
  EmptyState,
  TextArea,
} from "@vmscloud/moz-ui-components";
import { SplitPane, Pane } from "@vmscloud/moz-ui-components";
import {
  useHostPlanCycle,
  useHostUser,
  useHostProjectInfo,
} from "@/composables/useHostStores";
import { useOnTimeRescheduledPlanResult } from "./onTimeRescheduledPlanResult";
import OnTimeRescheduledPlanResultSub1 from "./OnTimeRescheduledPlanResultSub1.vue";
import OnTimeRescheduledPlanResultSub2 from "./OnTimeRescheduledPlanResultSub2.vue";
import OnTimeRescheduledPlanResultDetail from "./OnTimeRescheduledPlanResultDetail.vue";
import type { ReplanRtfSummary } from "./onTimeRescheduledPlanResult";

// === Host Data ===
const { planVer } = useHostPlanCycle();
const { userInfo } = useHostUser();
useHostProjectInfo();
const planCycleID = computed(() => ""); // Will be resolved from host if available

// === Composable ===
const {
  summaryType,
  aggType,
  uomType,
  prodStatus,
  region,
  hkDetail,
  selectedCustomers,
  selectedItemGroups,
  selectedProdTypes,
  committedSummaryType,
  committedAggType,
  committedUomType,
  customerSource,
  itemGroupSource,
  prodTypeSource,
  summaryData,
  detailData,
  prodDetailData,
  shortData,
  demandSummaryData,
  demandInfoData,
  pegInfoData,
  bomMapData,
  selectedDemandID,
  frozenStatus,
  loading,
  detailLoading,
  prodDetailLoading,
  isZoomedDetail,
  commitFilters,
  loadFilters,
  loadSummary,
  loadDetail,
  loadProdDetail,
  loadShort,
  loadDemandSummary,
  loadDemandInfo,
  loadPegInfo,
  loadBomMap,
  loadFrozenStatus: _loadFrozenStatus,
  executeFreezeAction,
  cancelFreezeAction,
  updateFrozenDescription,
  reset,
} = useOnTimeRescheduledPlanResult();

// === Static Options ===

const regionSource = [
  { value: "default", label: "전체" },
  { value: "대구", label: "대구" },
  { value: "HK", label: "HK" },
];

const hkDetailSource = [
  { value: "HK", label: "전체" },
  { value: "HK 완제", label: "HK 완제" },
  { value: "HK 반제", label: "HK 반제" },
];

const summaryOptions = [
  { value: "itemGroup", label: "제품 그룹" },
  { value: "prodType", label: "생산 유형" },
];

const aggTypeOptions = [
  { value: "WEEK", label: "WEEK" },
  { value: "MONTH", label: "MONTH" },
];

const uomOptions = [
  { value: "DEFAULT", label: "DEFAULT" },
  { value: "CONVERSION", label: "CONVERSION" },
];

const prodStatusOptions = [
  { value: "default", label: "전체" },
  { value: "on_time", label: "On-Time" },
  { value: "late", label: "Late" },
  { value: "short", label: "Short" },
  { value: "early", label: "Early" },
];

// === Freeze Local State ===
const freezePopup = ref(false);
const confirmCancelPopup = ref(false);
const freezePlanDesc = ref("");
const isEditingFrozenDesc = ref(false);
const freezeLoading = ref(false);
const cancelLoading = ref(false);

const freezeButtonDisabled = computed(() => {
  // Disable if no frozen plan capability or plan not DONE
  return !planVer.value;
});

// === Event Handlers ===

async function handleSearch() {
  if (!planVer.value) return;
  commitFilters();
  reset();
  await loadSummary(planVer.value);
}

function handleSummaryRowSelect(item: ReplanRtfSummary) {
  if (!planVer.value) return;
  loadDetail(planVer.value, item);
}

function handleDemandSelect(demandID: string) {
  if (!planVer.value || !demandID) return;
  selectedDemandID.value = demandID;
  loadProdDetail(planVer.value, demandID);
  loadDemandSummary(planVer.value, [demandID]);
}

// MultiSelect close handlers
function onCustomersClose() {
  if (selectedCustomers.value.length === 0) {
    selectedCustomers.value = customerSource.value.map((c: any) => c.cust_id);
  }
}
function onItemGroupsClose() {
  if (selectedItemGroups.value.length === 0) {
    selectedItemGroups.value = itemGroupSource.value.map((g: any) => g.item_group);
  }
}
function onProdTypesClose() {
  if (selectedProdTypes.value.length === 0) {
    selectedProdTypes.value = prodTypeSource.value.map((p: any) => p.value);
  }
}

// Region change handler
watch(region, (newVal) => {
  if (newVal !== "HK") {
    hkDetail.value = "HK";
  }
});

// Freeze handlers
function onFreezePopup() {
  isEditingFrozenDesc.value = false;
  freezePlanDesc.value = "";
  freezePopup.value = true;
}

function onClickFrozenPlanVer() {
  isEditingFrozenDesc.value = true;
  freezePlanDesc.value = frozenStatus.value?.frozen_desc || "";
  freezePopup.value = true;
}

function onConfirmCancelPopup() {
  confirmCancelPopup.value = true;
}

async function onFreezePlan() {
  if (!planVer.value) return;

  if (isEditingFrozenDesc.value) {
    await updateFrozenDescription(
      frozenStatus.value?.plan_cycle_id || planCycleID.value,
      freezePlanDesc.value,
    );
  } else {
    freezeLoading.value = true;
    await executeFreezeAction(
      planCycleID.value,
      planVer.value,
      userInfo.value?.email || "",
      freezePlanDesc.value,
    );
    freezeLoading.value = false;
  }

  freezePopup.value = false;
}

async function onCancelFrozen() {
  if (!planVer.value) return;
  cancelLoading.value = true;

  await cancelFreezeAction(
    planCycleID.value,
    planVer.value,
    userInfo.value?.email || "",
  );

  confirmCancelPopup.value = false;
  cancelLoading.value = false;
}

// === Lifecycle ===

onMounted(async () => {
  if (planVer.value) {
    await loadFilters(planVer.value);
    handleSearch();
  }
});

// planVer change: reload
watch(planVer, async (newVer) => {
  if (newVer) {
    reset();
    await loadFilters(newVer);
    handleSearch();
  }
});
</script>

<style scoped lang="scss">
.ontime-rescheduled-plan-result-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.content-section {
  padding: 0 20px 20px 20px;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.hide-splitter :deep(.splitpanes__splitter) {
  display: none;
}

.controller-container {
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.controller-search-container {
  display: flex;
  gap: 6px;
}

// Frozen plan pill
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
}

.info-frozen-plan-text {
  font-size: 13px;
  color: #434c60;
}

.info-frozen-plan-ver {
  color: #4568e0;
  cursor: pointer;
  text-decoration: underline;
}

// Freeze popup
.plan-freeze-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.plan-freeze-check-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
}

.plan-freeze-info-wrapper {
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background-color: #f8f8fd;
  border-radius: 4px;
  border: solid 1px #e1e3f0;
}

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

// Cancel button style
:deep(.moz-button.moz-default-button.confirm-cancel) {
  background-color: #d6def8;
  border: solid 1px #d6def8;

  span {
    font-weight: 300;
    color: #4568e0;
  }

  &:disabled {
    background-color: #e0e1ec;
    border-color: #e0e1ec;
  }

  &:disabled span {
    color: #a7b1bc;
  }

  &:hover:not(:disabled) {
    background-color: #4568e04d;
    border-color: #4568e033;
  }
}

.confirm-cancel-popup-content-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #28364e;
}
</style>
