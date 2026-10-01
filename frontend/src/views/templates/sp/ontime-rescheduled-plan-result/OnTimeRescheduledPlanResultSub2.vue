<template>
  <div class="rtf-report-sub2-wrapper">
    <!-- Detail Grid -->
    <MozGrid
      name="onTimeReplanDetail"
      :coreConfig="coreConfig"
      height="100%"
      :loading="loading"
      :use-tool-box="false"
      :use-sort="false"
      class="rtf-report-sub2"
      :contextMenuConfig="contextMenuConfig"
      @ready="onGridReady"
      @data:loaded="selectFirstRow"
      @cell:click="onCellClick"
    />

    <!-- Short Detail Popup (원본: BomMapInterface + Short Grid SplitPane) -->
    <Popup
      :width="popupWidth"
      :height="popupHeight"
      v-model:visible="shortPopupVisible"
      :title="t('text-short-reason-detail-view')"
      preset="close"
      :onCancel="() => (shortPopupVisible = false)"
      :maxWidth="popupWidth"
      :maxHeight="popupHeight"
      :resizeable="true"
      :style="{ minWidth: '650px', minHeight: '400px' }"
      :useVShow="false"
    >
      <div class="bom-map-popup-container">
        <SplitPane horizontal style="max-width: 100%">
          <!-- 상단 70%: BomMapInterface -->
          <Pane size="70%" max-size="90%">
            <BomMapInterface
              v-if="bomMapData.length"
              :bomNetworkInfos="bomMapData"
              :demandInfos="demandInfoData"
              :shortLogs="(bomMapShortLogs as any)"
              :initKey="demandInfoData?.item_id"
              :planCycleData="{
                planVer,
                planCycleID: '',
                projectID: getProjectId(),
                fromDate: '',
                toDate: '',
                demandID: currentPopupDemandID,
              }"
              userID=""
            />
            <div v-else class="grid-empty">
              <EmptyState :is-read-only="true" />
            </div>
          </Pane>
          <!-- 하단 30%: Short Reason Grid -->
          <Pane size="30%" max-size="90%">
            <div class="grid-sort-reason">
              <MozGrid
                name="onTimeReplanShortDetail"
                :coreConfig="shortCoreConfig"
                height="100%"
                :use-tool-box="false"
                :use-sort="false"
                :loading="shortLoading"
                :contextMenuConfig="contextMenuConfig"
              />
            </div>
          </Pane>
        </SplitPane>
      </div>
    </Popup>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, computed } from "vue";
import { useTranslation } from "i18next-vue";
import { MozGrid } from "@vmscloud/moz-ui-grid-vue";
import type {
  IContextMenuConfig,
  MaskConfig,
  MozGridCoreProps,
  PureSheet,
} from "@vmscloud/moz-ui-grid-vue";
import { EmptyState, Pane, Popup, SplitPane } from "@vmscloud/moz-ui-components-vue";
import BomMapInterface from "@/views/templates/sp/new-rtf-report/components/bom-map/BomMapInterface.vue";
import { getProjectId } from "@/api/client";
import { GRID_ROW_KEY, withRowKey } from "./onTimeRescheduledPlanResult";
import type { ReplanRtfDetail, ShortData } from "./onTimeRescheduledPlanResult";

const { t } = useTranslation();

// === Props & Emits ===

interface Props {
  data: ReplanRtfDetail[];
  loading: boolean;
  planVer: string;
  uomType: string;
  shortData: ShortData[];
  shortLoading?: boolean;
  bomMapData?: any[];
  bomMapShortLogs?: any[];
  demandInfoData?: any;
}

const props = withDefaults(defineProps<Props>(), {
  bomMapData: () => [],
  bomMapShortLogs: () => [],
  demandInfoData: () => ({}),
});

const emit = defineEmits<{
  (e: "demand-selected", demandID: string): void;
  (e: "load-short", demandID: string): void;
}>();

// === Popup size (브라우저 80% x 90%) ===
const windowWidth = ref(window.innerWidth);
const windowHeight = ref(window.innerHeight);
const popupWidth = computed(() => Math.floor(windowWidth.value * 0.8));
const popupHeight = computed(() => Math.floor(windowHeight.value * 0.9));
const updateWindowSize = () => {
  windowWidth.value = window.innerWidth;
  windowHeight.value = window.innerHeight;
};
onMounted(() => window.addEventListener("resize", updateWindowSize));
onBeforeUnmount(() => window.removeEventListener("resize", updateWindowSize));

