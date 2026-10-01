<template>
  <div class="rtf-report-detail">
    <!-- Main Detail Grid -->
    <MozGrid
      name="rtfReportDetail"
      :coreConfig="coreConfig"
      height="100%"
      :loading="loading"
      :use-tool-box="false"
      :use-sort="false"
      :contextMenuConfig="contextMenuConfig"
      @cell:click="onCellClick"
      @contextmenu="onContextMenu"
    />

    <!-- Short 사유 팝업 -->
    <Popup v-model:visible="shortPopupVisible" title="Short 사유 상세">
      <template #default>
        <div class="popup-grid-wrapper">
          <MozGrid
            name="rtfShortReasonGrid"
            :coreConfig="shortCoreConfig"
            height="100%"
            :use-tool-box="false"
          />
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
          <MozGrid
            name="rtfItemPropsGrid"
            :coreConfig="itemPropsCoreConfig"
            height="100%"
            :use-tool-box="false"
          />
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
          <MozGrid
            name="rtfDemandRecordGrid"
            :coreConfig="demandRecordCoreConfig"
            height="100%"
            :use-tool-box="false"
          />
        </div>
      </template>
      <template #footer>
        <Button @click="demandRecordPopupVisible = false">닫기</Button>
      </template>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type {
  FieldDef,
  IContextMenuConfig,
  MaskConfig,
  MozGridCoreProps,
} from "@vmscloud/moz-ui-grid-vue";
import { Popup, Button } from "@vmscloud/moz-ui-components-vue";
import { GRID_ROW_KEY, withRowKey } from "./rtfReport";
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

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: "demand-selected", demandID: string): void;
  (e: "load-short", demandID: string): void;
  (e: "load-item-props", itemID: string): void;
  (e: "load-demand-record", demandID: string): void;
}>();

// === Local State ===

const selectedDemandId = ref("");
const selectedItemId = ref("");
const shortPopupVisible = ref(false);
const itemPropsPopupVisible = ref(false);
const demandRecordPopupVisible = ref(false);

// === Context Menu ===

const contextMenuConfig: IContextMenuConfig = {
  useFilter: true,
  useExportExcel: true,
  customMenu: [
    {
      id: "openItemProps",
      label: "제품 속성 보기",
      handler: () => {
        if (selectedItemId.value) {
          emit("load-item-props", selectedItemId.value);
          itemPropsPopupVisible.value = true;
        }
      },
    },
    {
      id: "openDemandRecord",
      label: "수요 레코드 보기",
      handler: () => {
        if (selectedDemandId.value) {
          emit("load-demand-record", selectedDemandId.value);
          demandRecordPopupVisible.value = true;
        }
      },
    },
  ],
};

// === Formatting ===

// 수량은 toLocaleString 과 같은 표시, 비율은 소수 1자리 + %
const QTY_MASK: MaskConfig = { type: "numeric", pattern: "#,##0.###" };
const RATIO_MASK: MaskConfig = { type: "numeric", pattern: "#,##0.#", suffix: "%" };
const N0_MASK: MaskConfig = { type: "numeric", pattern: "#,##0" };

// "상세 보기" 링크 — 클릭은 cell:click 에서 처리한다
const renderDetailLink = () => {
  const span = document.createElement("span");
  span.className = "detail-link";
  span.textContent = "상세 보기";
  return span;
};

// Row-level conditional formatting (applied to entire row)
const formatRow = (info: any) => {
  if (info.type !== "data") return;
  const item = info.ctx.data as RtfDetailData;
  const isShort = item.rtfRatio < 100;
  info.ctx.rowElement.classList.toggle("ratio-short", isShort);
  info.ctx.rowElement.classList.toggle(
    "ratio-late",
    !isShort && item.rtfRatio === 100 && item.lateRatio > 0,
  );
};

// === Grid Config ===

const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.data),
  formatRow,
  fields: [
    // 기본 컬럼
    { id: "demandID", header: "수요 ID", dataType: "string", width: 100 },
    { id: "custID", header: "고객", dataType: "string", width: 100 },
    { id: "onTimeRatio", header: "On-Time %", dataType: "number", width: 85, align: "right", mask: RATIO_MASK },
    { id: "lateRatio", header: "Late %", dataType: "number", width: 75, align: "right", mask: RATIO_MASK },
    {
      id: "rtfRatio",
      header: "RTF %",
      dataType: "number",
      width: 75,
      align: "right",
      mask: RATIO_MASK,
      // RTF ratio font color for shortage
      cellAttributes: ({ value }: { value: unknown }) =>
        typeof value === "number" && value < 100 ? { class: "ratio-short-font" } : undefined,
    },
    { id: "_short_detail", header: "상세", dataType: "string", width: 72, align: "center", cellRenderer: renderDetailLink },
    { id: "itemGroupID", header: "제품 그룹", dataType: "string", width: 100 },
    { id: "itemID", header: "제품 ID", dataType: "string", width: 100 },
    { id: "itemName", header: "제품명", dataType: "string", width: 120 },
    { id: "dueWeek", header: "납기 주차", dataType: "string", width: 90, align: "center" },
    { id: "dueDate", header: "납기일", dataType: "string", width: 100 },
    { id: "demandQty", header: "수요량", dataType: "number", width: 90, align: "right", mask: QTY_MASK },
    { id: "onTimeQty", header: "On-Time 수량", dataType: "number", width: 100, align: "right", mask: QTY_MASK },
    { id: "lateQty", header: "Late 수량", dataType: "number", width: 90, align: "right", mask: QTY_MASK },
    { id: "rtfQty", header: "RTF 수량", dataType: "number", width: 90, align: "right", mask: QTY_MASK },
    { id: "shortQty", header: "Short 수량", dataType: "number", width: 90, align: "right", mask: QTY_MASK },
    { id: "qtyUom", header: "단위", dataType: "string", width: 60, hidden: true },
    { id: "demand_type", header: "수요 유형", dataType: "string", width: 90, hidden: true },
    { id: "item_type", header: "제품 유형", dataType: "string", width: 90, hidden: true },
    { id: "prod_type", header: "생산 유형", dataType: "string", width: 90, hidden: true },
    { id: "item_size_type", header: "제품 크기", dataType: "string", width: 90, hidden: true },
    { id: "item_spec", header: "제품 사양", dataType: "string", width: 100, hidden: true },
    // 동적 속성 컬럼
    ...props.propColumns.map<FieldDef>((col) => ({
      id: col.columnName,
      header: col.displayText,
      dataType: "string",
      width: 120,
      hidden: true,
    })),
  ],
}));

const shortCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.shortData),
  fields: [
    { id: "shortType", header: "부족 유형", dataType: "string", width: 100, align: "center" },
    { id: "shortCategory", header: "부족 분류", dataType: "string", width: 150 },
    { id: "shortReason", header: "부족 사유", dataType: "string", width: 200 },
    { id: "shortQty", header: "부족 수량", dataType: "number", width: 100, align: "right", mask: N0_MASK },
    { id: "qtyUom", header: "단위", dataType: "string", width: 60, hidden: true },
    { id: "shortDetailInfo", header: "부족 상세 정보", dataType: "string", width: 300 },
    { id: "isbID", header: "ISB 코드", dataType: "string", width: 300 },
    { id: "bomID", header: "BOM 코드", dataType: "string", width: 300 },
  ],
}));

const itemPropsCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.itemPropsData),
  fields: [
    { id: "itemID", header: "제품 ID", dataType: "string", width: 120 },
    { id: "item_type", header: "제품 유형", dataType: "string", width: 100 },
    { id: "itemName", header: "제품명", dataType: "string", width: 150 },
    { id: "item_group", header: "제품 그룹", dataType: "string", width: 100 },
    { id: "item_priority", header: "우선순위", dataType: "string", width: 80 },
    { id: "procurement_type", header: "조달 유형", dataType: "string", width: 100 },
    { id: "prod_type", header: "생산 유형", dataType: "string", width: 100 },
    { id: "item_size", header: "제품 크기", dataType: "string", width: 80 },
    { id: "item_spec", header: "제품 사양", dataType: "string", width: 120 },
  ],
}));

const demandRecordCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.demandRecordData),
  fields: [
    { id: "demandID", header: "수요 ID", dataType: "string", width: 120 },
    { id: "itemID", header: "제품 ID", dataType: "string", width: 120 },
    { id: "site_id", header: "사이트 ID", dataType: "string", width: 100 },
    { id: "buffer_id", header: "버퍼 ID", dataType: "string", width: 100 },
    { id: "dueDate", header: "납기일", dataType: "string", width: 110 },
    { id: "demandQty", header: "수요량", dataType: "number", width: 90, align: "right", mask: N0_MASK },
    { id: "demand_priority", header: "우선순위", dataType: "string", width: 80 },
    { id: "custID", header: "고객 ID", dataType: "string", width: 100 },
    { id: "demand_type", header: "수요 유형", dataType: "string", width: 100 },
    { id: "max_lateness_day", header: "최대 지연일", dataType: "string", width: 90 },
    { id: "max_earliness_day", header: "최대 선행일", dataType: "string", width: 90 },
    { id: "demand_group", header: "수요 그룹", dataType: "string", width: 100 },
  ],
}));

// === Selection ===

function onCellClick(e: any) {
  const dataItem = e?.row as RtfDetailData | undefined;
  if (!dataItem) return;

  selectedDemandId.value = dataItem.demandID ?? "";
  selectedItemId.value = dataItem.itemID ?? "";

  if (dataItem.demandID) {
    emit("demand-selected", dataItem.demandID);
  }

  // "상세 보기" clickable link
  if (e.columnId === "_short_detail" && dataItem.demandID) {
    emit("load-short", dataItem.demandID);
    shortPopupVisible.value = true;
  }
}

// 우클릭한 행을 컨텍스트 메뉴 대상으로 잡는다
function onContextMenu(e: any) {
  if (e?.area !== "cell" || !e.rowData) return;
  selectedDemandId.value = e.rowData.demandID ?? "";
  selectedItemId.value = e.rowData.itemID ?? "";
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

:deep(.detail-link) {
  color: #4568e0;
  text-decoration: underline;
  cursor: pointer;
}

// Short (RTF < 100%) — light red background
:deep(.ratio-short .ps-cell) {
  background-color: #f6d5d5 !important;
}

// Late (RTF = 100% & Late > 0) — light orange background
:deep(.ratio-late .ps-cell) {
  background-color: #fde6c8 !important;
}

// Red font for shortage ratio
:deep(.ratio-short-font) {
  color: #dc5a5a !important;
}
</style>
