<template>
  <div class="moz-frame-for-outer-control" style="padding: 0px">
    <!-- v-show를 감싸는 div에 적용하여 그리드 내부 CSS가 display: none을 override하지 못하게 함 -->
    <div v-show="showGrid" class="grid-wrapper">
      <MozGrid
        height="100%"
        name="LoadFactorByOperGroupDetail"
        :coreConfig="coreConfig"
        :contextMenuConfig="{
          useViewSelectColumn: false,
          useBulkEditColumn: false,
          useExportExcel: false,
          useExportImport: false,
        }"
        @ready="onReady"
      >
        <template #tool-items>
          <div @click="handleZoomClick" class="zoom-button">
            <IconExpandArrow v-if="!isZoomedSub3" />
            <IconCollapseArrow v-else />
          </div>
        </template>
      </MozGrid>
    </div>
    <div
      v-show="!showGrid"
      class="grid-empty load_factor_by_oper_group-loading"
    >
      <EmptyState
        :headerMsg="t('msg-empty_state-data_empty_header')"
        :contentMsg="t('msg-select_oper_group')"
        :is-read-only="true"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { EmptyState } from "@vmscloud/moz-ui-components-vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type { GridChrome, MozGridCoreProps, PureSheet } from "@vmscloud/moz-ui-grid-vue";
import { useTranslation } from "i18next-vue";
import { computed, ref } from "vue";
import IconExpandArrow from "./assets/IconExpandArrow.vue";
import IconCollapseArrow from "./assets/IconCollapseArrow.vue";

/**
 * DEFINE DEFAULT VARIABLE
 */
const { t } = useTranslation(); // 다국어

const grid = ref<PureSheet | null>(null); // 코어 그리드
const chrome = ref<GridChrome | null>(null); // 그리드 래퍼(툴박스·컨텍스트 메뉴 등)

// ===== Props & Emits =====
const props = defineProps<{
  detailDataSource: any[];
  detailLoading: boolean;
  clickedSeriesData: string;
  isZoomedSub3: boolean;
}>();

const emit = defineEmits<{
  (e: "update:isZoomedSub3", val: boolean): void;
}>();

// 그리드 표시 여부 (v-show 조건을 computed로 분리)
const showGrid = computed(
  () => !!props.clickedSeriesData && !!props.detailDataSource.length,
);

// 그리드 설정 — 상세 데이터에는 고유 키가 없어 행 순번(__rowKey)을 키로 쓴다.
const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: ["__rowKey"],
  data: props.detailDataSource.map((row, idx) => ({ ...row, __rowKey: idx })),
  fields: [
    { id: "oper_group_id", header: t("text-isu_oper_group_id"), width: 160, readonly: true },
    { id: "str_date", header: t("text-isu_str_date"), width: 120, readonly: true },
    { id: "capa", header: t("text-isu_capa"), width: 120, readonly: true },
    { id: "str_qty", header: t("text-isu_str_qty"), width: 120, readonly: true },
    { id: "outer_str_area", header: t("text-isu_outer_str_area"), width: 120, readonly: true },
    { id: "inner_str_area", header: t("text-isu_inner_str_area"), width: 120, readonly: true },
    { id: "str_rate", header: t("text-isu_str_rate"), width: 120, readonly: true },
    { id: "floor_number", header: t("text-isu_floor_number"), width: 120, readonly: true },
    { id: "item_id", header: t("text-isu_item_id"), width: 140, readonly: true },
    { id: "item_group_id", header: t("text-isu_item_group_id"), width: 140, readonly: true },
    { id: "demand_id", header: t("text-isu_demand_id"), width: 140, readonly: true },
    { id: "due_date", header: t("text-isu_due_date"), width: 120, readonly: true },
    { id: "aps_due_date", header: t("text-isu_aps_due_date"), width: 120, readonly: true },
    { id: "oper_id", header: t("text-isu_oper_id"), width: 120, readonly: true },
  ],
}));

// ✅ 확대 버튼 클릭 핸들러
const handleZoomClick = () => {
  emit("update:isZoomedSub3", !props.isZoomedSub3);
};

// GRID INITIALIZE
const onReady = (_grid: PureSheet, _chrome: GridChrome) => {
  grid.value = _grid;
  chrome.value = _chrome;
  // 구분·일자 컬럼은 인접한 같은 값끼리 병합 (원본 useMerge)
  _grid.setMergeConfig({ type: "content", columns: ["oper_group_id", "str_date"] });
};
</script>
<style lang="scss" scoped>
.grid-wrapper {
  height: 100%;
}

.grid-empty.load_factor_by_oper_group-loading {
  position: relative;
  height: 100%;
  :deep(.load-element-outer-wrapper) {
    position: absolute;
    top: 0;
    left: 0;
  }
}

.zoom-button {
  width: 25px;
  height: 25px;

  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  &:hover {
    background-color: #f0f0f0;
    border-radius: 4px;
  }
}
</style>
