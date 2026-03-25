<template>
  <Popup
    class="dashboard-setting-detail-popup"
    title="위젯 상세 설정"
    :visible="true"
    preset="save"
    :width="1036"
    :height="620"
    :on-confirm="handleSave"
    :on-cancel="() => emit('close')"
  >
    <Tab
      vertical
      v-model="activeTab"
      :itemSource="itemSource"
      class="setting-tab"
    >
      <!-- Tab 1: 당월 예상 납기 준수율 (RTF Report) -->
      <template #rtfReport>
        <div class="tab-body-content rtf-report-tab">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">수량 UOM 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                RTF Report에 표시할 수량 UOM을 선택합니다.
              </div>
              <Select
                :key-prop="'value'"
                :display-prop="'label'"
                :items-source="uomOptions"
                v-model="rtfUomType"
              />
            </div>
          </div>
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">집계 기준 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                RTF 집계 기준을 LOT 또는 DEMAND 단위로 설정합니다.
              </div>
              <Radio
                :valueExpr="'value'"
                :display-expr="'label'"
                :items-source="[
                  { key: 'Lot', value: 'LOT', label: 'LOT' },
                  { key: 'Demand', value: 'DEMAND', label: 'DEMAND' },
                ]"
                v-model="rtfStd"
              />
            </div>
          </div>
          <ExtendFlexGrid
            style="flex: 1"
            :alternatingRowStep="0"
            class="rtf-summary-grid"
            :itemsSource="matrixRows"
            :use-tool-box="false"
            :use-extend-footer="false"
            :useContextMenu="false"
            :initialized="onRtfGridInitialized"
            :formatItem="rtfGridFormatItem"
          >
            <WjFlexGridColumn
              binding="category"
              header="분류"
              :width="125"
              :isReadOnly="true"
              align="center"
            />
            <WjFlexGridColumn
              binding="planType"
              header="계획 유형"
              :width="130"
              :isReadOnly="true"
              align="center"
            />
            <WjFlexGridColumn
              binding="apply_early"
              header="Early"
              :width="120"
              align="center"
            />
            <WjFlexGridColumn
              binding="apply_on_time"
              header="On-time"
              :width="120"
              align="center"
            />
            <WjFlexGridColumn
              binding="apply_late"
              header="Late"
              :width="120"
              align="center"
            />
            <WjFlexGridColumn
              binding="apply_short"
              header="Short"
              :width="120"
              align="center"
            />
            <WjFlexGridColumn
              binding="apply_excluded"
              header="제외"
              :width="120"
              align="center"
            />
          </ExtendFlexGrid>
        </div>
      </template>

      <!-- Tab 2: 생산 실적의 납기 준수율 -->
      <template #prodPerformance>
        <div class="tab-body-content rtf-report-tab">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">수량 UOM 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                생산 실적 RTF Report에 표시할 수량 UOM을 선택합니다.
              </div>
              <Select
                :key-prop="'value'"
                :display-prop="'label'"
                :items-source="uomOptions"
                v-model="actualRtfUomType"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- Tab 3: 재계획의 납기 준수율 -->
      <template #rePlanPerformance>
        <div class="tab-body-content rtf-report-tab">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">수량 UOM 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                재계획 RTF Report에 표시할 수량 UOM을 선택합니다.
              </div>
              <Select
                :key-prop="'value'"
                :display-prop="'label'"
                :items-source="uomOptions"
                v-model="planRtfUomType"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- Tab 4: 월초 계획 vs. 실적 -->
      <template #onTimeDelivery>
        <div class="tab-body-content">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">수량 UOM 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                월초 계획 vs. 실적 비교에 표시할 수량 UOM을 선택합니다.
              </div>
              <Select
                :key-prop="'value'"
                :display-prop="'label'"
                :items-source="uomOptions"
                v-model="frozenActualUomType"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- Tab 5: 공정 그룹별 부하율(향후 30일) -->
      <template #stockInPlan>
        <div class="tab-body-content oper-group-tab">
          <div class="setting-popup-section">
            <div class="oper-group-text-wrapper">
              <div class="setting-popup-sub-title">
                공정 그룹 표시 여부 설정
              </div>
              <div class="setting-popup-sub-desc">
                표시할 공정 그룹을 선택하고 순서를 변경할 수 있습니다.
              </div>
            </div>
            <div class="oper-group-selection-container">
              <div>
                <div class="setting-popup-sub-title oper-group-text-title">
                  선택 가능 공정 그룹
                </div>
                <div class="setting-popup-sub-desc">
                  목록에 추가할 그룹을 선택하세요.
                </div>
                <div class="oper-group-selection-list">
                  <div
                    v-if="operGroupSourceDisplay.length > 0"
                    class="oper-group-selection-list-item"
                    v-for="value in operGroupSourceDisplay"
                    :key="value"
                  >
                    <div>{{ value }}</div>
                    <div
                      class="oper-group-selection-list-item-add"
                      @click="addOperGroupOption(value)"
                    >
                      추가
                    </div>
                  </div>
                  <div class="container-body-wrapper body-wrapper-empty" v-else>
                    데이터 없음
                  </div>
                </div>
              </div>
              <div>
                <div class="oper-group-option-list-wrapper">
                  <div class="oper-group-option-text-wrapper">
                    <div class="setting-popup-sub-title oper-group-text-title">
                      선택된 그룹
                    </div>
                    <div class="setting-popup-sub-desc">순서 변경 가능</div>
                  </div>
                  <div class="oper-group-option-list-arrow-wrapper">
                    <button
                      @click="moveOperGroupOptionDown"
                      :class="{
                        'oper-group-option-list-arrow': true,
                        'oper-group-option-list-arrow-disabled':
                          !selectedOperGroupItem,
                      }"
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 14 14"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M11.5 7.5L7.17678 11.8232C7.07915 11.9209 6.92085 11.9209 6.82322 11.8232L2.5 7.5"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M7 10.5V2"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                        />
                      </svg>
                    </button>
                    <button
                      @click="moveOperGroupOptionUp"
                      :class="{
                        'oper-group-option-list-arrow': true,
                        'oper-group-option-list-arrow-disabled':
                          !selectedOperGroupItem,
                      }"
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 14 14"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M11.5 6.498L7.17678 2.17479C7.07915 2.07716 6.92085 2.07716 6.82322 2.17479L2.5 6.498"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M7 3.5V12"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
                <div class="oper-group-option-list">
                  <div
                    v-if="selectedOperGroups.length > 0"
                    class="oper-group-option-list-item"
                    v-for="(group, _idx) in selectedOperGroups"
                    :key="group"
                  >
                    <div
                      :class="{
                        'oper-group-option-list-item-category': true,
                        'oper-group-option-list-item-category-selected':
                          selectedOperGroupItem === group,
                      }"
                      @click="selectOperGroupItem(group)"
                    >
                      <div class="oper-group-option-list-item-category-text">
                        {{ group }}
                      </div>
                      <div
                        class="close-button"
                        @click.stop="removeOperGroupOption(group)"
                      >
                        <svg
                          width="10"
                          height="10"
                          viewBox="0 0 10 10"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d="M1 1L9 9M9 1L1 9"
                            stroke="#4568e0"
                            stroke-width="1.5"
                            stroke-linecap="round"
                          />
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div class="container-body-wrapper body-wrapper-empty" v-else>
                    데이터 없음
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Tab 6: 설비 가동 현황 -->
      <template #resGroupSummary>
        <div class="tab-body-content">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">수량 UOM 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                설비 가동 현황에 표시할 수량 UOM을 선택합니다.
              </div>
              <Select
                :key-prop="'value'"
                :display-prop="'label'"
                :items-source="uomOptions"
                v-model="operCapaUomType"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- Tab 7: 확정 계획 vs. 재수립 계획 -->
      <template #rePlanDelivery>
        <div class="tab-body-content">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">수량 UOM 설정</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                확정 계획 vs. 재수립 계획 비교에 표시할 수량 UOM을 선택합니다.
              </div>
              <Select
                :key-prop="'value'"
                :display-prop="'label'"
                :items-source="uomOptions"
                v-model="frozenPlanUomType"
              />
            </div>
          </div>
        </div>
      </template>
    </Tab>
  </Popup>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { Popup, Radio, Select, Tab } from "@vmscloud/moz-ui-components";
