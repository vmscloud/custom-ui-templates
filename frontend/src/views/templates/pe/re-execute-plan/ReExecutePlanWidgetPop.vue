<template>
  <Popup
    class="re-execute-plan-widget-setting-popup"
    :title="widgetSettingTitle"
    v-model:visible="visibleModel"
    preset="save"
    :width="1037"
    :height="700"
    :on-before-confirm="onConfirmPopup"
    @open="onLoadPopup"
  >
    <Tab vertical v-model="settingPopupCurrentTab" :itemSource="itemSource" class="setting-tab">
      <template #reExecutePlan>
        <div class="tab-body-content rtf-report-tab">
          <div class="setting-popup-section">
            <div class="setting-popup-sub-title">{{ t('text-setting_produce_plan_aggr_standard') }}</div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                {{ t('desc-set_analysis_view_point') }}
              </div>
              <div>
                <MultiSelect
                  v-model="viewPointWidget"
                  :headerFormat="'{count:n0} ITEMS'"
                  :useSelectAll="true"
                  :useFilter="true"
                  :itemsSource="viewPointSource"
                  keyProp="value"
                  displayProp="label"
                  @close="
                    () => {
                      if (!viewPointWidget?.length) {
                        viewPointWidget = viewPointSource.map((item: any) => item.value);
                      }
                    }
                  "
                />
              </div>
            </div>
            <div class="setting-popup-sub-section">
              <div class="setting-popup-sub-desc">
                {{ t('desc-set_detailed_break_down') }}
              </div>
              <div>
                <Select
                  v-model="breakdownWidget"
                  :headerFormat="'{count:n0} ITEMS'"
                  :useSelectAll="true"
                  :useFilter="true"
                  :itemsSource="breakdownSource"
                  keyProp="value"
                  displayProp="label"
                  :use-obj-binding="true"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </Tab>
  </Popup>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useTranslation } from "i18next-vue";
import { MultiSelect, Popup, Select, Tab } from "@vmscloud/moz-ui-components";
import { api, getProjectId } from "@/api/client";

// Widget settings API (inline — not exported from composable)
const saveWidgetSettings = (params: any) =>
  api.post(`/api/custom/backend/${getProjectId()}/re-execute-plan/save-widget`, params);
const fetchWidgetSettings = (userId: string, menuId: string) =>
  api.post(`/api/custom/backend/${getProjectId()}/re-execute-plan/get-widget`, { user_id: userId, menu_id: menuId });

type PropsType = {
  visible: boolean;
  initialTab?: "reExecutePlan";
  // Menu info (replaces store dependencies)
  parentMenuName?: string;
  menuName?: string;
  // User info
  userId?: string;
  // View point / breakdown sources
  viewPointSource?: { label: string; value: string }[];
  breakdownSource?: { label: string; value: string }[];
  // Initial values
  initialViewPoint?: string[];
  initialBreakdown?: { label: string; value: string } | null;
};

const props = withDefaults(defineProps<PropsType>(), {
  initialTab: "reExecutePlan",
  parentMenuName: "",
  menuName: "",
  userId: "",
  viewPointSource: () => [
    { label: "Customer", value: "cust" },
    { label: "Item Group", value: "itemGroup" },
    { label: "Region", value: "region" },
    { label: "Demand Type", value: "demandType" },
  ],
  breakdownSource: () => [
    { label: "OPER", value: "OPER" },
    { label: "OPER GROUP", value: "OPERGROUP" },
  ],
  initialViewPoint: () => [],
  initialBreakdown: null,
});

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (e: "close"): void;
  (e: "saved", settings: { summaryTypes: Record<string, boolean>; detailType: string }): void;
}>();

const { t } = useTranslation();

// ===== Visible Model =====
const visibleModel = computed({
  get: () => props.visible,
  set: (v: boolean) => emit("update:visible", v),
});

// ===== Widget Setting Title =====
const widgetSettingTitle = computed(
  () =>
    `${props.parentMenuName ? t(props.parentMenuName) + " > " : ""}${props.menuName ? t(props.menuName) + " > " : ""}${t("text-menu-setting")}`
);

// ===== Tab =====
const itemSource = computed(() => [
  { id: "reExecutePlan" as const, text: props.menuName ? t(props.menuName) : t("text-re_plan_excute") },
]);

const settingPopupCurrentTab = ref<string>(props.initialTab);

watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) settingPopupCurrentTab.value = props.initialTab;
  }
);

// ===== State =====
const viewPointWidget = ref<string[]>(
  props.initialViewPoint.length
    ? [...props.initialViewPoint]
    : props.viewPointSource.map((item) => item.value)
);

const breakdownWidget = ref<{ label: string; value: string } | null>(
  props.initialBreakdown || (props.breakdownSource.length ? props.breakdownSource[0] : null)
);

// ===== Confirm =====
const onConfirmPopup = async () => {
  const summaryTypes: Record<string, boolean> = {};
  for (const vp of props.viewPointSource) {
    summaryTypes[vp.value] = viewPointWidget.value.includes(vp.value);
  }

  const detailType = breakdownWidget.value?.value || "OPER";

  const param = {
    widget_id: "reExecutePlanPopup",
    menu_id: "/lb/ReExecutePlan",
    user_id: props.userId,
    widget_value: JSON.stringify({
      summaryTypes,
      detailType,
    }),
  };

  try {
    await saveWidgetSettings(param);
  } catch (e) {
    console.error("Widget setting save error:", e);
  }

  emit("saved", { summaryTypes, detailType });
  return true;
};

// ===== Load =====
const onLoadPopup = async () => {
  // Load previously saved settings if needed
  if (!props.userId) return;
  try {
    const res = await fetchWidgetSettings(props.userId, "/lb/ReExecutePlan") as any;
    if (res?.success && res?.data) {
      const raw = res.data["reExecutePlanPopup"];
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.summaryTypes) {
          viewPointWidget.value = Object.keys(parsed.summaryTypes).filter(
            (key) => parsed.summaryTypes[key]
          );
        }
        if (parsed.detailType) {
          const found = props.breakdownSource.find((b) => b.value === parsed.detailType);
          if (found) {
            breakdownWidget.value = found;
          }
        }
      }
    }
  } catch {
    /* ignore */
  }
};
</script>

<style lang="scss">
.re-execute-plan-widget-setting-popup {
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
      min-width: 140px !important;
      .tab-label {
        text-overflow: clip !important;
      }
    }

    .currentTab {
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
        margin-bottom: 10px;

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
}
</style>
