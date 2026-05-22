<template>
  <div class="load-factor-by-oper-group-page">
    <Controller
      :navigations="navigations"
      :show-filter-button="true"
      :actions="[
        {
          action: 'Search',
          click: async () => {
            await onLoad();
          },
          loading: false,
        },
      ]"
    >
      <template #action>
        <Button @click="showPopup">
          <template #icon>
            <IconDownload :size="'14'" color="#ffffff" />
          </template>

          <div class="download-button-text">
            {{ t("text-detail_data_excel_download") }}
          </div>
        </Button>
      </template>
      <template #filter>
        <DateInput
          :label="t('text-from_date')"
          v-model="startDate"
          :min="planStartDate"
          :max="endDate"
        />
        <DateInput
          :label="t('text-to_date')"
          v-model="endDate"
          :min="startDate"
        />
        <div class="load-factor-controller-checkbox">
          <CheckBox
            :label="t('text-isu_include_undefined_capa')"
            v-model="showOriginData"
          />
        </div>
      </template>
    </Controller>
    <div class="moz-frame-for-outer-control">
      <!-- 확대 상태일 때 splitter 숨김 (v-show로 그리드 상태 유지) -->
      <SplitPane
        horizontal
        style="max-width: 100%"
        :class="{ 'hide-splitter': isZoomedSub3 }"
      >
        <Pane
          :size="isZoomedSub3 ? '0%' : '34%'"
          :max-size="isZoomedSub3 ? '0%' : '300%'"
          :min-size="isZoomedSub3 ? '0%' : '20%'"
          v-show="!isZoomedSub3"
        >
          <LoadFactorByOperGroupSub1
            :mainDataSource="mainDataSource"
            :loading="loading"
            :clickedSeriesData="clickedSeriesData"
            :detailChartSelectSource="detailChartSelectSource"
            @update:clickedSeriesData="onClickedSeriesDataUpdate"
            @update:detailChartSelectSource="onDetailChartSelectSourceUpdate"
          />
        </Pane>
        <Pane
          :size="isZoomedSub3 ? '0%' : '33%'"
          :max-size="isZoomedSub3 ? '0%' : '300%'"
          :min-size="isZoomedSub3 ? '0%' : '20%'"
          v-show="!isZoomedSub3"
        >
          <LoadFactorByOperGroupSub2
            :detailChartDataSource="detailChartDataSource"
            :originDetailChartDataSource="originDetailChartDataSource"
            :loading="loading"
            :groupLoading="groupLoading"
            :clickedSeriesData="clickedSeriesData"
            :detailChartSelectSource="detailChartSelectSource"
            @update:clickedSeriesData="onClickedSeriesDataUpdate"
          />
        </Pane>
        <Pane
          :size="isZoomedSub3 ? '100%' : '33%'"
          :max-size="isZoomedSub3 ? '100%' : '300%'"
          :min-size="isZoomedSub3 ? '100%' : '20%'"
        >
          <LoadFactorByOperGroupSub3
            :detailDataSource="detailDataSource"
            :detailLoading="detailLoading"
            :clickedSeriesData="clickedSeriesData"
            :isZoomedSub3="isZoomedSub3"
            @update:isZoomedSub3="isZoomedSub3 = $event"
          />
        </Pane>
      </SplitPane>
    </div>

    <Popup
      :title="t('text-detail_data_excel_download')"
      v-model:visible="isShowPopup"
      :onCancel="
        () => {
          isShowPopup = false;
        }
      "
      class="demand-popup"
      :resizeable="true"
    >
      <div class="excel-download-popup-content">
        <div class="excel-download-popup-description">
          {{ t("msg-select_oper_groups_for_excel") }}
        </div>
        <MultiSelect
          :placeholder="`${!operGroupSource.length ? t('MOZ-DATA_EMPTY') : ''}`"
          v-model="excelDownloadOperGroupIds"
          :header-format="'{count:n0} GROUPS'"
          :use-select-all="true"
          :use-filter="true"
          key-prop="oper_group_id"
          display-prop="oper_group_id"
          :itemsSource="execelDownloadOperGroupSource"
          @close="
            () => {
              if (
                !excelDownloadOperGroupIds?.length &&
                detailChartSelectSource?.length
              ) {
                excelDownloadOperGroupIds = detailChartSelectSource.map(
                  (item: any) => item.oper_group_id,
                );
              } else if (!excelDownloadOperGroupIds?.length) {
                excelDownloadOperGroupIds = execelDownloadOperGroupSource.map(
                  (item: any) => item.oper_group_id,
                );
              }
            }
          "
        />
      </div>
      <template #footer>
        <Button
          :text="t('text-download')"
          @click="
            () => {
              downloadExcelData();
              isShowPopup = false;
            }
          "
          :disabled="!excelDownloadOperGroupIds?.length"
        />
        <Button
          type="outline"
          :text="t('text-cancel')"
          :width="80"
          @click="
            () => {
              isShowPopup = false;
            }
          "
        />
      </template>
    </Popup>
  </div>