import { ExtendFlexGrid } from "@vmscloud/moz-wijmo-grid";
import { WjFlexGridColumn } from "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid";
import {
  type FlexGrid,
  CellType,
  SelectionMode,
  AllowMerging,
} from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import type { FormatItemEventArgs } from "@vmscloud/moz-wijmo-grid/wijmo.grid";
import { fetchSettings, saveSettings } from "../planDashboard";

const props = defineProps<{
  planVer: string;
  userId: string;
}>();

const emit = defineEmits<{
  close: [];
  saved: [];
}>();

// UOM options shared across tabs
const uomOptions = [
  { value: "DEFAULT", label: "DEFAULT" },
  { value: "CONVERSION", label: "CONVERSION" },
];

// Tab itemSource for vertical Tab component (matches original format)
const itemSource = [
  { id: "rtfReport", text: "당월 예상 납기 준수율" },
  { id: "prodPerformance", text: "생산 실적의 납기 준수율" },
  { id: "rePlanPerformance", text: "재계획의 납기 준수율" },
  { id: "onTimeDelivery", text: "월초 계획 vs. 실적" },
  { id: "stockInPlan", text: "공정 그룹별 부하율(향후 30일)" },
  { id: "resGroupSummary", text: "설비 가동 현황" },
  { id: "rePlanDelivery", text: "확정 계획 vs. 재수립 계획" },
];

