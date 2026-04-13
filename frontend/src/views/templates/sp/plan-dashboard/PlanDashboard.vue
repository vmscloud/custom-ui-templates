<template>
  <div class="plan-dashboard-page">
    <Controller
      :navigations="[t('menu-ProductionPlanning'), t('menu-PlanDashboard2')]"
    >
      <template #action>
        <div v-if="frozenVer" class="frozen-plan-badge">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle
              cx="7"
              cy="7"
              r="6"
              stroke="#8998b5"
              stroke-width="1.2"
              fill="none"
            />
            <path
              d="M7 4v3M7 9v.5"
              stroke="#8998b5"
              stroke-width="1.2"
              stroke-linecap="round"
            />
          </svg>
          <span class="frozen-plan-text"
            >{{ t("text-frozen_plan") }}:
            <span class="frozen-plan-ver">{{ frozenVer }}</span></span
          >
        </div>
        <div class="dashboard-separator" />
        <Radio
          :valueExpr="'value'"
          :display-expr="'label'"
          :items-source="regionOptions"
          v-model="region"
          variant="segment"
        />
        <div class="dashboard-separator" />
        <button
          class="dashboard-controller-btn"
          style="background-color: #fa9e2321"
          @click="
            openLinkNewTab(
              {
                path: '/pe/ErrorReport',
                query: {
                  planVer: planVer || '',
                  'severityType[+]': 'Warning,Notice',
                },
              },
              true,
            )
          "
        >
          <IconToastWarning :width="14" :height="14" :color="'#fa9e23'" />
          <div class="num" style="color: #fa9e23">{{ warningCount }}</div>
        </button>
        <button
          class="dashboard-controller-btn"
          style="background-color: #4568e029"
          @click="
            openLinkNewTab(
              {
                path: '/pe/ErrorReport',
                query: { planVer: planVer || '', 'severityType[+]': 'Info' },
              },
              true,
            )
          "
        >
          <IconInfoFilled :width="14" :height="14" :color="'#4568E0'" />
          <div class="num" style="color: #4568e0">{{ infoCount }}</div>
        </button>

        <Button
          class="dashboard-controller-btn setting-btn"
          type="accent-icon"
          @click="showSettings = !showSettings"
        >
          <template #icon>
            <IconSetting :color="'#ffffff'" />
          </template>
        </Button>
      </template>
    </Controller>

    <section class="content-section">
      <div v-if="!dashboardData && !loading" class="empty-state">
        <EmptyState :is-read-only="true" />
      </div>

      <div v-else class="dashboard-grid" :class="{ 'is-loading': loading }">
        <div class="panel panel-a">
          <PlanDashboardSub1 />
        </div>
        <div class="panel panel-b">
          <PlanDashboardSub2 />
        </div>
        <div class="panel panel-c">
          <PlanDashboardSub3 />
        </div>

        <div class="filter-row">
          <Radio
            :disabled="region !== 'RTF_HK'"
            v-model="detailRegion"
            :items-source="detailRegionOptions"
            display-expr="label"
            value-expr="value"
            variant="segment"
            class="detail-region-options"
          />
        </div>

        <div class="panel panel-d">
          <PlanDashboardSub4 />
        </div>
        <div class="panel panel-e">
          <PlanDashboardSub5 />
        </div>
        <div class="panel panel-f">
          <PlanDashboardSub6 />
        </div>
      </div>
    </section>

    <!-- Settings Popup -->
    <PlanDashboardSettings
      v-if="showSettings"
      :plan-ver="planVer"
      :user-id="currentUserId"
      @close="showSettings = false"
      @saved="handleSettingsSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, provide } from "vue";
import { useTranslation } from "i18next-vue";
import { showMessage } from "@moz-shared/utils";
import {
  Controller,
  Radio,
  Button,
  EmptyState,
} from "@vmscloud/moz-ui-components";
import {
  useHostPlanCycle,
  useHostUser,
  useHostNavigation,
} from "@/composables/useHostStores";

const { t } = useTranslation();
import { usePlanDashboard } from "./planDashboard";
import PlanDashboardSub1 from "./components/PlanDashboardSub1.vue";
import PlanDashboardSub2 from "./components/PlanDashboardSub2.vue";
import PlanDashboardSub3 from "./components/PlanDashboardSub3.vue";
import PlanDashboardSub4 from "./components/PlanDashboardSub4.vue";
import PlanDashboardSub5 from "./components/PlanDashboardSub5.vue";
import PlanDashboardSub6 from "./components/PlanDashboardSub6.vue";
import PlanDashboardSettings from "./components/PlanDashboardSettings.vue";
import IconInfoFilled from "./assets/IconInfoFilled.vue";
import IconToastWarning from "./assets/IconToastWarning.vue";
import IconSetting from "./assets/IconSetting.vue";

// Host 데이터
const { planVer, fromDate } = useHostPlanCycle();
const planMonth = computed(() => {
  const fd = fromDate.value;
  if (fd && fd.length >= 7) return fd.substring(5, 7);
  // fallback: planVer에서 추출 (예: "20260403-M-01" → "04")
  const pv = planVer.value;
  return pv && pv.length >= 6 ? pv.substring(4, 6) : "";
});
const { userInfo } = useHostUser();
const { openLinkNewTab } = useHostNavigation();