// === Local State ===

let grid: PureSheet | null = null;
const shortPopupVisible = ref(false);
const currentPopupDemandID = ref("");
const pendingFirstRowSelect = ref(false);

const contextMenuConfig: IContextMenuConfig = {
  useFilter: true,
  useExportExcel: true,
};

// === Ratio Formatting ===

const formatNumber = (num: number) => {
  const truncated = Number(num.toFixed(1));
  if (truncated % 1 === 0)
    return truncated.toLocaleString("en-US", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
  return truncated.toLocaleString("en-US", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
};

const QTY_MASK: MaskConfig = { type: "numeric", pattern: "#,##0.###" };
const RATIO_MASK: MaskConfig = {
  type: "function",
  formatter: (value: unknown) =>
    typeof value === "number" ? `${formatNumber(value)}%` : "",
};

// ratio_rtf / rtfQty 헤더 아래 보조 문구
const renderSubTextHeader = ({ header }: { header: string }) => {
  const headerDiv = document.createElement("div");
  headerDiv.style.display = "flex";
  headerDiv.style.flexDirection = "column";
  headerDiv.style.alignItems = "center";
  headerDiv.style.justifyContent = "center";
  headerDiv.style.height = "100%";

  const mainHeader = document.createElement("div");
  mainHeader.textContent = header;
  mainHeader.classList.add("rtf-ratio-main-header");

  const subHeader = document.createElement("div");
  subHeader.textContent = t("text-isu_early_ontime_late");
  subHeader.classList.add("rtf-ratio-sub-header");

  headerDiv.appendChild(mainHeader);
  headerDiv.appendChild(subHeader);
  return headerDiv;
};

// "상세 보기" 링크 — 클릭은 cell:click 에서 처리한다
const renderDetailLink = () => {
  const span = document.createElement("span");
  span.className = "detail-link";
  span.textContent = t("text-view_detail");
  return span;
};

// Short / Late highlighting (행 전체)
const formatRow = (info: any) => {
  if (info.type !== "data") return;
  const item = info.ctx.data as ReplanRtfDetail;
  info.ctx.rowElement.classList.toggle("ratio-short", item.ratio_rtf < 100);
  info.ctx.rowElement.classList.toggle(
    "ratio-late",
    item.ratio_rtf === 100 && item.ratio_late > 0,
  );
};

// === Grid Config ===

const coreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.data),
  formatRow,
  fields: [
    { id: "itemID", header: t("text-item_id"), dataType: "string" },
    { id: "demandID", header: t("text-isu_mo_id"), dataType: "string", width: 80, align: "left" },
    { id: "showDetailCol", header: t("text-simple_short_reason"), dataType: "string", width: 80, cellRenderer: renderDetailLink },
    { id: "custID", header: t("text-cust_name"), dataType: "string", width: 150 },
    {
      id: "ratio_rtf",
      header: t("text-isu_otd_expected_rate"),
      dataType: "number",
      width: 110,
      align: "right",
      mask: RATIO_MASK,
      headerRenderer: renderSubTextHeader,
      // Short font color for ratio_rtf
      cellAttributes: ({ value }: { value: unknown }) =>
        typeof value === "number" && value < 100 ? { class: "ratio-short-font" } : undefined,
    },
    { id: "rtfQty", header: t("text-isu_otd_expected_qty"), dataType: "number", width: 110, align: "right", mask: QTY_MASK, headerRenderer: renderSubTextHeader },
    { id: "ratio_early", header: t("text-isu_early"), dataType: "number", width: 80, align: "right", mask: RATIO_MASK },
    { id: "ratio_ontime", header: t("text-isu_ontime"), dataType: "number", width: 80, align: "right", mask: RATIO_MASK },
    { id: "ratio_late", header: t("text-isu_late"), dataType: "number", width: 80, align: "right", mask: RATIO_MASK },
    { id: "ratio_short", header: t("text-isu_short"), dataType: "number", width: 80, align: "right", mask: RATIO_MASK },
    { id: "earlyQty", header: t("text-isu_early"), dataType: "number", width: 80, align: "right", mask: QTY_MASK },
    { id: "onTimeQty", header: t("text-isu_ontime"), dataType: "number", width: 80, align: "right", mask: QTY_MASK },
    { id: "lateQty", header: t("text-isu_late"), dataType: "number", width: 80, align: "right", mask: QTY_MASK },
    { id: "shortQty", header: t("text-isu_short"), dataType: "number", width: 80, align: "right", mask: QTY_MASK },
  ],
  columnGroups: [
    {
      id: "rtfRate",
      header: t("text-isu_rtf_rate"),
      children: ["ratio_early", "ratio_ontime", "ratio_late", "ratio_short"],
    },
    {
      id: "prodQty",
      header: t("text-isu_prod_qty"),
      children: ["earlyQty", "onTimeQty", "lateQty", "shortQty"],
    },
  ],
}));