const activeTab = ref("rtfReport");

// Tab 1: RTF settings
const rtfStd = ref("LOT");
const rtfUomType = ref("DEFAULT");

interface MatrixRow {
  category: string;
  planType: string;
  value: string;
}

const matrixRows = reactive<MatrixRow[]>([
  { category: "수요 충족", planType: "EARLY", value: "EARLY" },
  { category: "수요 충족", planType: "ON_TIME", value: "ON_TIME" },
  { category: "수요 충족", planType: "LATE", value: "LATE" },
  { category: "수요 미충족", planType: "SHORT_LATE", value: "SHORT" },
  { category: "수요 미충족", planType: "SHORT_ON_TIME", value: "SHORT" },
  { category: "수요 미충족", planType: "SHORT_EARLY", value: "SHORT" },
  { category: "수요 미충족", planType: "FULL_SHORT", value: "SHORT" },
  { category: "수요 없음", planType: "NO_DEMAND", value: "EXCLUDED" },
  { category: "잔여", planType: "UPCOMING", value: "EXCLUDED" },
  { category: "기타", planType: "ETC", value: "EXCLUDED" },
]);

// Tab 2-4, 6-7: UOM type selectors
const actualRtfUomType = ref("DEFAULT");
const planRtfUomType = ref("DEFAULT");
const frozenActualUomType = ref("DEFAULT");
const frozenPlanUomType = ref("DEFAULT");
const operCapaUomType = ref("DEFAULT");

// Tab 5: Oper group selection
const operGroupList = ref<string[]>([]);
const selectedOperGroups = ref<string[]>([]);
const selectedOperGroupItem = ref("");

// Computed: display only groups not already selected
const operGroupSourceDisplay = computed(() =>
  operGroupList.value.filter(
    (group) => !selectedOperGroups.value.includes(group),
  ),
);

const addOperGroupOption = (category: string) => {
  selectedOperGroups.value.push(category);
};

const removeOperGroupOption = (category: string) => {
  selectedOperGroups.value = selectedOperGroups.value.filter(
    (g) => g !== category,
  );
  if (category === selectedOperGroupItem.value) {
    selectedOperGroupItem.value = "";
  }
};

const selectOperGroupItem = (category: string) => {
  selectedOperGroupItem.value = category;
};

const moveOperGroupOptionUp = () => {
  if (!selectedOperGroupItem.value) return;
  const idx = selectedOperGroups.value.indexOf(selectedOperGroupItem.value);
  if (idx <= 0) return;
  const arr = [...selectedOperGroups.value];
  [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]];
  selectedOperGroups.value = arr;
};

const moveOperGroupOptionDown = () => {
  if (!selectedOperGroupItem.value) return;
  const idx = selectedOperGroups.value.indexOf(selectedOperGroupItem.value);
  if (idx < 0 || idx >= selectedOperGroups.value.length - 1) return;
  const arr = [...selectedOperGroups.value];
  [arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]];
  selectedOperGroups.value = arr;
};

// Track original values for change detection
// === RTF Grid: formatItem + initialized (원본 동일) ===

const radioColumns = [
  "apply_early",
  "apply_on_time",
  "apply_late",
  "apply_short",
  "apply_excluded",
];
const valueMap: Record<string, string> = {
  apply_early: "EARLY",
  apply_on_time: "ON_TIME",
  apply_late: "LATE",
  apply_short: "SHORT",
  apply_excluded: "EXCLUDED",
};