// Composable
const planDashboard = usePlanDashboard();
const {
  region,
  detailRegion,
  dashboardData,
  frozenVer,
  loading,
  userId,
  loadDashboard,
  loadSettings,
  reset,
} = planDashboard;

// provide to sub-components
provide("planDashboard", planDashboard);
provide("openLinkNewTab", openLinkNewTab);
provide("planMonth", planMonth);
provide("hostPlanVer", planVer);

// 로컬 상태
const showSettings = ref(false);

// 현재 사용자 ID
const currentUserId = computed(() => userInfo.value?.id ?? "");

// 정적 옵션
const regionOptions = [
  { value: "RTF", label: "전체" },
  { value: "RTF_대구", label: "대구" },
  { value: "RTF_HK", label: "HK" },
  { value: "RTF_APEX", label: "APEX" },
];

const detailRegionOptions = [
  { value: "전체", label: "전체" },
  { value: "HK 완제", label: "HK 완제" },
  { value: "HK 반제", label: "HK 반제" },
];

// 오류 카운트
const warningCount = computed(() => {
  if (!dashboardData.value?.errorLogSummary) return 0;
  return dashboardData.value.errorLogSummary
    .filter((r: any) => r.severity === "Warning" || r.severity === "Notice")
    .reduce((sum: number, r: any) => sum + (r.cnt || 0), 0);
});

const infoCount = computed(() => {
  if (!dashboardData.value?.errorLogSummary) return 0;
  return dashboardData.value.errorLogSummary
    .filter((r: any) => r.severity === "Info")
    .reduce((sum: number, r: any) => sum + (r.cnt || 0), 0);
});

// 이벤트 핸들러

async function handleSearch() {
  if (!planVer.value) {
    showMessage("계획 버전을 선택해주세요.", false);
    return;
  }
  const uid = currentUserId.value;
  userId.value = uid;
  reset();
  await loadDashboard(planVer.value, uid);
}

async function handleSettingsSaved() {
  showSettings.value = false;
  const uid = currentUserId.value;
  if (uid) {
    await loadSettings(uid);
  }
  // 설정 저장 후 대시보드 재조회
  if (planVer.value) {
    await loadDashboard(planVer.value, uid);
  }
}

// Lifecycle

onMounted(async () => {
  const uid = currentUserId.value;
  userId.value = uid;
  if (uid) {
    await loadSettings(uid);
  }
  if (planVer.value) {
    await handleSearch();
  }
});

watch(planVer, async (newVer) => {
  if (newVer) {
    reset();
    await handleSearch();
  }
});

// region 변경 시 detailRegion 리셋 + 대시보드 재조회
watch(region, async (newVal, oldVal) => {
  if (newVal === oldVal) return;
  detailRegion.value = "전체";
  if (planVer.value) {
    await handleSearch();
  }
});

// detailRegion 변경 시 대시보드 재조회
watch(detailRegion, async (newVal, oldVal) => {
  if (newVal === oldVal) return;
  if (planVer.value) {
    await handleSearch();
  }
});
</script>

<style scoped lang="scss">
.plan-dashboard-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-section {
  overflow-y: auto;
  padding-left: 20px;
  padding-right: 12px;
  padding-bottom: 0;
  flex: 1;
}

.dashboard-grid {
  display: grid;
  grid-template-rows: minmax(315px, 35vh) 30px auto;
  grid-template-columns: repeat(3, 1fr);
  grid-template-areas:
    "a b c"
    "filter filter filter"
    "d e f";
  min-height: 100%;
  width: 100%;
  padding-bottom: 20px;
  column-gap: 22px;
  row-gap: 16px;
}

.panel {
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 514px;
  overflow: hidden;
}

.panel :deep(.container) {
  height: 100%;
  width: 100%;
  min-height: 0;
  border: 1px solid #bbc6d9;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-a {
  grid-area: a;
}
.panel-b {
  grid-area: b;
}
.panel-c {
  grid-area: c;
}
.panel-d {
  grid-area: d;
}
.panel-e {
  grid-area: e;
}
.panel-f {
  grid-area: f;
}
.filter-row {
  grid-area: filter;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.frozen-plan-badge {
  max-width: fit-content;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  border: 1px solid #bac6d4;
  border-radius: 50px;
  background-color: #f8f8fd;
  padding: 0 10px;
  .frozen-plan-text {
    font-size: 13px;
    color: #434c60;
    white-space: nowrap;
  }
  .frozen-plan-ver {
    color: #4568e0;
    text-decoration: underline;
    cursor: pointer;
  }
}

.dashboard-controller-btn {
  height: 30px;
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  .num {
    font-size: 0.875rem;
    font-weight: 400;
  }
}

.setting-btn.setting-btn.setting-btn {
  width: 30px;
  min-width: 30px;
  padding: 0;
  margin-left: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dashboard-separator {
  width: 1px;
  height: 14px;
  background-color: #bac6d4;
  margin: 0 4px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.dashboard-grid.is-loading {
  position: relative;
  pointer-events: none;
  opacity: 0.5;
  transition: opacity 0.15s;
}

:deep(.detail-region-options) .radio-container.segment {
  min-width: 215px;
}
</style>
