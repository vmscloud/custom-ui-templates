<template>
  <div class="rtf-report-detail">
    <!-- Main Detail Grid -->
    <ExtendFlexGrid
      name="rtfReportDetail"
      :itemsSource="data"
      height="100%"
      :isReadOnly="true"
      allowSorting="None"
      :initialized="onInitialized"
      :selectionChanged="onSelectionChanged"
      :formatItem="onFormatItem"
      :loading="loading"
      :use-tool-box="false"
      :setContextMenuProps="{
        useFlexGridSetting: true,
        useFilter: true,
        useExportExcel: true,
        customMenu: contextMenuItems,
      }"
    >
      <!-- 기본 컬럼 -->
      <WjFlexGridColumn binding="demandID" header="수요 ID" :width="100" />
      <WjFlexGridColumn binding="custID" header="고객" :width="100" />
      <WjFlexGridColumn
        binding="onTimeRatio"
        header="On-Time %"
        :width="85"
        align="right"
      />
      <WjFlexGridColumn
        binding="lateRatio"
        header="Late %"
        :width="75"
        align="right"
      />
      <WjFlexGridColumn
        binding="rtfRatio"
        header="RTF %"
        :width="75"
        align="right"
      />
      <WjFlexGridColumn
        binding="_short_detail"
        header="상세"
        :width="72"
        align="center"
        :isReadOnly="true"
      />
      <WjFlexGridColumn
        binding="itemGroupID"
        header="제품 그룹"
        :width="100"
      />
      <WjFlexGridColumn binding="itemID" header="제품 ID" :width="100" />
      <WjFlexGridColumn binding="itemName" header="제품명" :width="120" />
      <WjFlexGridColumn
        binding="dueWeek"
        header="납기 주차"
        :width="90"
        align="center"
      />
      <WjFlexGridColumn binding="dueDate" header="납기일" :width="100" />
      <WjFlexGridColumn
        binding="demandQty"
        header="수요량"
        :width="90"
        align="right"
        format="n0"
      />
      <WjFlexGridColumn
        binding="onTimeQty"
        header="On-Time 수량"
        :width="100"
        align="right"
        format="n0"
      />
      <WjFlexGridColumn
        binding="lateQty"
        header="Late 수량"
        :width="90"
        align="right"
        format="n0"
      />
      <WjFlexGridColumn
        binding="rtfQty"
        header="RTF 수량"
        :width="90"
        align="right"
        format="n0"
      />
      <WjFlexGridColumn
        binding="shortQty"
        header="Short 수량"
        :width="90"
        align="right"
        format="n0"
      />
      <WjFlexGridColumn
        binding="qtyUom"
        header="단위"
        :width="60"
        :visible="false"
      />
      <WjFlexGridColumn
        binding="demand_type"
        header="수요 유형"
        :width="90"
        :visible="false"
      />
      <WjFlexGridColumn
        binding="item_type"
        header="제품 유형"
        :width="90"
        :visible="false"
      />
      <WjFlexGridColumn
        binding="prod_type"
        header="생산 유형"
        :width="90"
        :visible="false"
      />
      <WjFlexGridColumn
        binding="item_size_type"
        header="제품 크기"
        :width="90"
        :visible="false"
      />
      <WjFlexGridColumn
        binding="item_spec"
        header="제품 사양"
        :width="100"
        :visible="false"
      />

      <!-- 동적 속성 컬럼 -->
      <WjFlexGridColumn
        v-for="col in propColumns"
        :key="col.columnName"
        :binding="col.columnName"
        :header="col.displayText"
        :width="120"
        :visible="false"
      />
    </ExtendFlexGrid>

    <!-- Short 사유 팝업 -->
    <Popup v-model:visible="shortPopupVisible" title="Short 사유 상세">
      <template #default>
        <div class="popup-grid-wrapper">
          <ExtendFlexGrid
            name="rtfShortReasonGrid"
            :itemsSource="shortData"
            height="100%"
            :isReadOnly="true"
            :use-tool-box="false"
          >
            <WjFlexGridColumn
              binding="shortType"
              header="부족 유형"
              :width="100"
              align="center"
            />
            <WjFlexGridColumn
              binding="shortCategory"
              header="부족 분류"
              :width="150"
            />
            <WjFlexGridColumn
              binding="shortReason"
              header="부족 사유"
              :width="200"
            />
            <WjFlexGridColumn
              binding="shortQty"
              header="부족 수량"
              :width="100"
              align="right"
              format="n0"
            />
            <WjFlexGridColumn
              binding="qtyUom"
              header="단위"
              :width="60"
              :visible="false"
            />
            <WjFlexGridColumn
              binding="shortDetailInfo"
              header="부족 상세 정보"
              :width="300"
            />
            <WjFlexGridColumn
              binding="isbID"
              header="ISB 코드"
              :width="300"
            />
            <WjFlexGridColumn
              binding="bomID"
              header="BOM 코드"
              :width="300"
            />
          </ExtendFlexGrid>
        </div>
      </template>
      <template #footer>
        <Button @click="shortPopupVisible = false">닫기</Button>
      </template>
    </Popup>

    <!-- 제품 속성 팝업 -->
    <Popup v-model:visible="itemPropsPopupVisible" title="제품 속성 상세">
      <template #default>
        <div class="popup-grid-wrapper">
          <ExtendFlexGrid
            name="rtfItemPropsGrid"
            :itemsSource="itemPropsData"
            height="100%"
            :isReadOnly="true"
            :use-tool-box="false"
          >
            <WjFlexGridColumn binding="itemID" header="제품 ID" :width="120" />
            <WjFlexGridColumn
              binding="item_type"
              header="제품 유형"
              :width="100"
            />
            <WjFlexGridColumn
              binding="itemName"
              header="제품명"
              :width="150"
            />
            <WjFlexGridColumn
              binding="item_group"
              header="제품 그룹"
              :width="100"
            />
            <WjFlexGridColumn
              binding="item_priority"
              header="우선순위"
              :width="80"
            />
            <WjFlexGridColumn
              binding="procurement_type"
              header="조달 유형"
              :width="100"
            />
            <WjFlexGridColumn
              binding="prod_type"
              header="생산 유형"
              :width="100"
            />
            <WjFlexGridColumn
              binding="item_size"
              header="제품 크기"
              :width="80"
            />
            <WjFlexGridColumn
              binding="item_spec"
              header="제품 사양"
              :width="120"
            />
          </ExtendFlexGrid>
        </div>
      </template>
      <template #footer>
        <Button @click="itemPropsPopupVisible = false">닫기</Button>
      </template>
    </Popup>

    <!-- 수요 레코드 팝업 -->
    <Popup v-model:visible="demandRecordPopupVisible" title="수요 레코드 상세">
      <template #default>
        <div class="popup-grid-wrapper">
          <ExtendFlexGrid
            name="rtfDemandRecordGrid"
            :itemsSource="demandRecordData"
            height="100%"
            :isReadOnly="true"
            :use-tool-box="false"
          >
            <WjFlexGridColumn
              binding="demandID"
              header="수요 ID"
              :width="120"
            />
            <WjFlexGridColumn
              binding="itemID"
              header="제품 ID"
              :width="120"
            />
            <WjFlexGridColumn
              binding="site_id"
              header="사이트 ID"
              :width="100"
            />
            <WjFlexGridColumn
              binding="buffer_id"
              header="버퍼 ID"
              :width="100"
            />
            <WjFlexGridColumn
              binding="dueDate"
              header="납기일"
              :width="110"
            />
            <WjFlexGridColumn
              binding="demandQty"
              header="수요량"
              :width="90"
              align="right"
              format="n0"
            />
            <WjFlexGridColumn
              binding="demand_priority"
              header="우선순위"
              :width="80"
            />
            <WjFlexGridColumn
              binding="custID"
              header="고객 ID"
              :width="100"
            />
            <WjFlexGridColumn
              binding="demand_type"
              header="수요 유형"
              :width="100"
            />
            <WjFlexGridColumn
              binding="max_lateness_day"
              header="최대 지연일"
              :width="90"
            />
            <WjFlexGridColumn
              binding="max_earliness_day"
              header="최대 선행일"
              :width="90"
            />
            <WjFlexGridColumn
              binding="demand_group"
              header="수요 그룹"
              :width="100"
            />
          </ExtendFlexGrid>
        </div>
      </template>
      <template #footer>
        <Button @click="demandRecordPopupVisible = false">닫기</Button>
      </template>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ExtendFlexGrid, type ExtendGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import {
  type FlexGrid,
  GroupRow,
} from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { Popup, Button } from "@vmscloud/moz-ui-components";
import type { RtfDetailData, RtfShortData, PropColumn } from "./rtfReport";