const shortCoreConfig = computed<MozGridCoreProps>(() => ({
  mode: "flat",
  keyFields: [GRID_ROW_KEY],
  data: withRowKey(props.bomMapShortLogs),
  fields: [
    { id: "short_type", header: t("text-short_type"), dataType: "string", width: 100, align: "center" },
    { id: "short_category", header: t("text-short_category"), dataType: "string", width: 150 },
    { id: "short_reason", header: t("text-short_reason"), dataType: "string", width: 200 },
    { id: "short_qty", header: t("text-short_qty"), dataType: "number", width: 100, align: "right", mask: { type: "numeric", pattern: "#,##0" } },
    { id: "qty_uom", header: t("text-qty_uom"), dataType: "string", width: 80, hidden: true },
    { id: "short_detail_info", header: t("text-short_detail_info"), dataType: "string", width: 300 },
    { id: "isb_id", header: t("text-isb_id"), dataType: "string", width: 300 },
    { id: "bom_id", header: t("text-bom_id"), dataType: "string", width: 300 },
    { id: "routing_id", header: t("text-routing_id"), dataType: "string", width: 100, hidden: true },
    { id: "oper_id", header: t("text-oper_id"), dataType: "string", width: 100, hidden: true },
    { id: "res_id", header: t("text-res_id"), dataType: "string", width: 100, hidden: true },
  ],
}));

// === Grid Initialization ===

const onGridReady = (sheet: PureSheet) => {
  grid = sheet;
};

// Auto-select first row when data changes
watch(
  () => props.data,
  (newData) => {
    pendingFirstRowSelect.value = !!newData && newData.length > 0;
  },
);

function selectFirstRow() {
  if (!pendingFirstRowSelect.value || !grid) return;
  pendingFirstRowSelect.value = false;

  const firstItem = props.data[0];
  grid.cells.selectCellsByViewIndices([{ viewIndex: 0, columnId: "itemID" }]);
  if (firstItem?.demandID) {
    emit("demand-selected", firstItem.demandID);
  }
}

// === Selection ===

const onCellClick = (e: any) => {
  const item = e?.row as ReplanRtfDetail | undefined;
  if (!item) return;

  if (item.demandID) {
    emit("demand-selected", item.demandID);
  }

  if (e.columnId === "showDetailCol") {
    currentPopupDemandID.value = item.demandID;
    emit("load-short", item.demandID);
    shortPopupVisible.value = true;
  }
};
</script>

<style lang="scss">
.rtf-report-sub2-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.bom-map-popup-container {
  height: 100%;
  width: 100%;

  .bom-map-outer-wrapper {
    border: 1px solid #bbc6d9;
    border-bottom: none;

    &:before {
      border: none !important;
    }
  }

  .grid-sort-reason {
    height: 100%;
  }

  .grid-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
}

.rtf-report-sub2 {
  .rtf-ratio-main-header {
    font-weight: 500;
    margin-bottom: 2px;
  }

  .rtf-ratio-sub-header {
    font-size: 0.65rem;
    color: #6b7280;
    font-weight: 400;
    white-space: nowrap;
  }

  .detail-link {
    cursor: pointer;
    color: #4568e0;
    text-decoration: underline;
  }
}

// Row coloring for short/late
.rtf-report-sub2 {
  .ps-row.ratio-short .ps-cell {
    background-color: #f6d5d5 !important;
  }

  .ps-row.ratio-late .ps-cell {
    background-color: #fde6c8 !important;
  }

  .ps-row.ratio-short:hover .ps-cell,
  .ps-row.ratio-late:hover .ps-cell {
    background-color: #d4cde8 !important;
  }

  .ratio-short-font {
    color: #dc5a5a !important;
  }
}
</style>