</template>
<script setup lang="ts">
import {
  Controller,
  Button,
  CheckBox,
  DateInput,
  MultiSelect,
  Pane,
  Popup,
  SplitPane,
} from "@vmscloud/moz-ui-components";
import { useTranslation } from "i18next-vue";
import { computed, nextTick, onMounted, ref, toRaw, watch } from "vue";
import { useHostPlanCycle, useHostNavigations } from "@/composables/useHostStores";
import {
  fetchMain,
  fetchGroup,
  fetchDetail,
  fetchOperGroups,
} from "./loadFactorByOperGroup";
import LoadFactorByOperGroupSub1 from "./LoadFactorByOperGroupSub1.vue";
import LoadFactorByOperGroupSub2 from "./LoadFactorByOperGroupSub2.vue";
import LoadFactorByOperGroupSub3 from "./LoadFactorByOperGroupSub3.vue";
import IconDownload from "./assets/IconDownload.vue";
import { downloadBigData } from "@vmscloud/moz-wijmo-grid/excel";
import { getProjectId } from "@/api/client";

const { t } = useTranslation(); // 다국어
const navigations = useHostNavigations(() => [t("text-menu-production_planning"), t("text-isu_entire_oper_group_avg_load_factor")]);
const { planVer, fromDate: planStartDate } = useHostPlanCycle();

// ===== Oper Group State =====
const operGroupIds = ref<string[]>([]);
const operGroupSource = ref<{ oper_group_id: string }[]>([]);
const operGroupIsSuccess = ref(false);

const showOriginData = ref(true);

const startDate = ref<string>("");
const endDate = ref<string>("");

// ===== Main Data =====
const mainDataSource = ref<any[]>([]);
const clickedSeriesData = ref<string>("");
const detailChartSelectSource = ref<{ oper_group_id: string }[]>([]);
const loading = ref(false);

// ===== Excel Download =====
const excelDownloadOperGroupIds = ref<string[]>([]);
const execelDownloadOperGroupSource = computed(() => {
  // 세부 데이터 다운로드 MultiSelect에 detailChartSelectSource에 들어있는 공정 그룹을 상단으로 올리는 로직
  const selectedIds = new Set(
    detailChartSelectSource.value.map((item: any) => item.oper_group_id),
  );

  return toRaw(operGroupSource.value).sort((a: any, b: any) => {
    const aIsSelected = selectedIds.has(a.oper_group_id);
    const bIsSelected = selectedIds.has(b.oper_group_id);

    // ✅ 선택된 항목을 상단으로
    if (aIsSelected && !bIsSelected) return -1;
    if (!aIsSelected && bIsSelected) return 1;

    // ✅ 둘 다 선택되었거나 둘 다 선택되지 않은 경우 oper_group_id로 정렬
    return a.oper_group_id.localeCompare(b.oper_group_id);
  });
});

// ===== Sub3 확대/축소 상태 =====
const isZoomedSub3 = ref(false);

// ===== Detail Chart (Sub2) =====
const detailChartDataSource = ref<any[]>([]);
const originDetailChartDataSource = ref<any[]>([]);
const groupLoading = ref(false);

// ===== Detail Grid (Sub3) =====
const detailDataSource = ref<any[]>([]);
const detailLoading = ref(false);

// ===== Main Load Params =====
const mainLoadParams = computed(() => ({
  planVer: planVer.value,
  fromDate: startDate.value,
  toDate: endDate.value,
  operGroupIDs: operGroupIds.value,
  showOriginData: showOriginData.value,
}));

// capaDays - kept for reference, may be used by future excel download
const _capaDays = computed(() =>
  mainLoadParams.value.fromDate && mainLoadParams.value.toDate
    ? Math.abs(
        Math.ceil(
          (new Date(mainLoadParams.value.toDate).getTime() -
            new Date(mainLoadParams.value.fromDate).getTime()) /
            (1000 * 60 * 60 * 24),
        ) + 1,
      )
    : 0,
);
void _capaDays;

