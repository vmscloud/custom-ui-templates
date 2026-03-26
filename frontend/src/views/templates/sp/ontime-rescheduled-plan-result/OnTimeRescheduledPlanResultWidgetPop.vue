<template>
  <Popup
    class="rtf-widget-setting-popup"
    :title="t('text-popup-rtf_aggregate_type_setting')"
    :visible="true"
    preset="save"
    :width="600"
    :on-confirm="handleSave"
    :on-cancel="() => emit('close')"
  >
    <div class="widget-body">
      <div class="setting-section">
        <div class="setting-title">{{ t('text-popup-rtf_aggregate_type_setting') }}</div>
        <div class="setting-box">
          <div class="setting-desc">{{ t('desc-rtf_aggregate_type_setting') }}</div>
          <Radio
            :valueExpr="'value'"
            :display-expr="'label'"
            :items-source="[
              { value: 'LOT', label: 'LOT' },
              { value: 'DEMAND', label: 'DEMAND' },
            ]"
            v-model="rtfStd"
          />
        </div>
      </div>
      <div class="setting-section">
        <div class="setting-title">{{ t('text-popup-qty_uom_setting') }}</div>
        <div class="setting-box">
          <div class="setting-desc">{{ t('desc-qty_uom_setting') }}</div>
          <Select
            :key-prop="'value'"
            :display-prop="'label'"
            :items-source="uomOptions"
            v-model="uomType"
          />
        </div>
      </div>
    </div>
  </Popup>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useTranslation } from "i18next-vue";
import { Popup, Radio, Select } from "@vmscloud/moz-ui-components";
import { fetchWidgetSettings, saveWidgetSettings } from "./onTimeRescheduledPlanResult";

const { t } = useTranslation();

const props = defineProps<{
  userId: string;
}>();

const emit = defineEmits<{
  close: [];
  saved: [settings: { rtfStd: string; uomType: string }];
}>();

const uomOptions = [
  { value: "DEFAULT", label: "DEFAULT" },
  { value: "CONVERSION", label: "CONVERSION" },
];

const rtfStd = ref("LOT");
const uomType = ref("DEFAULT");

onMounted(async () => {
  if (!props.userId) return;
  try {
    const res = await fetchWidgetSettings(props.userId, "/pa/PlanDashboard");
    if (res.success && res.data) {
      const raw = res.data["rtfSummaryPopup"];
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.rtfStd) rtfStd.value = parsed.rtfStd;
        if (parsed.uomType) uomType.value = parsed.uomType;
      }
    }
  } catch { /* ignore */ }
});

async function handleSave() {
  try {
    const widgetValue = JSON.stringify({
      rtfStd: rtfStd.value,
      uomType: uomType.value,
    });
    await saveWidgetSettings({
      userId: props.userId,
      menuId: "/pa/PlanDashboard",
      widgetId: "rtfSummaryPopup",
      widgetValue,
    });
    emit("saved", { rtfStd: rtfStd.value, uomType: uomType.value });
    emit("close");
  } catch (e) {
    console.error("위젯 설정 저장 오류:", e);
  }
}
</script>

<style lang="scss">
.rtf-widget-setting-popup {
  .moz-popup-body {
    padding: 24px !important;
  }

  .widget-body {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .setting-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .setting-title {
    font-size: 14px;
    font-weight: 500;
  }

  .setting-box {
    border: 1px solid #bac6d4;
    background-color: #f8f8fd;
    border-radius: 6px;
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .setting-desc {
    font-size: 12px;
    color: #434c60;
  }
}
</style>
