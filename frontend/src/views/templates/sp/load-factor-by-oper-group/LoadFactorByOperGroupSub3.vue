<template>
  <div class="moz-frame-for-outer-control" style="padding: 0px">
    <!-- v-show를 감싸는 div에 적용하여 ExtendFlexGrid 내부 CSS가 display: none을 override하지 못하게 함 -->
    <div v-show="showGrid" class="grid-wrapper">
      <ExtendFlexGrid
        height="100%"
        name="LoadFactorByOperGroupDetail"
        :useMerge="['oper_group_id', 'str_date']"
        :autoGenerateColumns="false"
        :alternatingRowStep="0"
        :itemsSource="detailDataSource"
        :initialized="onInitialized"
        :isReadOnly="true"
        :validateKey="'none'"
        :setContextMenuProps="{
          useGroupColumn: false,
          useViewSelectColumn: false,
          useBulkEditColumn: false,
          useExportExcel: false,
          useExportImport: false,
        }"
      >
        <template #tool-items>
          <div @click="handleZoomClick" class="zoom-button">
            <IconExpandArrow v-if="!isZoomedSub3" />
            <IconCollapseArrow v-else />
          </div>
        </template>

        <WjFlexGridColumn
          :width="160"
          binding="oper_group_id"
          :header="t('text-isu_oper_group_id')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="str_date"
          :header="t('text-isu_str_date')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="capa"
          :header="t('text-isu_capa')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="str_qty"
          :header="t('text-isu_str_qty')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="outer_str_area"
          :header="t('text-isu_outer_str_area')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="inner_str_area"
          :header="t('text-isu_inner_str_area')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="str_rate"
          :header="t('text-isu_str_rate')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="floor_number"
          :header="t('text-isu_floor_number')"
        />
        <WjFlexGridColumn
          :width="140"
          binding="item_id"
          :header="t('text-isu_item_id')"
        />
        <WjFlexGridColumn
          :width="140"
          binding="item_group_id"
          :header="t('text-isu_item_group_id')"
        />
        <WjFlexGridColumn
          :width="140"
          binding="demand_id"
          :header="t('text-isu_demand_id')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="due_date"
          :header="t('text-isu_due_date')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="aps_due_date"
          :header="t('text-isu_aps_due_date')"
        />
        <WjFlexGridColumn
          :width="120"
          binding="oper_id"
          :header="t('text-isu_oper_id')"
        />
      </ExtendFlexGrid>
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
import { EmptyState } from "@vmscloud/moz-ui-components";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import { type FlexGrid } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { useTranslation } from "i18next-vue";
import { computed, ref } from "vue";
import IconExpandArrow from "./assets/IconExpandArrow.vue";
import IconCollapseArrow from "./assets/IconCollapseArrow.vue";

/**
 * DEFINE DEFAULT VARIABLE
 */
const { t } = useTranslation(); // 다국어

const grid = ref<FlexGrid | null>(null); // Wijmo grid
const extendGrid = ref<ExtendGrid | null>(null); // Wijmo grid 확장 기능

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

// ✅ 확대 버튼 클릭 핸들러
const handleZoomClick = () => {
  emit("update:isZoomedSub3", !props.isZoomedSub3);
};

// GRID INITIALIZE
const onInitialized = (flexGrid: FlexGrid, _extendGrid: ExtendGrid) => {
  grid.value = flexGrid;
  extendGrid.value = _extendGrid;
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