// === Props & Emits ===

interface Props {
  data: RtfDetailData[];
  loading: boolean;
  planVer: string;
  uomType: string;
  propColumns: PropColumn[];
  shortData: RtfShortData[];
  itemPropsData: any[];
  demandRecordData: any[];
}

defineProps<Props>();
const emit = defineEmits<{
  (e: "demand-selected", demandID: string): void;
  (e: "load-short", demandID: string): void;
  (e: "load-item-props", itemID: string): void;
  (e: "load-demand-record", demandID: string): void;
}>();

// === Local State ===

const grid = ref<FlexGrid>();
const selectedDemandId = ref("");
const selectedItemId = ref("");
const shortPopupVisible = ref(false);
const itemPropsPopupVisible = ref(false);
const demandRecordPopupVisible = ref(false);

// === Context Menu ===

const contextMenuItems = [
  {
    align: 0,
    header: "제품 속성 보기",
    cmd: "openItemProps",
    clicked: () => {
      if (selectedItemId.value) {
        emit("load-item-props", selectedItemId.value);
        itemPropsPopupVisible.value = true;
      }
    },
    active: () => !!selectedItemId.value,
  },
  {
    align: 0,
    header: "수요 레코드 보기",
    cmd: "openDemandRecord",
    clicked: () => {
      if (selectedDemandId.value) {
        emit("load-demand-record", selectedDemandId.value);
        demandRecordPopupVisible.value = true;
      }
    },
    active: () => !!selectedDemandId.value,
  },
];