// ===== Date Init =====
function toLocalDateString(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

watch(
  planStartDate,
  () => {
    if (planStartDate.value) {
      // planStartDate is Dayjs or string (e.g. "2026-03-23T00:00:00")
      const raw = planStartDate.value;
      let dateStr: string;
      if (typeof raw === "string") {
        // "2026-03-23T00:00:00" or "2026-03-23" → take first 10 chars
        dateStr = raw.slice(0, 10);
      } else if (raw.format) {
        // Dayjs
        dateStr = raw.format("YYYY-MM-DD");
      } else {
        dateStr = toLocalDateString(new Date(raw));
      }
      startDate.value = dateStr;
      const endDateObj = new Date(dateStr + "T00:00:00");
      endDateObj.setDate(endDateObj.getDate() + 29);
      endDate.value = toLocalDateString(endDateObj);
    }
  },
  { immediate: true },
);

// ===== Load Oper Groups =====
async function loadOperGroupsData() {
  if (!planVer.value) return;
  try {
    const res = await fetchOperGroups(planVer.value);
    if (res.success && res.data?.length) {
      operGroupSource.value = res.data.map((item: any) => {
        if (item?.oper_group_label === "text-not_set_oper_group") {
          item.oper_group_label = t("text-not_set_oper_group");
        }
        return item;
      });
      operGroupIds.value = operGroupSource.value.map(
        (item: any) => item.oper_group_id,
      );
      operGroupIsSuccess.value = true;
    } else {
      operGroupSource.value = [];
      operGroupIds.value = [];
      operGroupIsSuccess.value = true;
    }
  } catch {
    console.error("Failed to load oper groups");
    operGroupIsSuccess.value = false;
  }
}

// ===== Main Load =====
const onLoad = async () => {
  if (!planVer.value || !startDate.value || !endDate.value) {
    console.warn("[LoadFactor] planVer/startDate/endDate 미설정 — 조회 스킵");
    return;
  }
  detailChartSelectSource.value = [];
  clickedSeriesData.value = "";
  loading.value = true;

  try {
    const res = await fetchMain({
      planVer: planVer.value,
      fromDate: startDate.value,
      toDate: endDate.value,
      operGroupIDs: operGroupIds.value,
      includeUndefinedCapa: showOriginData.value,
    });

    if (res.success && res.data?.length) {
      mainDataSource.value = res.data.map((item: any, index: number) => ({
        ...item,
        oper_group_id: item.oper_group_id,
        legend: t("부하율"),
        rnum: index + 1,
      }));
    } else {
      mainDataSource.value = [];
    }
  } catch {
    console.error("Failed to load main data");
    mainDataSource.value = [];
  } finally {
    loading.value = false;
  }
};

// ===== Load Group Data (Sub2) =====
const loadGroupData = async (operGroupId: string) => {
  if (!planVer.value || !startDate.value || !endDate.value) return;
  groupLoading.value = true;
  try {
    const res = await fetchGroup({
      planVer: planVer.value,
      fromDate: startDate.value,
      toDate: endDate.value,
      operGroupIDs: [operGroupId],
    });

    if (res.success && res.data?.length) {
      detailChartDataSource.value = toRaw(res.data)
        .sort((a: any, b: any) => a.item_group_id - b.item_group_id)
        .filter((item: any) => item.item_group_id !== "TOTAL");
      originDetailChartDataSource.value = toRaw(res.data);
    } else {
      detailChartDataSource.value = [];
      originDetailChartDataSource.value = [];
    }
  } catch {
    console.error("Failed to load group data");
    detailChartDataSource.value = [];
    originDetailChartDataSource.value = [];
  } finally {
    groupLoading.value = false;
  }
};

// ===== Load Detail Data (Sub3) =====
const loadDetailData = async (operGroupId: string) => {
  if (!planVer.value || !startDate.value || !endDate.value) return;
  detailLoading.value = true;
  try {
    const res = await fetchDetail({
      planVer: planVer.value,
      fromDate: startDate.value,
      toDate: endDate.value,
      operGroupIDs: [operGroupId],
      includeUndefinedCapa: showOriginData.value,
    });

    if (res.success && res.data?.length) {
      detailDataSource.value = toRaw(res.data);
    } else {
      detailDataSource.value = [];
    }
  } catch {
    console.error("Failed to load detail data");
    detailDataSource.value = [];
  } finally {
    detailLoading.value = false;
  }
};

// ===== Watch clickedSeriesData → load group + detail =====
watch(clickedSeriesData, (newVal) => {
  if (newVal) {
    loadGroupData(newVal);
    loadDetailData(newVal);
  }
});

// ===== Event handlers from child components =====
const onClickedSeriesDataUpdate = (val: string) => {
  clickedSeriesData.value = val;
};

const onDetailChartSelectSourceUpdate = (val: { oper_group_id: string }[]) => {
  detailChartSelectSource.value = val;
};

const isShowPopup = ref<boolean>(false);

const showPopup = () => {
  if (detailChartSelectSource.value.length) {
    excelDownloadOperGroupIds.value = detailChartSelectSource.value.map(
      (item: any) => item.oper_group_id,
    );
  } else {
    excelDownloadOperGroupIds.value = execelDownloadOperGroupSource.value.map(
      (item: any) => item.oper_group_id,
    );
  }

  isShowPopup.value = true;
};

// LoadFactorByOperGroup Sub3 그리드와 동일한 바인딩/헤더 순서.
//   원본 APS 에서는 Sub3 FlexGrid 인스턴스에서 createColumnMapForExport(grid) 로
//   자동 추출했지만, 포팅본에선 Sub3 grid ref 를 부모로 노출하지 않아 정적 맵 사용.
const LOAD_FACTOR_DETAIL_COLUMN_MAP: Record<string, string> = {
  oper_group_id: t("text-isu_oper_group_id"),
  str_date: t("text-isu_str_date"),
  capa: t("text-isu_capa"),
  str_qty: t("text-isu_str_qty"),
  outer_str_area: t("text-isu_outer_str_area"),
  inner_str_area: t("text-isu_inner_str_area"),
  str_rate: t("text-isu_str_rate"),
  floor_number: t("text-isu_floor_number"),
  item_id: t("text-isu_item_id"),
  item_group_id: t("text-isu_item_group_id"),
  demand_id: t("text-isu_demand_id"),
  due_date: t("text-isu_due_date"),
  aps_due_date: t("text-isu_aps_due_date"),
  oper_id: t("text-isu_oper_id"),
};

const downloadExcelData = async () => {
  // 원본 aps/LoadFactorByOperGroup.ts 의 downloadBigData 호출과 동일 형태.
  //   - 원본은 @/stores/queryStore 의 downloadBigData (aps-local) 를 사용했는데
  //     그 함수는 백엔드 Excel 큐 + SSE 인프라에 의존. 우리는 shim 의 downloadBigData
  //     (proxy POST → JSON → wijmo Workbook → save) 로 동일 시그니처 유지.
  try {
    await downloadBigData({
      file_name: "LoadFactorByOperGroup_Detail_Export",
      column_map: LOAD_FACTOR_DETAIL_COLUMN_MAP,
      proxy_path: `/api/custom/backend/${getProjectId()}/load-factor/detail-excel`,
      data_method: "POST",
      data_parameter: {
        ...mainLoadParams.value,
        operGroupIDs: excelDownloadOperGroupIds.value,
      },
    });
    isShowPopup.value = false;
  } catch (error) {
    console.error("[LoadFactorByOperGroup] 세부데이터 다운로드 실패:", error);
  }
};

// ===== Lifecycle =====
const callWatch = watch(
  [planVer, operGroupIsSuccess],
  () => {
    if (planVer.value && operGroupIsSuccess.value) {
      nextTick(() => {
        onLoad();
        callWatch();
      });
    }
  },
  { immediate: true, flush: "post" },
);

onMounted(() => {
  loadOperGroupsData();
});

watch(planVer, (newVal, oldVal) => {
  if (planVer.value && newVal !== oldVal) {
    loadOperGroupsData();
  }
});
</script>
<style scoped lang="scss">
.load-factor-by-oper-group-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;

  .moz-frame-for-outer-control {
    flex: 1;
    min-height: 0;
  }
}

.load-factor-controller-checkbox {
  padding-top: 21px;

  & label {
    font-weight: 500 !important;
    line-height: 100%;
    padding-top: 1px;
  }
}

.download-button-text {
  line-height: 20px;
  font-size: 14px;
}

.excel-download-popup-content {
  display: flex;
  gap: 62px;
  align-items: center;
  height: 62px;
  background-color: #4568e017;
  padding: 16px;
  border-radius: 6px;

  .excel-download-popup-description {
    font-size: 14px;
    font-weight: 400;
    color: var(color-text-700);
    line-height: 20px;
  }
}

// Pane 외곽선 (원본과 동일)
:deep(.splitpanes__pane) {
  border: 1px solid #e4e6eb;
  border-radius: 8px;
  overflow: hidden;
}

// 확대 상태일 때 splitter 숨김
:deep(.hide-splitter) {
  .splitpanes__splitter {
    display: none !important;
  }
}
</style>