const rtfGridFormatItem = (s: FlexGrid, e: FormatItemEventArgs) => {
  if (e.panel.cellType === CellType.Cell) {
    const col = s.columns[e.col];
    const binding = col?.binding || "";
    if (radioColumns.includes(binding)) {
      const row = s.rows[e.row].dataItem;
      const checked = row.value === valueMap[binding];
      e.cell.innerHTML = `
        <label class="custom-radio">
          <input type="radio" name="apply-radio-${row.category}-${row.planType}" ${checked ? "checked" : ""} />
          <span></span>
        </label>
      `;
      e.cell.querySelector("input")?.addEventListener("change", () => {
        // 해당 행의 value를 변경
        row.value = valueMap[binding];
        // 그리드 갱신
        s.invalidate();
      });
    }
  }
  // planType 컬럼 오른쪽 경계선
  if (s.columns[e.col]?.binding === "planType") {
    e.cell.classList.add("rtf-grid-border-right");
  }
};

const onRtfGridInitialized = (flexGrid: FlexGrid) => {
  flexGrid.selectionMode = SelectionMode.None;
  flexGrid.allowMerging = AllowMerging.Cells;
  flexGrid.columns[0].allowMerging = true;
};

// === 원본 설정 추적 ===

const originalSettings = ref<Record<string, string>>({});

// Load settings from server
onMounted(async () => {
  if (!props.userId) return;
  try {
    const res = await fetchSettings(props.userId, "/pa/PlanDashboard2");
    if (res.success && res.data) {
      // 백엔드 응답: { success, data: { widgetId: widgetValue, ... } } (object map)
      const settingsMap: Record<string, string> =
        typeof res.data === "object" && !Array.isArray(res.data)
          ? (res.data as Record<string, string>)
          : {};

      // Apply loaded settings
      if (settingsMap["rtfStd"]) rtfStd.value = settingsMap["rtfStd"];
      if (settingsMap["rtfUomType"])
        rtfUomType.value = settingsMap["rtfUomType"];
      if (settingsMap["actualRtfUomType"])
        actualRtfUomType.value = settingsMap["actualRtfUomType"];
      if (settingsMap["planRtfUomType"])
        planRtfUomType.value = settingsMap["planRtfUomType"];
      if (settingsMap["frozenActualUomType"])
        frozenActualUomType.value = settingsMap["frozenActualUomType"];
      if (settingsMap["frozenPlanUomType"])
        frozenPlanUomType.value = settingsMap["frozenPlanUomType"];
      if (settingsMap["operCapaUomType"])
        operCapaUomType.value = settingsMap["operCapaUomType"];

      if (settingsMap["rtfMatrix"]) {
        try {
          const parsed = JSON.parse(settingsMap["rtfMatrix"]);
          if (Array.isArray(parsed)) {
            parsed.forEach((item: { idx: number; value: string }) => {
              if (item.idx >= 0 && item.idx < matrixRows.length) {
                matrixRows[item.idx].value = item.value;
              }
            });
          }
        } catch {
          /* ignore parse errors */
        }
      }

      if (settingsMap["operGroupList"]) {
        try {
          operGroupList.value = JSON.parse(settingsMap["operGroupList"]);
        } catch {
          /* ignore */
        }
      }

      if (settingsMap["selectedOperGroups"]) {
        try {
          selectedOperGroups.value = JSON.parse(
            settingsMap["selectedOperGroups"],
          );
        } catch {
          /* ignore */
        }
      }

      // Store original for change detection
      originalSettings.value = { ...settingsMap };
    }
  } catch (e) {
    console.error("설정 로드 오류:", e);
  }
});

/** Build current settings map */
function getCurrentSettings(): Array<{
  widgetId: string;
  widgetValue: string;
}> {
  return [
    { widgetId: "rtfStd", widgetValue: rtfStd.value },
    { widgetId: "rtfUomType", widgetValue: rtfUomType.value },
    { widgetId: "actualRtfUomType", widgetValue: actualRtfUomType.value },
    { widgetId: "planRtfUomType", widgetValue: planRtfUomType.value },
    { widgetId: "frozenActualUomType", widgetValue: frozenActualUomType.value },
    { widgetId: "frozenPlanUomType", widgetValue: frozenPlanUomType.value },
    { widgetId: "operCapaUomType", widgetValue: operCapaUomType.value },
    {
      widgetId: "rtfMatrix",
      widgetValue: JSON.stringify(
        matrixRows.map((row, idx) => ({ idx, value: row.value })),
      ),
    },
    {
      widgetId: "selectedOperGroups",
      widgetValue: JSON.stringify(selectedOperGroups.value),
    },
  ];
}