// === Grid Initialization ===

function onInitialized(flexGrid: FlexGrid, _extendGrid: ExtendGrid) {
  grid.value = flexGrid;
}

// === Selection Changed ===

function onSelectionChanged(s: FlexGrid, e: any) {
  if (!s || e.row < 0) return;

  const row = s.rows[e.row];
  if (!row || row instanceof GroupRow) return;

  const dataItem = (row as any).dataItem as RtfDetailData;
  if (!dataItem) return;

  selectedDemandId.value = dataItem.demandID ?? "";
  selectedItemId.value = dataItem.itemID ?? "";

  if (dataItem.demandID) {
    emit("demand-selected", dataItem.demandID);
  }
}

// === FormatItem ===

const QTY_BINDINGS = [
  "demandQty",
  "onTimeQty",
  "lateQty",
  "rtfQty",
  "shortQty",
];
const RATIO_BINDINGS = ["onTimeRatio", "lateRatio", "rtfRatio"];

function onFormatItem(s: FlexGrid, e: any) {
  if (e.panel !== s.cells) return;

  const row = s.rows[e.row];
  if (!row || row instanceof GroupRow) return;

  const dataItem = (row as any).dataItem as RtfDetailData;
  if (!dataItem) return;

  const binding = s.columns[e.col]?.binding;
  if (!binding) return;

  // "상세 보기" clickable link
  if (binding === "_short_detail") {
    e.cell.innerHTML =
      '<span class="detail-link" style="color:#4568e0;text-decoration:underline;cursor:pointer;">상세 보기</span>';
    if (!e.cell.dataset.clickBound) {
      e.cell.dataset.clickBound = "1";
      e.cell.addEventListener("click", () => {
        if (dataItem.demandID) {
          emit("load-short", dataItem.demandID);
          shortPopupVisible.value = true;
        }
      });
    }
  }

  // Quantity formatting
  if (QTY_BINDINGS.includes(binding)) {
    const val = dataItem[binding];
    if (val != null) e.cell.innerText = Number(val).toLocaleString();
  }

  // Ratio formatting with %
  if (RATIO_BINDINGS.includes(binding)) {
    const val = dataItem[binding];
    if (val != null) {
      e.cell.innerText =
        Number(val).toLocaleString(undefined, { maximumFractionDigits: 1 }) +
        "%";
    }
  }

  // Row-level conditional formatting (applied to entire row)
  if (dataItem.rtfRatio < 100) {
    e.cell.classList.add("ratio-short");
  } else if (dataItem.rtfRatio === 100 && dataItem.lateRatio > 0) {
    e.cell.classList.add("ratio-late");
  }

  // RTF ratio font color for shortage
  if (binding === "rtfRatio" && dataItem.rtfRatio < 100) {
    e.cell.classList.add("ratio-short-font");
  }
}
</script>

<style scoped lang="scss">
.rtf-report-detail {
  height: 100%;
  width: 100%;
  position: relative;
}

.popup-grid-wrapper {
  width: 700px;
  height: 400px;
  min-width: 500px;
  min-height: 300px;
}

// Short (RTF < 100%) — light red background
:deep(.ratio-short) {
  background-color: #f6d5d5 !important;
}

// Late (RTF = 100% & Late > 0) — light orange background
:deep(.ratio-late) {
  background-color: #fde6c8 !important;
}

// Red font for shortage ratio
:deep(.ratio-short-font) {
  span,
  & {
    color: #dc5a5a !important;
  }
}

// Selected state override
:deep(.ratio-short.wj-state-multi-selected),
:deep(.ratio-short.wj-state-active),
:deep(.ratio-late.wj-state-multi-selected),
:deep(.ratio-late.wj-state-active) {
  background-color: #eae0ec !important;
}
</style>