// Save changed settings only — used as on-before-confirm callback
async function handleSave() {
  if (!props.userId) return;

  const menuId = "/pa/PlanDashboard2";
  const allSettings = getCurrentSettings();

  // Filter to only changed widgets
  const changedSettings = allSettings.filter(
    (s) => s.widgetValue !== originalSettings.value[s.widgetId],
  );

  try {
    for (const setting of changedSettings) {
      await saveSettings({
        userId: props.userId,
        menuId,
        widgetId: setting.widgetId,
        widgetValue: setting.widgetValue,
      });
    }
    emit("saved");
    emit("close");
  } catch (e) {
    console.error("설정 저장 오류:", e);
  }
}
</script>

<style lang="scss">
.dashboard-setting-detail-popup {
  .moz-tabs-container {
    .moz-tabs {
      width: 280px !important;
    }
  }

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
      min-width: 152px !important;

      .tab-label {
        text-overflow: clip !important;
      }
    }

    .tab-panel.active {
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
      }

      .setting-popup-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 20px;

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

  .oper-group-tab {
    .oper-group-text-wrapper {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .oper-group-selection-container {
      display: flex;
      align-items: start;
      gap: 10px;
      flex: 1;
      margin: 12px 0 0 0;

      .oper-group-text-title {
        margin-bottom: 4px;
      }
      .oper-group-selection-list {
        margin: 10px 0 0 0;
        overflow-y: auto;
        height: 350px;
        width: 246px;
        border-radius: 4px;
        border: 1px solid #e1e3f0;
        padding: 11px 10px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        box-sizing: border-box;

        .body-wrapper-empty {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          color: #6a7184;
          font-size: 13px;
          font-weight: 500;
        }

        .oper-group-selection-list-item {
          display: flex;
          justify-content: space-between;
          align-items: center;

          border-radius: 4px;
          height: 28px;
          padding: 8px 10px;
          outline: 1px solid #cad4e5;
          font-size: 13px;

          box-sizing: border-box;

          .oper-group-selection-list-item-add {
            color: #4568e0;
            cursor: pointer;
          }
        }
      }

      .oper-group-option-list-wrapper {
        display: flex;
        gap: 8px;
        align-items: flex-end;
        justify-content: space-between;

        .oper-group-option-list-arrow-wrapper {
          display: flex;
          gap: 8px;
          align-items: center;
          justify-content: center;
          .oper-group-option-list-arrow {
            all: unset;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 4px;
            box-sizing: border-box;
            outline: 1px solid #bac6d4;
            color: #8998b5;
            background: #ffffff;
            cursor: pointer;
            &:hover {
              outline: 1px solid #4568e0;
              color: #8998b5;
            }
          }
          .oper-group-option-list-arrow-disabled {
            cursor: not-allowed;
            outline: 1px solid #a7b1bc;
            color: #a7b1bc;
            &:hover {
              outline: 1px solid #a7b1bc;
              color: #a7b1bc;
            }
          }
        }
      }

      .oper-group-option-list {
        border-radius: 4px;
        border: 1px dashed #4568e0;
        background: #f4f4f7;
        padding: 10px;
        margin: 10px 0 0 0;
        height: 350px;
        width: 336px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        gap: 6px;
        overflow-y: auto;

        .body-wrapper-empty {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          font-size: 13px;
          color: #6a7184;
          font-weight: 500;
        }

        .oper-group-option-list-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-radius: 4px;
          gap: 6px;
          font-size: 13px;
          .oper-group-option-list-item-category {
            border-radius: 4px;
            outline: 1px solid #4568e066;
            background: #4568e017;
            box-sizing: border-box;
            height: 28px;
            padding: 0 10px;
            width: 198px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            .oper-group-option-list-item-category-text {
              color: #4568e0;
            }
            .close-button {
              cursor: pointer;
              width: 14px;
              height: 14px;
              display: flex;
              align-items: center;
              justify-content: center;
            }
          }
          .oper-group-option-list-item-category-selected {
            outline: 1px solid #4568e0;
            background: #4568e029;
          }
        }
      }
    }
  }
}

.custom-radio {
  display: inline-flex;
  align-items: center;
  cursor: pointer;

  input[type="radio"] {
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

  input[type="radio"]:checked + span {
    background: #4568e0;
    border: none;
  }

  input[type="radio"]:checked + span::after {
    content: "";
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
</style>
